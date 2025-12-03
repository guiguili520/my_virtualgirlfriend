#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP客户端
MCP Client

负责路由请求到不同服务，处理认证、重试和响应标准化
Responsible for routing requests to different services, handling auth, retries, and response normalization
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .mcp_config import MCPConfig, ServiceConfig, load_mcp_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MCPResponse:
    """
    MCP标准化响应
    MCP Normalized Response
    """
    content: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    service_name: str
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return asdict(self)


class MCPClient:
    """
    MCP客户端类
    MCP Client Class

    提供统一的接口来查询不同的外部服务
    Provides unified interface to query different external services
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化MCP客户端
        Initialize MCP client

        Args:
            config_path: 配置文件路径 / Path to config file
        """
        self.config = load_mcp_config(config_path)
        self._request_count = 0
        self._session_ids = {}  # 存储每个服务的session ID

        # Log initialization
        if self.config.is_mcp_enabled():
            enabled_services = self.config.get_enabled_services()
            logger.info(f"MCP Client initialized with {len(enabled_services)} enabled services")
            for service in enabled_services:
                logger.info(f"  - {service.name}: {', '.join(service.domains)}")

            # 为所有启用的服务进行MCP初始化
            self._initialize_mcp_services()
        else:
            logger.warning("MCP Client initialized but MCP is globally disabled")

    def _initialize_mcp_services(self):
        """
        为所有启用的MCP服务进行初始化握手
        Initialize MCP handshake for all enabled services
        """
        for service in self.config.get_enabled_services():
            try:
                session_id = self._perform_mcp_handshake(service)
                if session_id:
                    self._session_ids[service.name] = session_id
                    logger.info(f"MCP handshake successful for {service.name}, session_id: {session_id}")
                else:
                    logger.warning(f"MCP handshake failed for {service.name}")
            except Exception as e:
                logger.error(f"MCP handshake error for {service.name}: {e}")

    def _perform_mcp_handshake(self, service: ServiceConfig) -> Optional[str]:
        """
        执行MCP初始化握手
        Perform MCP initialization handshake

        Args:
            service: 服务配置

        Returns:
            session_id: 会话ID，如果握手失败返回None
        """
        try:
            import requests

            # MCP初始化请求
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "clientInfo": {
                        "name": "virtual-girlfriend",
                        "version": "1.0.0"
                    }
                }
            }

            headers = service.authentication.get_auth_header() or {}
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json, text/event-stream'

            logger.debug(f"Sending MCP handshake to {service.endpoint}")
            response = requests.post(
                service.endpoint,
                json=init_payload,
                headers=headers,
                timeout=service.timeout
            )

            # 从响应头中提取session ID（无论状态码是什么，因为406也会返回session ID）
            session_id = response.headers.get('Mcp-Session-Id')

            if session_id:
                logger.info(f"Got session ID from header: {session_id}")

                # 发送 initialized 通知（MCP协议要求）
                try:
                    notify_payload = {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized"
                    }
                    # 添加session ID到通知头
                    notify_headers = headers.copy()
                    notify_headers['Mcp-Session-Id'] = session_id

                    notify_response = requests.post(
                        service.endpoint,
                        json=notify_payload,
                        headers=notify_headers,
                        timeout=service.timeout
                    )
                    logger.debug(f"Sent initialized notification, status: {notify_response.status_code}")
                except Exception as e:
                    logger.warning(f"Failed to send initialized notification: {e}")

                return session_id

            # 如果状态码是200，尝试从响应体中提取
            if response.status_code == 200:
                try:
                    data = response.json()
                    session_id = data.get("result", {}).get("sessionId")
                    if session_id:
                        logger.info(f"Got session ID from response body: {session_id}")
                        return session_id
                except Exception:
                    pass

            # 如果都没有，记录错误
            logger.warning(f"MCP handshake failed with status {response.status_code}: {response.text[:200]}")
            return None

        except Exception as e:
            logger.error(f"MCP handshake exception: {e}")
            return None
    
    def fetch(self, domain: str, query: str, **kwargs) -> MCPResponse:
        """
        获取指定域的信息
        Fetch information for specified domain
        
        Args:
            domain: 查询域 / Query domain (e.g., 'weather', 'news')
            query: 查询内容 / Query content
            **kwargs: 额外参数 / Additional parameters
        
        Returns:
            MCPResponse: 标准化响应 / Normalized response
        """
        self._request_count += 1
        request_id = f"REQ-{self._request_count:06d}"
        
        # Log the request
        logger.info(f"[{request_id}] Fetch request - Domain: {domain}, Query: {query[:50]}...")
        
        # Check if MCP is globally enabled
        if not self.config.is_mcp_enabled():
            logger.warning(f"[{request_id}] MCP is globally disabled")
            return self._create_error_response(
                "MCP is globally disabled",
                domain,
                "system"
            )
        
        # Get services for domain
        services = self.config.get_services_for_domain(domain)
        
        if not services:
            logger.warning(f"[{request_id}] No services available for domain: {domain}")
            return self._create_error_response(
                f"No services available for domain: {domain}",
                domain,
                "system"
            )
        
        # Try each service in priority order
        last_error = None
        for service in services:
            logger.info(f"[{request_id}] Trying service: {service.name}")
            
            try:
                response = self._query_service(service, query, request_id, **kwargs)
                if response.success:
                    logger.info(f"[{request_id}] Successfully fetched from {service.name}")
                    return response
                else:
                    last_error = response.error
                    logger.warning(f"[{request_id}] Service {service.name} failed: {response.error}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"[{request_id}] Exception querying {service.name}: {e}")
        
        # All services failed
        error_msg = f"All services failed. Last error: {last_error}"
        logger.error(f"[{request_id}] {error_msg}")
        return self._create_error_response(error_msg, domain, services[-1].name if services else "unknown")
    
    def _query_service(
        self,
        service: ServiceConfig,
        query: str,
        request_id: str,
        **kwargs
    ) -> MCPResponse:
        """
        查询单个服务（带重试）
        Query a single service (with retry)
        
        Args:
            service: 服务配置 / Service configuration
            query: 查询内容 / Query content
            request_id: 请求ID / Request ID
            **kwargs: 额外参数 / Additional parameters
        
        Returns:
            MCPResponse: 服务响应 / Service response
        """
        retries = service.retries
        last_error = None
        
        for attempt in range(retries + 1):
            if attempt > 0:
                # Exponential backoff
                wait_time = min(2 ** attempt, 10)
                logger.info(f"[{request_id}] Retry {attempt}/{retries} after {wait_time}s...")
                time.sleep(wait_time)
            
            try:
                if service.protocol == "rest":
                    return self._query_rest_service(service, query, request_id, **kwargs)
                elif service.protocol == "grpc":
                    return self._query_grpc_service(service, query, request_id, **kwargs)
                else:
                    return self._create_error_response(
                        f"Unsupported protocol: {service.protocol}",
                        service.name,
                        service.name
                    )
            
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[{request_id}] Attempt {attempt + 1} failed: {e}")
        
        # All retries exhausted
        return self._create_error_response(
            f"Service unavailable after {retries} retries: {last_error}",
            service.name,
            service.name
        )
    
    def _query_rest_service(
        self,
        service: ServiceConfig,
        query: str,
        request_id: str,
        **kwargs
    ) -> MCPResponse:
        """
        查询REST服务
        Query REST service

        如果 endpoint 包含 example.com，则使用模拟响应；否则执行真实HTTP请求。
        """
        try:
            import requests
            import json as json_module

            # 当使用示例域名时，走模拟路径，确保测试与演示稳定
            if 'example.com' in service.endpoint:
                logger.debug(f"[{request_id}] REST simulated call to {service.endpoint}")
                simulated_response = self._simulate_service_response(service, query)
                return self._normalize_response(simulated_response, service.name)

            # 检查是否有有效的session ID，如果没有则重新初始化
            session_id = self._session_ids.get(service.name)
            if not session_id:
                logger.info(f"[{request_id}] No session ID for {service.name}, performing handshake...")
                session_id = self._perform_mcp_handshake(service)
                if session_id:
                    self._session_ids[service.name] = session_id
                else:
                    logger.warning(f"[{request_id}] Failed to get session ID for {service.name}")

            # Build request payload
            kwargs['service_endpoint'] = service.endpoint
            payload = self._build_rest_payload(query, **kwargs)

            # Get auth headers
            headers = service.authentication.get_auth_header() or {}
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json, text/event-stream'

            # 添加MCP session ID（如果可用）
            if session_id:
                headers['Mcp-Session-Id'] = session_id

            # 真实HTTP请求
            logger.info(f"[{request_id}] MCP REST call to {service.endpoint}")
            logger.debug(f"[{request_id}] Payload: {payload}")
            resp = requests.post(
                service.endpoint,
                json=payload,
                headers=headers,
                timeout=service.timeout
            )

            # 检查HTTP状态码
            if resp.status_code >= 400:
                error_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                logger.error(f"[{request_id}] Request failed: {error_msg}")
                raise Exception(error_msg)

            # 优先解析JSON
            try:
                raw = resp.json()
                logger.debug(f"[{request_id}] Raw response: {raw}")

                # 处理JSON-RPC响应格式
                if 'jsonrpc' in raw:
                    # JSON-RPC error
                    if 'error' in raw:
                        error_msg = raw.get('error', {}).get('message', 'Unknown error')
                        logger.error(f"[{request_id}] JSON-RPC error: {error_msg}")
                        raise Exception(f"JSON-RPC error: {error_msg}")

                    # JSON-RPC success result
                    if 'result' in raw:
                        result = raw['result']
                        # MCP tools/call 返回格式
                        if isinstance(result, dict) and 'content' in result:
                            content_items = result['content']
                            if isinstance(content_items, list) and len(content_items) > 0:
                                # 提取文本内容
                                text_parts = []
                                for item in content_items:
                                    if item.get('type') == 'text':
                                        text = item.get('text', '')
                                        # 尝试解析JSON字符串格式的天气数据
                                        try:
                                            weather_data = json_module.loads(text)
                                            if isinstance(weather_data, dict):
                                                # 格式化天气信息为可读文本
                                                formatted = self._format_weather_data(weather_data)
                                                text_parts.append(formatted)
                                            else:
                                                text_parts.append(text)
                                        except (json_module.JSONDecodeError, TypeError):
                                            text_parts.append(text)

                                text_content = ' '.join(text_parts)
                                logger.info(f"[{request_id}] MCP response content: {text_content[:100]}...")
                                raw = {
                                    'content': text_content,
                                    'confidence': 0.95,
                                    'data': result
                                }
                            else:
                                raw = {
                                    'content': str(result.get('content', result)),
                                    'confidence': 0.8,
                                    'data': result
                                }
                        else:
                            raw = {
                                'content': str(result),
                                'confidence': 0.8,
                                'data': {'result': result}
                            }

                # 若返回不包含标准字段，做轻度包装
                elif not isinstance(raw, dict) or 'content' not in raw:
                    raw = {
                        'content': str(raw),
                        'confidence': 0.8,
                        'data': {'status_code': resp.status_code}
                    }
            except ValueError as e:
                # 非JSON响应，作为文本包装
                raw = {
                    'content': resp.text,
                    'confidence': 0.7,
                    'data': {'status_code': resp.status_code}
                }

            return self._normalize_response(raw, service.name)

        except Exception as e:
            logger.error(f"[{request_id}] REST service error: {e}")
            raise

    def _format_weather_data(self, weather_data: Dict[str, Any]) -> str:
        """
        格式化天气数据为可读文本
        Format weather data into readable text
        """
        city = weather_data.get('city', '未知城市')
        description = weather_data.get('description', '未知')
        temperature = weather_data.get('temperature', '未知')
        humidity = weather_data.get('humidity', '未知')
        wind_speed = weather_data.get('wind_speed', '未知')

        # 构建自然语言描述
        parts = [f"{city}天气：{description}"]

        if temperature != '未知':
            parts.append(f"温度{temperature}°C")
        if humidity != '未知':
            parts.append(f"湿度{humidity}%")
        if wind_speed != '未知':
            parts.append(f"风速{wind_speed}m/s")

        return "，".join(parts)
    
    def _query_grpc_service(
        self,
        service: ServiceConfig,
        query: str,
        request_id: str,
        **kwargs
    ) -> MCPResponse:
        """
        查询gRPC服务
        Query gRPC service
        
        Note: This is a placeholder implementation.
        In production, this would use grpcio to make actual gRPC calls.
        """
        try:
            # Build gRPC request
            logger.debug(f"[{request_id}] gRPC call to {service.endpoint} with query: {query}")
            
            # Simulate gRPC call (placeholder)
            # In production: Use grpcio to make the actual call
            
            simulated_response = self._simulate_service_response(service, query)
            return self._normalize_response(simulated_response, service.name)
        
        except Exception as e:
            logger.error(f"[{request_id}] gRPC service error: {e}")
            raise
    
    def _build_rest_payload(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        构建REST请求负载
        Build REST request payload
        """
        # 对于MCP服务，使用JSON-RPC 2.0格式
        if 'mcp.api-inference.modelscope.net' in kwargs.get('service_endpoint', ''):
            # 提取城市名称
            city = self._extract_city_name(query)
            logger.info(f"Extracted city name: '{city}' from query: '{query}'")

            return {
                "jsonrpc": "2.0",
                "id": self._request_count,
                "method": "tools/call",
                "params": {
                    "name": "get_weather",
                    "arguments": {
                        "city": city,
                        "units": "metric",
                        "lang": "zh_cn"
                    }
                }
            }

        # 默认格式
        from datetime import datetime, timezone
        payload = {
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(kwargs)
        return payload

    def _extract_city_name(self, query: str) -> str:
        """
        从查询中提取城市名称
        Extract city name from query
        """
        import re

        # 常见中国城市列表（用于精确匹配）
        common_cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都",
            "重庆", "武汉", "西安", "天津", "青岛", "大连", "厦门", "宁波",
            "长沙", "郑州", "济南", "合肥", "福州", "昆明", "南昌", "长春",
            "哈尔滨", "石家庄", "太原", "沈阳", "南宁", "贵阳", "兰州", "西宁",
            "银川", "乌鲁木齐", "拉萨", "呼和浩特", "海口", "三亚", "珠海",
            "东莞", "佛山", "无锡", "常州", "温州", "烟台", "徐州", "扬州"
        ]

        # 首先尝试直接匹配已知城市
        for city in common_cities:
            if city in query:
                return city

        # 清理查询字符串
        text = query.strip()
        text = text.replace("?", "").replace("？", "").strip()

        # 移除常见的修饰词和时间词
        remove_words = [
            "怎么样", "如何", "怎样", "怎么", "吗", "呢", "啊", "呀",
            "今天", "明天", "后天", "昨天", "现在", "这会儿",
            "冷不冷", "热不热", "会下雨", "会下雪", "下不下雨",
            "的天气", "天气", "气温", "温度", "预报",
            "查一下", "告诉我", "帮我查", "请问", "想知道"
        ]

        for word in remove_words:
            text = text.replace(word, " ")

        # 清理多余空格
        text = ' '.join(text.split()).strip()

        # 尝试匹配常见的天气查询模式
        patterns = [
            r'^(.+?)的',       # "北京的天气怎么样" -> "北京"
            r'^(.{2,4})(?:市|省|区|县)?$',  # 2-4字的城市名
        ]

        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                city = match.group(1).strip()
                if city and 2 <= len(city) <= 10:
                    return city

        # 如果提取的文本是合理的城市名长度
        if text and 2 <= len(text) <= 10:
            return text

        # 默认城市
        logger.warning(f"Could not extract city from query: '{query}', using default '北京'")
        return "北京"
    
    def _simulate_service_response(self, service: ServiceConfig, query: str) -> Dict[str, Any]:
        """
        模拟服务响应（用于测试和开发）
        Simulate service response (for testing and development)
        
        Note: This is a placeholder. In production, remove this and use actual service responses.
        """
        # Simulate different responses based on service
        if "weather" in service.domains:
            return {
                "content": f"Weather information for query: {query}",
                "confidence": 0.85,
                "data": {
                    "temperature": 22,
                    "condition": "sunny",
                    "humidity": 65
                }
            }
        elif "news" in service.domains:
            return {
                "content": f"Latest news about: {query}",
                "confidence": 0.75,
                "data": {
                    "articles": [
                        {"title": "News Article 1", "source": "Example News"}
                    ]
                }
            }
        elif "facts" in service.domains or "general" in service.domains:
            return {
                "content": f"Knowledge about: {query}",
                "confidence": 0.90,
                "data": {
                    "facts": ["Fact 1", "Fact 2"]
                }
            }
        else:
            return {
                "content": f"Information about: {query}",
                "confidence": 0.70,
                "data": {}
            }
    
    def _normalize_response(self, raw_response: Dict[str, Any], service_name: str) -> MCPResponse:
        """
        标准化服务响应
        Normalize service response
        
        Args:
            raw_response: 原始响应 / Raw response
            service_name: 服务名称 / Service name
        
        Returns:
            MCPResponse: 标准化响应 / Normalized response
        """
        try:
            content = raw_response.get("content", "")
            confidence = float(raw_response.get("confidence", 0.5))
            
            # Extract metadata
            from datetime import datetime, timezone
            metadata = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": service_name,
            }
            
            # Include additional data if present
            if "data" in raw_response:
                metadata["data"] = raw_response["data"]
            
            # Include any other fields
            for key, value in raw_response.items():
                if key not in ["content", "confidence", "data"]:
                    metadata[key] = value
            
            return MCPResponse(
                content=content,
                confidence=min(max(confidence, 0.0), 1.0),  # Clamp to [0, 1]
                metadata=metadata,
                service_name=service_name,
                success=True
            )
        
        except Exception as e:
            logger.error(f"Error normalizing response: {e}")
            return self._create_error_response(
                f"Failed to normalize response: {e}",
                service_name,
                service_name
            )
    
    def _create_error_response(self, error_msg: str, domain: str, service_name: str) -> MCPResponse:
        """
        创建错误响应
        Create error response
        """
        from datetime import datetime, timezone
        return MCPResponse(
            content="",
            confidence=0.0,
            metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "domain": domain,
            },
            service_name=service_name,
            success=False,
            error=error_msg
        )
    
    def get_available_domains(self) -> List[str]:
        """
        获取所有可用的域
        Get all available domains
        
        Returns:
            List[str]: 域列表 / List of domains
        """
        if not self.config.is_mcp_enabled():
            return []
        
        domains = set()
        for service in self.config.get_enabled_services():
            domains.update(service.domains)
        
        return sorted(list(domains))
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取所有服务的状态
        Get status of all services
        
        Returns:
            Dict: 服务状态信息 / Service status information
        """
        status = {
            "mcp_enabled": self.config.is_mcp_enabled(),
            "total_services": len(self.config.services),
            "enabled_services": len(self.config.get_enabled_services()),
            "available_domains": self.get_available_domains(),
            "services": []
        }
        
        for service in self.config.services:
            service_info = {
                "name": service.name,
                "enabled": service.enabled,
                "protocol": service.protocol,
                "domains": service.domains,
                "priority": service.priority
            }
            status["services"].append(service_info)
        
        return status
    
    def reload_config(self, config_path: Optional[str] = None):
        """
        重新加载配置
        Reload configuration
        
        Args:
            config_path: 配置文件路径 / Path to config file
        """
        logger.info("Reloading MCP configuration...")
        self.config = load_mcp_config(config_path)
        logger.info(f"Configuration reloaded. MCP enabled: {self.config.is_mcp_enabled()}")
