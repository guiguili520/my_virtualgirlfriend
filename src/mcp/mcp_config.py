#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP配置解析器
MCP Configuration Parser

负责读取和解析mcp.json中的MCP服务配置
Responsible for reading and parsing MCP service configuration from mcp.json
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class AuthConfig:
    """认证配置 / Authentication Configuration"""
    type: str = "none"  # api_key, bearer, basic, none
    key: Optional[str] = None
    header: str = "Authorization"
    
    def get_auth_header(self) -> Optional[Dict[str, str]]:
        """获取认证头 / Get authentication header"""
        if self.type == "none" or not self.key:
            return None
        
        # Try to get from environment variable if key looks like an env var
        key_value = self.key
        if self.key.isupper() and "_" in self.key:
            key_value = os.getenv(self.key, self.key)
        
        if self.type == "api_key":
            return {self.header: key_value}
        elif self.type == "bearer":
            return {self.header: f"Bearer {key_value}"}
        elif self.type == "basic":
            return {self.header: f"Basic {key_value}"}
        
        return None


@dataclass
class ServiceConfig:
    """服务配置 / Service Configuration"""
    name: str
    enabled: bool
    endpoint: str
    protocol: str  # rest or grpc
    authentication: AuthConfig
    domains: List[str]
    timeout: int = 5
    retries: int = 3
    priority: int = 999  # Lower is higher priority
    
    def handles_domain(self, domain: str) -> bool:
        """检查服务是否处理指定域 / Check if service handles the specified domain"""
        return domain.lower() in [d.lower() for d in self.domains]
    
    def is_available(self) -> bool:
        """检查服务是否可用 / Check if service is available"""
        return self.enabled


@dataclass
class MCPConfig:
    """MCP全局配置 / MCP Global Configuration"""
    enabled: bool = True
    default_timeout: int = 5
    default_retries: int = 3
    services: List[ServiceConfig] = field(default_factory=list)
    
    def get_service_by_name(self, name: str) -> Optional[ServiceConfig]:
        """根据名称获取服务 / Get service by name"""
        for service in self.services:
            if service.name == name:
                return service
        return None
    
    def get_services_for_domain(self, domain: str) -> List[ServiceConfig]:
        """获取处理指定域的所有可用服务 / Get all available services for domain"""
        if not self.enabled:
            return []
        
        services = [
            service for service in self.services
            if service.is_available() and service.handles_domain(domain)
        ]
        
        # Sort by priority (lower number = higher priority)
        services.sort(key=lambda s: s.priority)
        return services
    
    def get_enabled_services(self) -> List[ServiceConfig]:
        """获取所有启用的服务 / Get all enabled services"""
        if not self.enabled:
            return []
        return [service for service in self.services if service.is_available()]
    
    def is_mcp_enabled(self) -> bool:
        """检查MCP是否全局启用 / Check if MCP is globally enabled"""
        return self.enabled


def load_mcp_config(config_path: Optional[str] = None) -> MCPConfig:
    """
    加载MCP配置文件
    Load MCP configuration file (supports both JSON and YAML)

    Args:
        config_path: 配置文件路径，默认为项目根目录下的enhance_config.yaml或mcp.json
                    Path to config file, defaults to enhance_config.yaml or mcp.json in project root

    Returns:
        MCPConfig: 解析后的配置对象 / Parsed configuration object
    """
    project_root = Path(__file__).parent.parent.parent

    if config_path is None:
        # Try to find config file: enhance_config.yaml first, then mcp.json
        config_file = project_root / "enhance_config.yaml"
        if not config_file.exists():
            config_file = project_root / "mcp.json"
    else:
        config_file = Path(config_path)

    if not config_file.exists():
        # Return default config if file doesn't exist
        print(f"Warning: MCP config file not found at {config_file}")
        return MCPConfig(enabled=False, services=[])

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            # Load YAML or JSON based on file extension
            if config_file.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        if not data or 'mcp' not in data:
            print(f"Warning: No 'mcp' section found in config file {config_file}")
            return MCPConfig(enabled=False, services=[])

        mcp_data = data['mcp']

        # Parse services
        services = []
        for service_data in mcp_data.get('services', []):
            auth_data = service_data.get('authentication', {})
            auth_config = AuthConfig(
                type=auth_data.get('type', 'none'),
                key=auth_data.get('key'),
                header=auth_data.get('header', 'Authorization')
            )

            service = ServiceConfig(
                name=service_data['name'],
                enabled=service_data.get('enabled', True),
                endpoint=service_data['endpoint'],
                protocol=service_data.get('protocol', 'rest'),
                authentication=auth_config,
                domains=service_data.get('domains', []),
                timeout=service_data.get('timeout', mcp_data.get('default_timeout', 5)),
                retries=service_data.get('retries', mcp_data.get('default_retries', 3)),
                priority=service_data.get('priority', 999)
            )
            services.append(service)

        print(f"✓ Loaded MCP config from {config_file} with {len(services)} services")

        return MCPConfig(
            enabled=mcp_data.get('enabled', True),
            default_timeout=mcp_data.get('default_timeout', 5),
            default_retries=mcp_data.get('default_retries', 3),
            services=services
        )

    except Exception as e:
        # Return default config on error
        import traceback
        print(f"Warning: Failed to load MCP config from {config_file}: {e}")
        traceback.print_exc()
        return MCPConfig(enabled=False, services=[])


def validate_config(config: MCPConfig) -> List[str]:
    """
    验证配置的完整性
    Validate configuration completeness
    
    Args:
        config: MCP配置对象 / MCP configuration object
    
    Returns:
        List[str]: 验证错误列表，空列表表示通过 / List of validation errors, empty if valid
    """
    errors = []
    
    if not config.services:
        errors.append("No services configured")
    
    service_names = set()
    for service in config.services:
        # Check for duplicate names
        if service.name in service_names:
            errors.append(f"Duplicate service name: {service.name}")
        service_names.add(service.name)
        
        # Check required fields
        if not service.endpoint:
            errors.append(f"Service {service.name} missing endpoint")
        
        if not service.domains:
            errors.append(f"Service {service.name} has no domains")
        
        if service.protocol not in ['rest', 'grpc']:
            errors.append(f"Service {service.name} has invalid protocol: {service.protocol}")
        
        if service.authentication.type not in ['none', 'api_key', 'bearer', 'basic']:
            errors.append(f"Service {service.name} has invalid auth type: {service.authentication.type}")
    
    return errors
