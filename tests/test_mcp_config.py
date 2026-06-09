#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP配置解析器
Test MCP Configuration Parser
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import tempfile
import yaml
from mcp import (
    AuthConfig,
    ServiceConfig,
    MCPConfig,
    load_mcp_config,
    validate_config
)


def test_auth_config_none():
    """测试无认证配置 / Test no authentication"""
    auth = AuthConfig(type="none")
    assert auth.get_auth_header() is None
    print("✓ No auth config works correctly")


def test_auth_config_api_key():
    """测试API密钥认证 / Test API key authentication"""
    auth = AuthConfig(type="api_key", key="test-key-123", header="X-API-Key")
    header = auth.get_auth_header()
    assert header == {"X-API-Key": "test-key-123"}
    print("✓ API key auth config works correctly")


def test_auth_config_bearer():
    """测试Bearer令牌认证 / Test Bearer token authentication"""
    auth = AuthConfig(type="bearer", key="token-456", header="Authorization")
    header = auth.get_auth_header()
    assert header == {"Authorization": "Bearer token-456"}
    print("✓ Bearer auth config works correctly")


def test_auth_config_basic():
    """测试Basic认证 / Test Basic authentication"""
    auth = AuthConfig(type="basic", key="basic-789", header="Authorization")
    header = auth.get_auth_header()
    assert header == {"Authorization": "Basic basic-789"}
    print("✓ Basic auth config works correctly")


def test_service_config_handles_domain():
    """测试服务域处理 / Test service domain handling"""
    auth = AuthConfig(type="none")
    service = ServiceConfig(
        name="test_service",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=["weather", "forecast", "temperature"]
    )
    
    assert service.handles_domain("weather")
    assert service.handles_domain("WEATHER")  # Case insensitive
    assert service.handles_domain("forecast")
    assert not service.handles_domain("news")
    print("✓ Service domain handling works correctly")


