#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具执行中介层
Tool Execution Middleware

负责：
1. 在提示词中包含工具信息
2. 解析模型输出中的工具调用请求
3. 执行工具并返回结果
4. 实现工具循环直到模型给出最终回答
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional

from .mcp_tool_manager import MCPToolManager

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    工具执行器

    负责管理工具调用的完整生命周期
    """

    # 工具调用的格式：<tool_call>{"tool": "...", "input": {...}}</tool_call>
    TOOL_CALL_PATTERN = r'<tool_call>(.*?)</tool_call>'

    def __init__(self):
        """初始化工具执行器"""
        self.tool_manager = MCPToolManager()
        logger.info("ToolExecutor initialized")

    def get_tool_context(self) -> str:
        """
        获取工具上下文信息，用于添加到提示词中

        Returns:
            工具信息的文本表示
        """
        tools = self.tool_manager.tools
        if not tools:
            return ""

        context_lines = [
            "【可用工具】",
            "你可以调用以下工具来帮助用户：",
            ""
        ]

        for tool_name, tool in tools.items():
            context_lines.append(f"- {tool_name}: {tool.description}")

            # 添加参数信息
            required_params = tool.input_schema.get("required", [])
            if required_params:
                params_str = ", ".join(required_params)
                context_lines.append(f"  (必需参数: {params_str})")

        context_lines.extend([
            "",
            "【工具调用格式】",
            "当你需要调用工具时，使用以下格式：",
            '<tool_call>{"tool": "工具的完整名称", "input": {"参数名": "参数值", ...}}</tool_call>',
            "",
            "【示例】",
            '如果用户询问"北京附近有什么餐厅"，你可以调用：',
            '<tool_call>{"tool": "amap-maps_search", "input": {"keywords": "餐厅", "city": "北京"}}</tool_call>',
            "",
        ])

        return "\n".join(context_lines)

    def parse_tool_calls(self, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        从文本中解析工具调用请求

        Args:
            text: 模型生成的文本

        Returns:
            [(工具名, 输入参数), ...]
        """
        tool_calls = []

        # 查找所有<tool_call>...</tool_call>块
        matches = re.findall(self.TOOL_CALL_PATTERN, text)

        for match in matches:
            try:
                call_data = json.loads(match)
                tool_name = call_data.get("tool")
                tool_input = call_data.get("input", {})

                if tool_name:
                    tool_calls.append((tool_name, tool_input))
                    logger.info(f"Parsed tool call: {tool_name} with input: {tool_input}")

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse tool call: {match}, error: {e}")

        return tool_calls

    def remove_tool_calls_from_text(self, text: str) -> str:
        """
        从文本中移除工具调用标记

        Args:
            text: 包含工具调用标记的文本

        Returns:
            清理后的文本
        """
        # 移除<tool_call>...</tool_call>块
        cleaned = re.sub(self.TOOL_CALL_PATTERN, '', text)
        return cleaned.strip()

    def execute_tool_calls(self, tool_calls: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, str]:
        """
        执行工具调用列表

        Args:
            tool_calls: [(工具名, 输入参数), ...]

        Returns:
            {工具名: 执行结果内容}
        """
        results = {}

        for tool_name, tool_input in tool_calls:
            logger.info(f"Executing tool: {tool_name}")
            result = self.tool_manager.execute_tool(tool_name, tool_input)

            if result.get("success"):
                results[tool_name] = result.get("content", "")
                logger.info(f"Tool {tool_name} executed successfully")
            else:
                error_msg = result.get("error", "Unknown error")
                results[tool_name] = f"[工具执行失败: {error_msg}]"
                logger.warning(f"Tool {tool_name} execution failed: {error_msg}")

        return results

    def format_tool_results(self, results: Dict[str, str]) -> str:
        """
        格式化工具执行结果，用于送回给模型

        Args:
            results: {工具名: 结果内容}

        Returns:
            格式化的结果文本
        """
        if not results:
            return ""

        lines = ["【工具执行结果】"]
        for tool_name, content in results.items():
            lines.append(f"\n工具: {tool_name}")
            lines.append(f"结果: {content[:500]}")  # 限制长度

        lines.append("\n请基于以上工具结果为用户生成最终回答。")
        return "\n".join(lines)

    def process_with_tools(
        self,
        initial_prompt: str,
        model_generator,
        max_iterations: int = 3
    ) -> str:
        """
        带工具支持的推理循环

        Args:
            initial_prompt: 初始提示词
            model_generator: 模型生成函数，签名：generator(prompt) -> str
            max_iterations: 最大迭代次数

        Returns:
            最终的模型回答（不包含工具调用标记）
        """
        current_prompt = initial_prompt
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Tool processing iteration {iteration}/{max_iterations}")

            # 调用模型生成回答
            response = model_generator(current_prompt)

            # 尝试从响应中解析工具调用
            tool_calls = self.parse_tool_calls(response)

            if not tool_calls:
                # 没有工具调用，返回清理后的响应
                logger.info("No tool calls found, returning final response")
                return self.remove_tool_calls_from_text(response)

            # 执行工具调用
            logger.info(f"Found {len(tool_calls)} tool call(s)")
            results = self.execute_tool_calls(tool_calls)

            # 构建新的提示词，让模型基���工具结果继续生成
            tool_results_text = self.format_tool_results(results)
            current_prompt = f"""{response}

{tool_results_text}"""

            logger.info(f"Updated prompt with tool results for next iteration")

        # 达到最大迭代次数，返回最后的响应
        logger.warning(f"Reached max iterations ({max_iterations})")
        return self.remove_tool_calls_from_text(response)
