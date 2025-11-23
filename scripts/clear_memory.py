#!/usr/bin/env python3
"""
内存清理脚本 - 在训练前运行以最大化可用内存
"""
import torch
import gc
import os

def clear_system_memory():
    """清理系统和PyTorch内存"""
    print("🧹 开始清理内存...")
    
    # 清理Python垃圾回收
    gc.collect()
    print("✓ Python 垃圾回收完成")
    
    # 清理MPS缓存
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
        print("✓ MPS 缓存已清理")
    
    # 清理CUDA缓存（如果有）
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("✓ CUDA 缓存已清理")
    
    print("✅ 内存清理完成！\n")

if __name__ == "__main__":
    clear_system_memory()
    
    # 显示系统信息
    print("📊 系统信息:")
    if torch.backends.mps.is_available():
        print(f"  MPS 可用: ✓")
        print(f"  建议: 训练前关闭其他应用以释放更多内存")
    print()
