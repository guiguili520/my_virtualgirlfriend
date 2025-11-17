#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变化引擎使用示例
展示如何在实际场景中使用变化引擎
"""

from variation_engine import (
    VariationEngine,
    generate_variations_for_scenario,
    get_tone_for_scenario
)


def example_1_basic_usage():
    """示例1: 基础使用"""
    print("=" * 70)
    print("示例1: 基础使用 - 生成8个变体")
    print("=" * 70)
    
    template = "早安呀！😊 今天也要元气满满哦！"
    
    # 使用便捷函数生成变体
    variations = generate_variations_for_scenario(
        base_response=template,
        num_variants=8,
        tone="happy"
    )
    
    print(f"原始模板: {template}")
    print(f"\n生成 {len(variations)} 个变体:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")


def example_2_with_placeholders():
    """示例2: 使用占位符"""
    print("\n" + "=" * 70)
    print("示例2: 使用占位符 - 动态内容填充")
    print("=" * 70)
    
    # 定义带占位符的模板
    template = "{pet_name}，今天{time}要{care_action}哦！💕 {encouragement}！"
    
    print(f"原始模板: {template}")
    print("占位符说明:")
    print("  {pet_name} - 昵称 (宝贝/亲爱的/小可爱等)")
    print("  {time} - 时间 (今天/现在/此刻等)")
    print("  {care_action} - 关心动作 (照顾好自己/好好休息等)")
    print("  {encouragement} - 鼓励语 (你一定可以的/我相信你等)")
    
    variations = generate_variations_for_scenario(
        base_response=template,
        num_variants=10,
        tone="care",
        seed=42
    )
    
    print(f"\n生成 {len(variations)} 个变体（占位符已自动填充）:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")


def example_3_different_tones():
    """示例3: 不同情感基调"""
    print("\n" + "=" * 70)
    print("示例3: 不同情感基调 - 同一模板不同风格")
    print("=" * 70)
    
    template = "我会一直陪着你的！💕"
    
    tones = {
        "happy": "开心场景",
        "care": "关心场景",
        "encourage": "鼓励场景",
        "love": "爱意场景",
        "comfort": "安慰场景"
    }
    
    print(f"原始模板: {template}\n")
    
    for tone, desc in tones.items():
        variations = generate_variations_for_scenario(
            base_response=template,
            num_variants=3,
            tone=tone,
            seed=123
        )
        print(f"{desc} ({tone}):")
        for i, var in enumerate(variations, 1):
            print(f"  {i}. {var}")
        print()


def example_4_deterministic_generation():
    """示例4: 确定性生成"""
    print("=" * 70)
    print("示例4: 确定性生成 - 使用种子确保可重现")
    print("=" * 70)
    
    template = "加油呀！💪 你是最棒的！"
    seed = 999
    
    print(f"原始模板: {template}")
    print(f"使用种子: {seed}\n")
    
    print("第一次生成:")
    variations_1 = generate_variations_for_scenario(
        base_response=template,
        num_variants=5,
        tone="encourage",
        seed=seed
    )
    for i, var in enumerate(variations_1, 1):
        print(f"  {i}. {var}")
    
    print("\n第二次生成（相同种子）:")
    variations_2 = generate_variations_for_scenario(
        base_response=template,
        num_variants=5,
        tone="encourage",
        seed=seed
    )
    for i, var in enumerate(variations_2, 1):
        print(f"  {i}. {var}")
    
    print(f"\n✓ 两次生成完全相同: {variations_1 == variations_2}")


def example_5_class_usage():
    """示例5: 使用类进行批量处理"""
    print("\n" + "=" * 70)
    print("示例5: 使用 VariationEngine 类进行批量处理")
    print("=" * 70)
    
    # 创建引擎实例
    engine = VariationEngine(seed=456)
    
    # 定义多个场景
    scenarios = [
        {
            "instruction": "早上问候",
            "template": "早安！😊 新的一天开始了！",
        },
        {
            "instruction": "遇到困难需要鼓励",
            "template": "别灰心！💪 你一定可以的！",
        },
        {
            "instruction": "表达爱意",
            "template": "我爱你！💕 超级超级爱你！",
        }
    ]
    
    print("批量处理3个场景，每个生成5个变体:\n")
    
    for scenario in scenarios:
        instruction = scenario["instruction"]
        template = scenario["template"]
        
        # 自动获取情感基调
        tone = get_tone_for_scenario(instruction)
        
        # 生成变体
        variations = engine.generate_variations(
            template=template,
            num_variants=5,
            tone=tone
        )
        
        print(f"场景: {instruction}")
        print(f"基调: {tone}")
        print(f"模板: {template}")
        print("变体:")
        for i, var in enumerate(variations, 1):
            print(f"  {i}. {var}")
        print()


def example_6_configurable_variants():
    """示例6: 可配置的变体数量"""
    print("=" * 70)
    print("示例6: 可配置的变体数量")
    print("=" * 70)
    
    template = "晚安~ 🌙 做个好梦！"
    
    print(f"原始模板: {template}\n")
    
    for num_variants in [3, 5, 8, 10]:
        variations = generate_variations_for_scenario(
            base_response=template,
            num_variants=num_variants,
            tone="care",
            seed=789
        )
        
        print(f"请求 {num_variants} 个变体，实际生成: {len(variations)} 个")
        # 只显示前3个
        for i, var in enumerate(variations[:3], 1):
            print(f"  {i}. {var}")
        if len(variations) > 3:
            print(f"  ... 还有 {len(variations) - 3} 个变体")
        print()


def example_7_scenario_integration():
    """示例7: 与场景系统集成"""
    print("=" * 70)
    print("示例7: 与场景系统集成 - 自动基调检测")
    print("=" * 70)
    
    # 定义多个场景（模拟真实数据集）
    scenarios = [
        {"instruction": "早上问候", "input": "早上好", "base_output": "早安！😊 今天也要加油！"},
        {"instruction": "天气炎热", "input": "今天好热", "base_output": "天气这么热，要注意防暑哦！☀️ 多喝水！"},
        {"instruction": "用户说生病了", "input": "我感冒了", "base_output": "啊？！感冒了吗？🥺 要好好休息！"},
        {"instruction": "完成了某项任务", "input": "我做到了", "base_output": "太棒了！🎉 我就知道你一定可以的！"},
        {"instruction": "表达爱意", "input": "我爱你", "base_output": "我也爱你！💕💕💕"},
    ]
    
    engine = VariationEngine(seed=111)
    
    print("为5个不同场景自动生成变体:\n")
    
    for scenario in scenarios:
        instruction = scenario["instruction"]
        template = scenario["base_output"]
        
        # 自动检测情感基调
        tone = get_tone_for_scenario(instruction)
        
        # 生成3个变体作为示例
        variations = engine.generate_variations(
            template=template,
            num_variants=3,
            tone=tone
        )
        
        print(f"场景: {instruction}")
        print(f"用户输入: {scenario['input']}")
        print(f"自动检测基调: {tone}")
        print(f"基础回复: {template}")
        print("生成的变体:")
        for i, var in enumerate(variations, 1):
            print(f"  {i}. {var}")
        print()


def example_8_quality_validation():
    """示例8: 质量验证"""
    print("=" * 70)
    print("示例8: 质量验证 - 确保所有变体符合人设")
    print("=" * 70)
    
    template = "加油！你一定可以的！"
    variations = generate_variations_for_scenario(
        base_response=template,
        num_variants=10,
        tone="encourage",
        seed=222
    )
    
    print(f"原始模板: {template}")
    print(f"生成 {len(variations)} 个变体\n")
    
    # 验证每个变体
    import re
    
    print("质量检查:")
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]')
    positive_words = ['好', '开心', '爱', '喜欢', '加油', '相信', '支持', '陪', '棒', '厉害', '可以', '呢', '呀', '啦', '哦']
    
    has_emoji_count = 0
    has_positive_count = 0
    
    for var in variations:
        if emoji_pattern.search(var):
            has_emoji_count += 1
        if any(word in var for word in positive_words):
            has_positive_count += 1
    
    emoji_percentage = (has_emoji_count / len(variations)) * 100
    positive_percentage = (has_positive_count / len(variations)) * 100
    
    print(f"  ✓ {has_emoji_count}/{len(variations)} ({emoji_percentage:.1f}%) 包含表情符号")
    print(f"  ✓ {has_positive_count}/{len(variations)} ({positive_percentage:.1f}%) 包含积极词汇")
    print(f"  ✓ 平均长度: {sum(len(v) for v in variations) / len(variations):.1f} 字符")
    print(f"  ✓ 所有变体都唯一: {len(set(variations)) == len(variations)}")
    
    print("\n生成的变体:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")


def main():
    """运行所有示例"""
    print("\n" + "🌸" * 35)
    print(" " * 15 + "变化引擎使用示例集合")
    print("🌸" * 35 + "\n")
    
    example_1_basic_usage()
    example_2_with_placeholders()
    example_3_different_tones()
    example_4_deterministic_generation()
    example_5_class_usage()
    example_6_configurable_variants()
    example_7_scenario_integration()
    example_8_quality_validation()
    
    print("\n" + "=" * 70)
    print("✨ 所有示例运行完成！")
    print("=" * 70)
    print("\n提示:")
    print("  - 查看 README_VARIATION_ENGINE.md 了解更多文档")
    print("  - 运行 python3 test_variation_engine.py 进行完整测试")
    print("  - 运行 python3 generate_girlfriend_dataset.py --help 查看命令行选项")
    print()


if __name__ == "__main__":
    main()
