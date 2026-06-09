#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP功能演示脚本
MCP Feature Demo Script

演示如何使用MCP客户端查询外部服务
Demonstrates how to use MCP client to query external services
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp import MCPClient


def print_section(title):
    """打印分隔符 / Print section separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_basic_fetch():
    """演示基本查询 / Demo basic fetch"""
    print_section("1. 基本查询 / Basic Fetch")
    
    client = MCPClient()
    
    # 查询天气
    print("查询: 北京的天气怎么样？")
    response = client.fetch("weather", "北京的天气怎么样？")
    
    if response.success:
        print(f"✓ 成功获取响应")
        print(f"  服务: {response.service_name}")
        print(f"  内容: {response.content}")
        print(f"  置信度: {response.confidence:.2f}")
        print(f"  时间戳: {response.metadata.get('timestamp', 'N/A')}")
    else:
        print(f"✗ 查询失败: {response.error}")


def demo_multiple_domains():
    """演示多域查询 / Demo multiple domain queries"""
    print_section("2. 多域查询 / Multiple Domain Queries")
    
    client = MCPClient()
    
    queries = [
        ("weather", "明天的天气预报"),
        ("news", "最新科技新闻"),
        ("facts", "Python编程语言的历史"),
    ]
    
    for domain, query in queries:
        print(f"\n查询域: {domain}")
        print(f"查询: {query}")
        
        response = client.fetch(domain, query)
        
        if response.success:
            print(f"✓ {response.service_name} 返回: {response.content[:50]}...")
        else:
            print(f"✗ 失败: {response.error}")


def demo_available_domains():
    """演示获取可用域 / Demo get available domains"""
    print_section("3. 可用域列表 / Available Domains")
    
    client = MCPClient()
    domains = client.get_available_domains()
    
    print(f"共有 {len(domains)} 个可用域:")
    for i, domain in enumerate(domains, 1):
        print(f"  {i}. {domain}")


def demo_service_status():
    """演示服务状态 / Demo service status"""
    print_section("4. 服务状态 / Service Status")
    
    client = MCPClient()
    status = client.get_service_status()
    
    print(f"MCP状态: {'启用' if status['mcp_enabled'] else '禁用'}")
    print(f"总服务数: {status['total_services']}")
    print(f"启用服务数: {status['enabled_services']}")
    print(f"\n服务详情:")
    
    for service in status['services']:
        status_icon = "✓" if service['enabled'] else "✗"
        print(f"  {status_icon} {service['name']}")
        print(f"      协议: {service['protocol']}")
        print(f"      域: {', '.join(service['domains'])}")
        print(f"      优先级: {service['priority']}")


def demo_disabled_service():
    """演示禁用的服务 / Demo disabled service"""
    print_section("5. 禁用服务处理 / Disabled Service Handling")
    
    client = MCPClient()
    
    # 尝试查询translation域（该服务在配置中被禁用）
    print("查询: 翻译服务（已禁用）")
    response = client.fetch("translation", "Translate 'hello' to Chinese")
    
    if response.success:
        print(f"✓ 响应: {response.content}")
    else:
        print(f"✗ 预期的错误: {response.error}")
        print("  这是正常的，因为翻译服务被禁用了")


def demo_invalid_domain():
    """演示无效域处理 / Demo invalid domain handling"""
    print_section("6. 无效域处理 / Invalid Domain Handling")
    
    client = MCPClient()
    
    # 查询不存在的域
    print("查询: 不存在的域 'nonexistent'")
    response = client.fetch("nonexistent", "Some query")
    
    if response.success:
        print(f"✓ 响应: {response.content}")
    else:
        print(f"✗ 预期的错误: {response.error}")
        print("  这是正常的，因为没有服务处理该域")


def demo_girlfriend_integration():
    """演示与女友回复的集成 / Demo integration with girlfriend replies"""
    print_section("7. 女友回复集成示例 / Girlfriend Reply Integration")
    
    client = MCPClient()
    
    scenarios = [
        {
            "user_input": "明天天气怎么样？",
            "domain": "weather",
            "query": "明天的天气"
        },
        {
            "user_input": "有什么新闻吗？",
            "domain": "news",
            "query": "最新新闻"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n用户: {scenario['user_input']}")
        
        response = client.fetch(scenario['domain'], scenario['query'])
        
        if response.success:
            # 构建女友风格的回复
            girlfriend_reply = f"让我看看~ {response.content} 希望对你有帮助呀！😊"
            print(f"女友: {girlfriend_reply}")
        else:
            # 优雅降级
            girlfriend_reply = "抱歉呀，我现在查不到实时信息~ 不过我会一直陪着你的！💕"
            print(f"女友: {girlfriend_reply}")


def demo_response_structure():
    """演示响应结构 / Demo response structure"""
    print_section("8. 响应结构详解 / Response Structure Details")
    
    client = MCPClient()
    response = client.fetch("weather", "天气查询")
    
    print("MCPResponse 对象属性:")
    print(f"  content: {response.content}")
    print(f"  confidence: {response.confidence}")
    print(f"  service_name: {response.service_name}")
    print(f"  success: {response.success}")
    print(f"  error: {response.error}")
    print(f"  metadata: {response.metadata}")
    
    print("\n转换为字典:")
    response_dict = response.to_dict()
    for key, value in response_dict.items():
        print(f"  {key}: {value}")


def main():
    """运行所有演示 / Run all demos"""
    print("\n" + "🌸" * 35)
    print(" " * 20 + "MCP功能演示")
    print(" " * 18 + "MCP Feature Demo")
    print("🌸" * 35)
    
    try:
        demo_basic_fetch()
        demo_multiple_domains()
        demo_available_domains()
        demo_service_status()
        demo_disabled_service()
        demo_invalid_domain()
        demo_girlfriend_integration()
        demo_response_structure()
        
        print("\n" + "=" * 70)
        print("✨ 演示完成！/ Demo Complete!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
