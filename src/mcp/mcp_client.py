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
        if 'example.com' in service.endpoint:
            logger.debug(f"Skipping MCP handshake for simulated service {service.name}")
            return f"simulated-{service.name}"

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
            kwargs['service_name'] = service.name
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
        格式化天气数据为完整可读文本
        Format weather data into complete readable text
        """
        city = weather_data.get('city', '未知城市')
        description = weather_data.get('description', weather_data.get('weather', '未知'))
        temperature = weather_data.get('temperature', weather_data.get('temp', '未知'))
        humidity = weather_data.get('humidity', '未知')
        wind_speed = weather_data.get('wind_speed', weather_data.get('windSpeed', '未知'))
        wind_direction = weather_data.get('wind_direction', weather_data.get('windDir', ''))

        # 构建自然语言描述
        parts = [f"{city}当前天气：{description}"]

        if temperature != '未知':
            parts.append(f"气温{temperature}°C")
        if humidity != '未知':
            parts.append(f"相对湿度{humidity}%")
        if wind_speed != '未知':
            if wind_direction:
                parts.append(f"{wind_direction}风 {wind_speed}m/s")
            else:
                parts.append(f"风速{wind_speed}m/s")

        # 添加体感温度（如有）
        if 'feels_like' in weather_data:
            parts.append(f"体感温度{weather_data['feels_like']}°C")

        # 添加降水概率（如有）
        if 'precipitation' in weather_data:
            parts.append(f"降水概率{weather_data['precipitation']}%")

        return "，".join(parts) + "。"
    
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
        # 获取服务名称以判断使用哪个payload builder
        service_name = kwargs.get('service_name', '')
        service_endpoint = kwargs.get('service_endpoint', '')

        # 对于MCP服务，使用JSON-RPC 2.0格式
        if 'mcp.api-inference.modelscope.net' in service_endpoint:
            # 根据服务名称判断使用哪个payload builder
            if 'fetch' in service_name.lower():
                return self._build_fetch_payload(query, **kwargs)
            elif 'amap' in service_name.lower() or 'map' in service_name.lower():
                return self._build_amap_payload(query, **kwargs)
            elif 'weather' in service_name.lower() or 'weather' in str(kwargs.get('domains', [])):
                # 天气服务payload
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
            else:
                # 默认：通用MCP工具调用格式
                logger.info(f"Using generic MCP tool call for service: {service_name}")
                return {
                    "jsonrpc": "2.0",
                    "id": self._request_count,
                    "method": "tools/call",
                    "params": {
                        "name": "query",
                        "arguments": {
                            "query": query
                        }
                    }
                }

        # 默认格式（非MCP服务）
        from datetime import datetime, timezone
        payload = {
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(kwargs)
        return payload

    def _build_fetch_payload(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        构建 Fetch MCP 服务请求负载
        Build Fetch MCP service request payload
        """
        # 从 query 或 kwargs 中提取 URL
        url = kwargs.get('url', None)

        if not url:
            # 从查询中提取 URL
            url = self._extract_url_from_query(query)
            if not url:
                logger.warning(f"Could not extract URL from query: {query}, using query as URL")
                url = query

        max_length = kwargs.get('max_length', 5000)
        start_index = kwargs.get('start_index', 0)
        raw = kwargs.get('raw', False)

        logger.info(f"Building fetch payload - URL: {url[:50]}...")

        return {
            "jsonrpc": "2.0",
            "id": self._request_count,
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {
                    "url": url,
                    "max_length": max_length,
                    "start_index": start_index,
                    "raw": raw
                }
            }
        }

    def _extract_url_from_query(self, query: str) -> str:
        """
        从查询中提取 URL
        Extract URL from query using regex
        """
        import re

        # 匹配 http:// 或 https:// 开头的 URL
        url_pattern = r'https?://[^\s\u3000\uff0c\u3001\uff1f\uff1a\u3002]*'
        match = re.search(url_pattern, query)

        if match:
            url = match.group(0)
            # 移除尾部的标点符号
            url = re.sub(r'[,\.\)!?:;\'\"]+$', '', url)
            logger.info(f"Extracted URL from query: {url}")
            return url

        logger.warning(f"No URL found in query: {query}")
        return None

    def _build_amap_payload(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        构建高德地图 MCP 服务请求负载
        Build Amap MCP service request payload

        注意：高德地图 MCP 目前无法工作
        ISSUE: Amap MCP tools are currently unavailable:
        - 尝试的工具名: maps_search_poi, maps_direction, maps_geocode 等都返回 "Unknown tool"
        - 测试其他可能的工具名都返回 "Invalid request parameters"
        - 可能需要查看高德地图 MCP 的官方文档或与服务提供商沟通
        """
        logger.warning("⚠️  高德地图 MCP 服务调用 - 工具不可用")

        # 作为占位符，返回一个简单的 search 请求，但预期会失败
        location = self._extract_city_name(query)

        return {
            "jsonrpc": "2.0",
            "id": self._request_count,
            "method": "tools/call",
            "params": {
                "name": "search",
                "arguments": {
                    "query": location,
                }
            }
        }

    def _detect_map_intent(self, query: str) -> str:
        """
        检测地图查询的意图
        Detect the intent of map query
        """
        q = query.lower()

        # 路线/导航意图
        direction_keywords = ["路线", "怎么走", "怎么去", "导航", "从", "到"]
        if any(k in q for k in direction_keywords):
            return "directions"

        # POI 搜索意图
        poi_keywords = ["附近", "周边", "找", "查找", "有没有", "哪里", "什么", "吃", "喝", "玩", "住"]
        if any(k in q for k in poi_keywords):
            return "search_poi"

        # 默认为地址查询
        return "geocode"

    def _extract_poi_keywords(self, query: str) -> str:
        """
        从查询中提取 POI 搜索关键词
        Extract POI keywords from query
        """
        import re

        # 移除修饰词
        text = query.replace("附近", " ").replace("周边", " ").replace("有没有", " ").replace("找", " ")
        text = text.replace("什么", " ").replace("哪里", " ").replace("怎么样", " ")

        # 提取可能的关键词
        keywords = [
            "餐厅", "饭店", "酒店", "宾馆", "便利店", "超市", "医院", "银行",
            "地铁", "公交", "停车场", "加油站", "电影院", "公园", "学校"
        ]

        for keyword in keywords:
            if keyword in query:
                return keyword

        # 尝试提取其他词汇
        if "吃" in query or "饭" in query:
            return "餐厅"
        elif "住" in query:
            return "宾馆"
        elif "玩" in query:
            return "景区"
        else:
            # 如果没有匹配，尝试提取最后一个有意义的词
            words = query.split()
            if words:
                return words[-1]
            return "地点"

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
