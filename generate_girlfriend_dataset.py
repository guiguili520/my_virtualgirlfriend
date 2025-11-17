#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟女友聊天数据集生成器
生成温柔体贴、俏皮可爱的二次元女友聊天数据
使用模块化架构，支持50+场景的结构化生成
"""

import os
from generator import GirlfriendDatasetGenerator


def main():
    """主函数"""
    print("=" * 60)
    print("🌸 虚拟女友聊天数据集生成器 🌸")
    print("=" * 60)
    
    # 创建生成器
    generator = GirlfriendDatasetGenerator()
    
    # 显示场景目录信息
    print(f"\n📊 场景目录信息:")
    print(f"   总场景数: {generator.metadata['total_scenarios']}")
    print(f"   分类数: {len(generator.metadata['categories'])}")
    print(f"   标签数: {len(generator.metadata['tags'])}")
    print(f"   分类列表: {', '.join(sorted(generator.metadata['categories']))}")
    
    # 验证场景目录满足要求
    assert generator.metadata['total_scenarios'] >= 50, \
        f"场景数量不足50个，当前只有{generator.metadata['total_scenarios']}个"
    print(f"   ✅ 场景数量验证通过 (≥50)")
    
    # 生成数据集（使用随机模式以保持与原版兼容）
    print(f"\n🔄 开始生成数据集...")
    print(f"   模式: 随机生成 (random)")
    print(f"   目标数量: 500条")
    
    dataset = generator.generate_random_dataset(num_samples=500)
    
    # 保存数据集
    print(f"\n💾 保存数据集...")
    output_file = generator.save_dataset(dataset)
    
    # 获取统计信息
    stats = generator.get_statistics(dataset)
    
    print(f"\n✨ 数据集生成完成！")
    print(f"📁 文件路径: {output_file}")
    print(f"📊 数据统计:")
    print(f"   总样本数: {stats['total_samples']}")
    print(f"   唯一指令数: {stats['unique_instructions']}")
    print(f"   Emoji覆盖率: {stats['emoji_coverage']}")
    print(f"   空输入比例: {stats['empty_input_ratio']}")
    print(f"   平均输出长度: {stats['avg_output_length']:.1f}字符")
    
    # 显示示例数据
    generator.print_sample_data(dataset, 3)
    
    print(f"\n{'=' * 60}")
    print("✅ 生成完成！数据集已保存。")
    print("=" * 60)


if __name__ == "__main__":
    main()
