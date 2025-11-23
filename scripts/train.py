#!/usr/bin/env python3
"""
模型训练脚本 (预留)
Model training script (placeholder)

本脚本用于统一管理模型训练流程，支持多种训练方式：
- 全参数微调 (fine_tune.py)
- LoRA 微调 (lora_train.py)
- 其他训练方法

This script provides a unified interface for model training,
supporting various training methods:
- Full parameter fine-tuning (fine_tune.py)
- LoRA fine-tuning (lora_train.py)
- Other training methods
"""
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """主函数"""
    print("=" * 60)
    print("虚拟女友模型训练 / Virtual Girlfriend Model Training")
    print("=" * 60)
    print()
    print("本功能即将推出，请使用以下脚本进行训练：")
    print("This feature is coming soon. Please use the following scripts:")
    print()
    print("1. LoRA 微调 (推荐 / Recommended):")
    print("   python scripts/lora_train.py")
    print()
    print("2. 全参数微调:")
    print("   python scripts/fine_tune.py")
    print()


if __name__ == "__main__":
    main()
