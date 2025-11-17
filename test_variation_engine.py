#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试变化引擎的完整功能
"""

import json
from variation_engine import (
    VariationEngine,
    generate_variations_for_scenario,
    get_tone_for_scenario,
    SCENARIO_TONE_MAP
)


def test_basic_variation():
    """测试基本变体生成"""
    print("=" * 70)
    print("测试 1: 基本变体生成（8个变体）")
    print("=" * 70)
    
    template = "早安呀！😊 今天也要元气满满哦！"
    variations = generate_variations_for_scenario(template, num_variants=8, tone="happy", seed=42)
    
    print(f"原始模板: {template}")
    print(f"\n生成的 {len(variations)} 个变体:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")
    
    # 验证每个变体都包含emoji
    all_have_emoji = all('😊' in var or '😄' in var or '✨' in var or '💕' in var or '🌸' in var for var in variations)
    print(f"\n✓ 所有变体都包含表情符号: {all_have_emoji}")


def test_configurable_variants():
    """测试可配置的变体数量"""
    print("\n" + "=" * 70)
    print("测试 2: 可配置的变体数量")
    print("=" * 70)
    
    template = "加油呀！💪 你一定可以的！"
    
    for num in [3, 8, 10]:
        variations = generate_variations_for_scenario(template, num_variants=num, tone="encourage", seed=123)
        print(f"\n请求 {num} 个变体，实际生成: {len(variations)} 个")
        for i, var in enumerate(variations[:3], 1):  # 只显示前3个
            print(f"  {i}. {var}")
        if len(variations) > 3:
            print(f"  ... 还有 {len(variations) - 3} 个变体")


def test_deterministic_seeding():
    """测试确定性种子"""
    print("\n" + "=" * 70)
    print("测试 3: 确定性种子（相同种子应产生相同结果）")
    print("=" * 70)
    
    template = "晚安~ 🌙 做个好梦！"
    seed = 456
    
    variations_a = generate_variations_for_scenario(template, num_variants=5, tone="care", seed=seed)
    variations_b = generate_variations_for_scenario(template, num_variants=5, tone="care", seed=seed)
    
    print(f"使用种子 {seed} 生成两次:")
    print(f"\n第一次生成:")
    for i, var in enumerate(variations_a[:3], 1):
        print(f"  {i}. {var}")
    
    print(f"\n第二次生成:")
    for i, var in enumerate(variations_b[:3], 1):
        print(f"  {i}. {var}")
    
    is_identical = variations_a == variations_b
    print(f"\n✓ 两次生成完全相同: {is_identical}")


def test_placeholder_filling():
    """测试占位符填充"""
    print("\n" + "=" * 70)
    print("测试 4: 占位符填充")
    print("=" * 70)
    
    template = "{pet_name}，{encouragement}！💕 记得{care_action}哦~"
    variations = generate_variations_for_scenario(template, num_variants=8, tone="care", seed=789)
    
    print(f"原始模板: {template}")
    print(f"\n生成的 {len(variations)} 个变体（占位符已填充）:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")
    
    # 验证占位符被替换
    placeholders_removed = all('{' not in var and '}' not in var for var in variations)
    print(f"\n✓ 所有占位符都已填充: {placeholders_removed}")


def test_emoji_variation():
    """测试表情符号变化"""
    print("\n" + "=" * 70)
    print("测试 5: 表情符号变化（不同情感基调）")
    print("=" * 70)
    
    template = "我也爱你！💕 超级超级爱你！"
    
    tones = ["love", "happy", "excited"]
    for tone in tones:
        variations = generate_variations_for_scenario(template, num_variants=5, tone=tone, seed=101)
        print(f"\n基调: {tone}")
        print("变体:")
        for i, var in enumerate(variations[:3], 1):
            print(f"  {i}. {var}")


def test_tone_modifiers():
    """测试语气词添加"""
    print("\n" + "=" * 70)
    print("测试 6: 语气词添加（呀、啦、哦、呢等）")
    print("=" * 70)
    
    template = "好想你！能不能多陪陪我？"
    variations = generate_variations_for_scenario(template, num_variants=8, tone="cute", seed=202)
    
    print(f"原始模板: {template}")
    print(f"\n生成的变体（注意语气词）:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")
    
    # 检测常见语气词
    tone_words = ['呀', '啦', '哦', '呢', '嘛', '吖', '喵', '哒', '捏', '呐']
    has_tone_words = [any(word in var for word in tone_words) for var in variations]
    percentage = sum(has_tone_words) / len(variations) * 100
    print(f"\n✓ {percentage:.1f}% 的变体包含语气词")


def test_persona_validation():
    """测试人设验证"""
    print("\n" + "=" * 70)
    print("测试 7: 人设验证（确保每个变体符合女友人设）")
    print("=" * 70)
    
    engine = VariationEngine(seed=303)
    
    # 测试不同场景
    scenarios = [
        ("早上好呀！😊 今天也要加油！", "happy", "早安场景"),
        ("别担心，我会一直陪着你的~ 💕", "comfort", "安慰场景"),
        ("太棒了！🎉 你真的很厉害！", "excited", "称赞场景"),
    ]
    
    for template, tone, desc in scenarios:
        variations = engine.generate_variations(template, num_variants=5, tone=tone)
        
        print(f"\n{desc}:")
        print(f"原始: {template}")
        
        # 验证所有变体
        all_valid = True
        for var in variations:
            # 检查是否有emoji
            import re
            emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]')
            has_emoji = bool(emoji_pattern.search(var))
            
            # 检查是否有积极词汇
            positive_words = ['好', '开心', '爱', '喜欢', '加油', '相信', '支持', '陪', '棒', '厉害', '呢', '呀', '啦', '哦']
            has_positive = any(word in var for word in positive_words)
            
            if not (has_emoji and has_positive):
                all_valid = False
                break
        
        print(f"✓ 所有变体都符合人设要求: {all_valid}")
        print(f"  示例: {variations[0]}")


def test_synonym_replacement():
    """测试同义词替换"""
    print("\n" + "=" * 70)
    print("测试 8: 同义词替换")
    print("=" * 70)
    
    template = "加油！相信你一定可以的！我会一直陪着你！"
    variations = generate_variations_for_scenario(template, num_variants=10, tone="encourage", seed=404)
    
    print(f"原始模板: {template}")
    print(f"\n生成的变体（注意同义词替换）:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")
    
    # 统计不同的变体
    unique_variations = set(variations)
    print(f"\n✓ 生成了 {len(unique_variations)} 个独特的变体（去重后）")


def test_sentence_reordering():
    """测试句子重排"""
    print("\n" + "=" * 70)
    print("测试 9: 句子重排（避免机械复制）")
    print("=" * 70)
    
    template = "早安！😊 希望你今天过得开心！我会一直陪着你的~"
    variations = generate_variations_for_scenario(template, num_variants=8, tone="happy", seed=505)
    
    print(f"原始模板: {template}")
    print(f"\n生成的变体（注意句子顺序和结构的变化）:")
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")


def test_scenario_tone_mapping():
    """测试场景-基调自动映射"""
    print("\n" + "=" * 70)
    print("测试 10: 场景-基调自动映射")
    print("=" * 70)
    
    print("部分场景的自动基调映射:")
    scenarios = [
        "早上问候", "遇到困难需要鼓励", "心情不好需要安慰",
        "表达爱意", "用户说生病了", "完成了某项任务"
    ]
    
    for scenario in scenarios:
        tone = get_tone_for_scenario(scenario)
        print(f"  {scenario:20s} -> {tone}")
    
    print(f"\n✓ 共支持 {len(SCENARIO_TONE_MAP)} 个场景的自动基调映射")


def main():
    """运行所有测试"""
    print("\n" + "🌸" * 35)
    print(" " * 20 + "变化引擎完整测试")
    print("🌸" * 35 + "\n")
    
    test_basic_variation()
    test_configurable_variants()
    test_deterministic_seeding()
    test_placeholder_filling()
    test_emoji_variation()
    test_tone_modifiers()
    test_persona_validation()
    test_synonym_replacement()
    test_sentence_reordering()
    test_scenario_tone_mapping()
    
    print("\n" + "=" * 70)
    print("✨ 所有测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
