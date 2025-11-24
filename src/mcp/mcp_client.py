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
        
        # Log initialization
        if self.config.is_mcp_enabled():
            enabled_services = self.config.get_enabled_services()
            logger.info(f"MCP Client initialized with {len(enabled_services)} enabled services")
            for service in enabled_services:
                logger.info(f"  - {service.name}: {', '.join(service.domains)}")
        else:
            logger.warning("MCP Client initialized but MCP is globally disabled")
    
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
        
        Note: This is a placeholder implementation that simulates REST calls.
        In production, this would use requests library to make actual HTTP calls.
        """
        try:
            # Build request payload
            payload = self._build_rest_payload(query, **kwargs)
            
            # Get auth headers
            headers = service.authentication.get_auth_header() or {}
            headers['Content-Type'] = 'application/json'
            
            # Simulate REST call (placeholder)
            # In production: response = requests.post(service.endpoint, json=payload, headers=headers, timeout=service.timeout)
            
            # For now, simulate a successful response
            logger.debug(f"[{request_id}] REST call to {service.endpoint} with payload: {payload}")
            
            # Simulate response based on service
            simulated_response = self._simulate_service_response(service, query)
            
            # Normalize response
            return self._normalize_response(simulated_response, service.name)
        
        except Exception as e:
            logger.error(f"[{request_id}] REST service error: {e}")
            raise
    
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
        payload = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
        }
        payload.update(kwargs)
        return payload
    
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
            metadata = {
                "timestamp": datetime.utcnow().isoformat(),
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
        return MCPResponse(
            content="",
            confidence=0.0,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
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
