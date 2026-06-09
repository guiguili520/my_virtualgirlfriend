#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具管理器
MCP Tool Manager

负责：
1. 管理预定义的MCP工具元数据（用于大模型的tool_use）
2. 执行大模型指定的工具调用
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from .mcp_config import load_mcp_config, ServiceConfig

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    service_name: str
    input_schema: Dict[str, Any]

    def to_claude_tool(self) -> Dict[str, Any]:
        """转换为Claude tool_use格式"""
        return {
            "name": f"{self.service_name}_{self.name}",
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.input_schema.get("properties", {}),
                "required": self.input_schema.get("required", [])
            }
        }


class MCPToolManager:
    """
    MCP工具管理器

    管理MCP服务的工具定义，并支持工具调用
    """

    # 预定义的工具列表（基于已知的MCP服务）
    PREDEFINED_TOOLS = {
        "amap-maps_search": MCPTool(
            name="search",
            description="搜索地点、地址或兴趣点（POI）。用于用户询问「附近有什么」、「怎么去某地」等地图相关问题。",
            service_name="amap-maps",
            input_schema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "搜索关键词，如「餐厅」、「医院」等"
                    },
                    "city": {
                        "type": "string",
                        "description": "城市名称，如「北京」、「上海」等，默认为当前位置"
                    },
                    "region": {
                        "type": "string",
                        "description": "区域范围，可选"
                    }
                },
                "required": ["keywords"]
            }
        ),
        "fetch_fetch": MCPTool(
            name="fetch",
            description="从网络获取网页内容。用于用户要求「查看某个网址的内容」、「抓取网页」等任务。",
            service_name="fetch",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要获取内容的网址，如 https://example.com"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "最大返回字符数，默认5000",
                        "default": 5000
                    },
                    "start_index": {
                        "type": "integer",
                        "description": "开始字符位置，用于获取长内容的后续部分，默认0",
                        "default": 0
                    }
                },
                "required": ["url"]
            }
        ),
        "mcp_tool_query": MCPTool(
            name="query",
            description="通用工具查询。用于各种信息查询和问题回答。",
            service_name="mcp_tool",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询内容"
                    }
                },
                "required": ["query"]
            }
        )
    }

    def __init__(self):
        """初始化工具管理器"""
        self.config = load_mcp_config()
        self.tools: Dict[str, MCPTool] = {}
        self.service_sessions: Dict[str, str] = {}
        self.service_clients: Dict[str, ServiceConfig] = {}

        logger.info("Initializing MCPToolManager...")

        # 使用预定义的工具
        self.tools = self.PREDEFINED_TOOLS.copy()
        logger.info(f"Loaded {len(self.tools)} predefined tools")

        # 初始化MCP服务连接
        self._init_services()

    def _init_services(self):
        """初始化所有MCP服务连接"""
        if not self.config.is_mcp_enabled():
            logger.warning("MCP is not enabled globally")
            return

        enabled_services = self.config.get_enabled_services()
        logger.info(f"Found {len(enabled_services)} enabled services")

        for service in enabled_services:
            try:
                session_id = self._perform_handshake(service)
                if session_id:
                    self.service_sessions[service.name] = session_id
                    self.service_clients[service.name] = service
                    logger.info(f"✓ Service {service.name} initialized")
                else:
                    logger.warning(f"Failed to initialize service {service.name}")
            except Exception as e:
                logger.error(f"Error initializing service {service.name}: {e}")

    def _perform_handshake(self, service: ServiceConfig) -> Optional[str]:
        """执行MCP握手"""
        try:
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "tools": {"listChanged": True}
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
            resp = requests.post(
                service.endpoint,
                json=init_payload,
                headers=headers,
                timeout=service.timeout
            )

            session_id = resp.headers.get('Mcp-Session-Id')
            if session_id:
                logger.debug(f"Got session ID from header: {session_id}")
                return session_id

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    session_id = data.get("result", {}).get("sessionId")
                    if session_id:
                        logger.debug(f"Got session ID from response body: {session_id}")
                        return session_id
                except Exception:
                    pass

            logger.warning(f"MCP handshake failed with status {resp.status_code}")
            return None

        except Exception as e:
            logger.error(f"MCP handshake exception: {e}")
            return None

    def get_tools_for_claude(self) -> List[Dict[str, Any]]:
        """
        获取Claude tool_use格式的工具列表

        Returns:
            Claude tool定义列表
        """
        return [tool.to_claude_tool() for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具调用

        Args:
            tool_name: 工具完整名称（service_name_tool_name格式）
            tool_input: 工具输入参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}",
                "available_tools": list(self.tools.keys())
            }

        tool = self.tools[tool_name]
        service_name = tool.service_name

        if service_name not in self.service_sessions:
            return {
                "success": False,
                "error": f"Service not initialized: {service_name}"
            }

        try:
            session_id = self.service_sessions[service_name]
            service = self.service_clients[service_name]

            # 构建工具调用请求
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool.name,
                    "arguments": tool_input
                }
            }

            headers = service.authentication.get_auth_header() or {}
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json, text/event-stream'
            headers['Mcp-Session-Id'] = session_id

            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

            resp = requests.post(
                service.endpoint,
                json=payload,
                headers=headers,
                timeout=service.timeout
            )

            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}: {resp.text[:200]}"
                }

            data = resp.json()

            # 处理响应
            if 'result' in data:
                result = data['result']

                # 提取内容
                if isinstance(result, dict) and 'content' in result:
                    content_items = result['content']
                    if isinstance(content_items, list) and len(content_items) > 0:
                        text_content = content_items[0].get('text', '')
                        return {
                            "success": True,
                            "content": text_content
                        }

                return {
                    "success": True,
                    "content": str(result)
                }

            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                return {
                    "success": False,
                    "error": error_msg
                }

            return {
                "success": False,
                "error": "Unexpected response format"
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