def test_service_config_availability():
    """测试服务可用性 / Test service availability"""
    auth = AuthConfig(type="none")
    
    enabled_service = ServiceConfig(
        name="enabled",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    disabled_service = ServiceConfig(
        name="disabled",
        enabled=False,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    assert enabled_service.is_available()
    assert not disabled_service.is_available()
    print("✓ Service availability check works correctly")


def test_mcp_config_get_service_by_name():
    """测试按名称获取服务 / Test get service by name"""
    auth = AuthConfig(type="none")
    service1 = ServiceConfig(
        name="service1",
        enabled=True,
        endpoint="https://api1.example.com",
        protocol="rest",
        authentication=auth,
        domains=["domain1"]
    )
    service2 = ServiceConfig(
        name="service2",
        enabled=True,
        endpoint="https://api2.example.com",
        protocol="rest",
        authentication=auth,
        domains=["domain2"]
    )
    
    config = MCPConfig(enabled=True, services=[service1, service2])
    
    assert config.get_service_by_name("service1") == service1
    assert config.get_service_by_name("service2") == service2
    assert config.get_service_by_name("nonexistent") is None
    print("✓ Get service by name works correctly")


def test_mcp_config_get_services_for_domain():
    """测试获取域的服务 / Test get services for domain"""
    auth = AuthConfig(type="none")
    service1 = ServiceConfig(
        name="weather1",
        enabled=True,
        endpoint="https://weather1.example.com",
        protocol="rest",
        authentication=auth,
        domains=["weather"],
        priority=2
    )
    service2 = ServiceConfig(
        name="weather2",
        enabled=True,
        endpoint="https://weather2.example.com",
        protocol="rest",
        authentication=auth,
        domains=["weather"],
        priority=1
    )
    service3 = ServiceConfig(
        name="news",
        enabled=True,
        endpoint="https://news.example.com",
        protocol="rest",
        authentication=auth,
        domains=["news"]
    )
    
    config = MCPConfig(enabled=True, services=[service1, service2, service3])
    
    weather_services = config.get_services_for_domain("weather")
    assert len(weather_services) == 2
    # Should be sorted by priority (lower first)
    assert weather_services[0].name == "weather2"
    assert weather_services[1].name == "weather1"
    
    news_services = config.get_services_for_domain("news")
    assert len(news_services) == 1
    assert news_services[0].name == "news"
    
    print("✓ Get services for domain works correctly (with priority sorting)")


def test_mcp_config_disabled_globally():
    """测试全局禁用MCP / Test globally disabled MCP"""
    auth = AuthConfig(type="none")
    service = ServiceConfig(
        name="service1",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    config = MCPConfig(enabled=False, services=[service])
    
    assert not config.is_mcp_enabled()
    assert len(config.get_services_for_domain("test")) == 0
    assert len(config.get_enabled_services()) == 0
    print("✓ Global MCP disable works correctly")


def test_load_mcp_config_from_yaml():
    """测试从YAML文件加载配置 / Test loading config from YAML file"""
    # Create temporary YAML file
    yaml_content = {
        'mcp': {
            'enabled': True,
            'default_timeout': 10,
            'default_retries': 5,
            'services': [
                {
                    'name': 'test_service',
                    'enabled': True,
                    'endpoint': 'https://test.example.com',
                    'protocol': 'rest',
                    'authentication': {
                        'type': 'api_key',
                        'key': 'TEST_KEY',
                        'header': 'X-Test-Key'
                    },
                    'domains': ['test', 'demo'],
                    'timeout': 15,
                    'retries': 2,
                    'priority': 1
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_content, f)
        temp_path = f.name
    
    try:
        config = load_mcp_config(temp_path)
        
        assert config.enabled is True
        assert config.default_timeout == 10
        assert config.default_retries == 5
        assert len(config.services) == 1
        
        service = config.services[0]
        assert service.name == 'test_service'
        assert service.enabled is True
        assert service.endpoint == 'https://test.example.com'
        assert service.protocol == 'rest'
        assert service.domains == ['test', 'demo']
        assert service.timeout == 15
        assert service.retries == 2
        assert service.priority == 1
        
        assert service.authentication.type == 'api_key'
        assert service.authentication.key == 'TEST_KEY'
        assert service.authentication.header == 'X-Test-Key'
        
        print("✓ Load MCP config from YAML works correctly")
    
    finally:
        Path(temp_path).unlink()


def test_load_mcp_config_nonexistent_file():
    """测试加载不存在的配置文件 / Test loading nonexistent config file"""
    config = load_mcp_config("/nonexistent/path/config.yaml")
    
    # Should return default config with MCP disabled
    assert config.enabled is False
    assert len(config.services) == 0
    print("✓ Load nonexistent config returns default disabled config")


def test_validate_config_valid():
    """测试验证有效配置 / Test validating valid config"""
    auth = AuthConfig(type="none")
    service = ServiceConfig(
        name="valid_service",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    config = MCPConfig(enabled=True, services=[service])
    errors = validate_config(config)
    
    assert len(errors) == 0
    print("✓ Valid config passes validation")


def test_validate_config_no_services():
    """测试验证无服务配置 / Test validating config with no services"""
    config = MCPConfig(enabled=True, services=[])
    errors = validate_config(config)
    
    assert len(errors) == 1
    assert "No services configured" in errors[0]
    print("✓ Validation detects missing services")


def test_validate_config_duplicate_names():
    """测试验证重复服务名 / Test validating duplicate service names"""
    auth = AuthConfig(type="none")
    service1 = ServiceConfig(
        name="duplicate",
        enabled=True,
        endpoint="https://api1.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    service2 = ServiceConfig(
        name="duplicate",
        enabled=True,
        endpoint="https://api2.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    config = MCPConfig(enabled=True, services=[service1, service2])
    errors = validate_config(config)
    
    assert any("Duplicate service name" in error for error in errors)
    print("✓ Validation detects duplicate service names")


def test_validate_config_missing_endpoint():
    """测试验证缺少端点 / Test validating missing endpoint"""
    auth = AuthConfig(type="none")
    service = ServiceConfig(
        name="no_endpoint",
        enabled=True,
        endpoint="",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    config = MCPConfig(enabled=True, services=[service])
    errors = validate_config(config)
    
    assert any("missing endpoint" in error for error in errors)
    print("✓ Validation detects missing endpoint")


def test_validate_config_no_domains():
    """测试验证无域配置 / Test validating config with no domains"""
    auth = AuthConfig(type="none")
    service = ServiceConfig(
        name="no_domains",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=[]
    )
    
    config = MCPConfig(enabled=True, services=[service])
    errors = validate_config(config)
    
    assert any("has no domains" in error for error in errors)
    print("✓ Validation detects missing domains")


def test_validate_config_invalid_protocol():
    """测试验证无效协议 / Test validating invalid protocol"""
    auth = AuthConfig(type="none")
    service = ServiceConfig(
        name="invalid_protocol",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="invalid",
        authentication=auth,
        domains=["test"]
    )
    
    config = MCPConfig(enabled=True, services=[service])
    errors = validate_config(config)
    
    assert any("invalid protocol" in error for error in errors)
    print("✓ Validation detects invalid protocol")


def test_validate_config_invalid_auth_type():
    """测试验证无效认证类型 / Test validating invalid auth type"""
    auth = AuthConfig(type="invalid_auth")
    service = ServiceConfig(
        name="invalid_auth",
        enabled=True,
        endpoint="https://api.example.com",
        protocol="rest",
        authentication=auth,
        domains=["test"]
    )
    
    config = MCPConfig(enabled=True, services=[service])
    errors = validate_config(config)
    
    assert any("invalid auth type" in error for error in errors)
    print("✓ Validation detects invalid auth type")


def main():
    """运行所有测试 / Run all tests"""
    print("\n" + "=" * 70)
    print("MCP配置解析器测试 / MCP Configuration Parser Tests")
    print("=" * 70 + "\n")
    
    test_auth_config_none()
    test_auth_config_api_key()
    test_auth_config_bearer()
    test_auth_config_basic()
    test_service_config_handles_domain()
    test_service_config_availability()
    test_mcp_config_get_service_by_name()
    test_mcp_config_get_services_for_domain()
    test_mcp_config_disabled_globally()
    test_load_mcp_config_from_yaml()
    test_load_mcp_config_nonexistent_file()
    test_validate_config_valid()
    test_validate_config_no_services()
    test_validate_config_duplicate_names()
    test_validate_config_missing_endpoint()
    test_validate_config_no_domains()
    test_validate_config_invalid_protocol()
    test_validate_config_invalid_auth_type()
    
    print("\n" + "=" * 70)
    print("✨ 所有MCP配置测试通过！/ All MCP config tests passed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
