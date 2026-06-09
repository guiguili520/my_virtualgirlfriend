#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP (Multi-service Content Provider) Module

提供多服务内容提供者功能，用于增强虚拟女友的知识库
Provides multi-service content provider functionality to enhance virtual girlfriend's knowledge base
"""

from .mcp_config import (
    AuthConfig,
    ServiceConfig,
    MCPConfig,
    load_mcp_config,
    validate_config
)

from .mcp_client import (
    MCPClient,
    MCPResponse
)

__all__ = [
    'AuthConfig',
    'ServiceConfig',
    'MCPConfig',
    'load_mcp_config',
    'validate_config',
    'MCPClient',
    'MCPResponse',
]
