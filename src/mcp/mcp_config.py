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

    只从 mcp.json 读取配置
    Only reads configuration from mcp.json
    """
    project_root = Path(__file__).parent.parent.parent

    if config_path is None:
        # 只从 mcp.json 读取
        config_file = project_root / "mcp.json"
    else:
        config_file = Path(config_path)

    if not config_file.exists():
        print(f"Warning: MCP config file not found at {config_file}")
        return MCPConfig(enabled=False, services=[])

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        if not data:
            print(f"Warning: Empty config file {config_file}")
            return MCPConfig(enabled=False, services=[])

        # 支持两种格式：
        # 1. mcp.services 格式（详细配置）
        # 2. mcpServers 格式（简洁配置）

        if 'mcp' in data:
            # 详细配置格式
            return _parse_detailed_config(data['mcp'], config_file)
        elif 'mcpServers' in data:
            # 简洁配置格式
            return _parse_simple_config(data['mcpServers'], config_file)
        else:
            print(f"Warning: No 'mcp' or 'mcpServers' section found in {config_file}")
            return MCPConfig(enabled=False, services=[])

    except Exception as e:
        import traceback
        print(f"Warning: Failed to load MCP config from {config_file}: {e}")
        traceback.print_exc()
        return MCPConfig(enabled=False, services=[])


def _parse_detailed_config(mcp_data: Dict, config_file: Path) -> MCPConfig:
    """解析详细配置格式（mcp.services）"""
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


def _parse_simple_config(servers_data: Dict, config_file: Path) -> MCPConfig:
    """
    解析简洁配置格式（mcpServers）

    简洁格式示例：
    {
      "mcpServers": {
        "weather": {
          "type": "streamable_http",
          "url": "https://..."
        }
      }
    }
    """
    services = []
    priority = 1

    for name, server_data in servers_data.items():
        # 从简洁格式推断domains（基于服务名称）
        domains = _infer_domains_from_name(name)

        service = ServiceConfig(
            name=name,
            enabled=True,
            endpoint=server_data.get('url', server_data.get('endpoint', '')),
            protocol='rest',  # streamable_http 等同于 rest
            authentication=AuthConfig(type='none'),
            domains=domains,
            timeout=5,
            retries=3,
            priority=priority
        )
        services.append(service)
        priority += 1

    print(f"✓ Loaded MCP config (simple format) from {config_file} with {len(services)} services")

    return MCPConfig(
        enabled=True,
        default_timeout=5,
        default_retries=3,
        services=services
    )


def _infer_domains_from_name(name: str) -> List[str]:
    """根据服务名称推断处理的域"""
    name_lower = name.lower()

    # 预定义的域映射
    domain_mappings = {
        'weather': ['weather', 'forecast', 'temperature', 'climate', '天气', '温度'],
        'map': ['maps', 'location', 'navigation', 'poi', '地图', '导航'],
        'amap': ['maps', 'location', 'navigation', 'poi', '地图', '导航', '高德'],
        'news': ['news', 'headlines', 'current_events', '新闻'],
        'search': ['search', 'query', '搜索'],
        'translate': ['translation', 'language', '翻译'],
    }

    # 尝试匹配
    for key, domains in domain_mappings.items():
        if key in name_lower:
            return domains

    # 默认使用服务名称作为域
    return [name_lower]


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
