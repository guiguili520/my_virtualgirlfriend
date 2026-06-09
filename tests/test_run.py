#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2.0 online model smoke test and optional manual chat runner."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.inference import generate_girlfriend_reply


def test_online_model_smoke():
    """默认 mock 模式下不需要本地模型权重也应能生成回复。"""
    reply = generate_girlfriend_reply("你好", opts={"model_provider": "mock"})

    assert isinstance(reply, str)
    assert len(reply) > 0


if __name__ == "__main__":
    print("=" * 60)
    print("AI女友聊天系统 2.0 - 在线模型 API")
    print("=" * 60)
    print("输入 'exit' 或 'quit' 退出")

    while True:
        user_input = input("\n你: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "退出", "再见"]:
            print("再见呀，期待下次聊天~")
            break

        response = generate_girlfriend_reply(user_input)
        print(f"AI女友: {response}")
