#!/usr/bin/env python3
"""
虚拟女友应用主入口
Main entry point for Virtual Girlfriend application
"""
import argparse
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import PROJECT_ROOT


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="虚拟女友应用 - Virtual Girlfriend Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --help              显示帮助信息
  
更多功能即将推出...
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Virtual Girlfriend v0.1.0"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("欢迎使用虚拟女友应用 / Welcome to Virtual Girlfriend")
    print("=" * 60)
    print()
    print(f"项目根目录: {PROJECT_ROOT}")
    print()
    print("可用功能:")
    print("  1. 数据集生成 - 运行 scripts/generate_dataset.py")
    print("  2. 模型训练 - 运行 scripts/fine_tune.py 或 scripts/lora_train.py")
    print("  3. Web UI - 运行 web/app.py (即将推出)")
    print()
    print("请使用对应的脚本来执行具体功能。")
    print()


if __name__ == "__main__":
    main()
