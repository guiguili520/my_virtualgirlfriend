#!/usr/bin/env python
"""
推理流水线演示
Inference Pipeline Demo

演示增强推理流水线的功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from inference import run_chat
import json


def print_separator():
    """打印分隔线"""
    print("=" * 80)


def demo_basic_chat():
    """演示基本聊天（无增强）"""
    print_separator()
    print("【演示1: 基本聊天】")
    print_separator()
    
    queries = [
        "你好呀~",
        "我今天很开心",
        "晚安",
    ]
    
    for query in queries:
        print(f"\n用户: {query}")
        result = run_chat(query, opts={"enable_enhancement": False})
        print(f"女友: {result['response']}")
        print(f"增强使用: {result['metadata']['enhancement_used']}")
        print(f"处理时间: {result['metadata']['processing_time']:.3f}秒")


def demo_enhanced_chat():
    """演示增强聊天"""
    print_separator()
    print("【演示2: 增强聊天】")
    print_separator()
    
    queries = [
        "今天的天气怎么样？",
        "告诉我一些健康生活的建议",
        "你知道最近有什么好看的电影吗？",
    ]
    
    for query in queries:
        print(f"\n用户: {query}")
        result = run_chat(query, opts={"enable_enhancement": True})
        print(f"女友: {result['response']}")
        print(f"增强使用: {result['metadata']['enhancement_used']}")
        print(f"数据源: {', '.join(result['metadata']['sources']) if result['metadata']['sources'] else '无'}")
        print(f"处理时间: {result['metadata']['processing_time']:.3f}秒")


def demo_with_history():
    """演示带对话历史的聊天"""
    print_separator()
    print("【演示3: 带对话历史的多轮对话】")
    print_separator()
    
    history = []
    
    conversations = [
        "你好呀，今天天气真好",
        "是呀，要不要一起出去散步？",
        "好啊，去哪里呢？",
    ]
    
    for user_msg in conversations:
        print(f"\n用户: {user_msg}")
        result = run_chat(user_msg, history=history)
        assistant_msg = result['response']
        print(f"女友: {assistant_msg}")
        
        # 更新历史
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": assistant_msg})


def demo_decision_logic():
    """演示增强决策逻辑"""
    print_separator()
    print("【演示4: 增强决策逻辑】")
    print_separator()
    
    test_cases = [
        ("嗨", "太短，不触发增强"),
        ("我很开心", "普通陈述，不触发增强"),
        ("今天天气怎么样？", "包含疑问词，触发增强"),
        ("你知道吗？", "太短，不触发增强"),
        ("告诉我关于健康的知识", "包含关键词，触发增强"),
    ]
    
    for query, expected in test_cases:
        result = run_chat(query)
        enhancement_used = result['metadata']['enhancement_used']
        print(f"\n查询: {query}")
        print(f"预期: {expected}")
        print(f"实际: {'触发增强' if enhancement_used else '不触发增强'}")


def demo_detailed_metadata():
    """演示详细的元数据"""
    print_separator()
    print("【演示5: 详细元数据】")
    print_separator()
    
    query = "今天的天气怎么样呢？"
    print(f"\n用户: {query}")
    result = run_chat(query)
    
    print(f"\n女友: {result['response']}")
    print("\n【元数据详情】")
    print(json.dumps(result['metadata'], indent=2, ensure_ascii=False))


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" " * 20 + "虚拟女友推理流水线演示")
    print(" " * 20 + "Inference Pipeline Demo")
    print("=" * 80 + "\n")
    
    try:
        # 运行各个演示
        demo_basic_chat()
        print("\n")
        
        demo_enhanced_chat()
        print("\n")
        
        demo_with_history()
        print("\n")
        
        demo_decision_logic()
        print("\n")
        
        demo_detailed_metadata()
        print("\n")
        
        print_separator()
        print(" " * 30 + "演示完成!")
        print_separator()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
