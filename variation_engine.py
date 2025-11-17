#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变化引擎 (Variation Engine)
为虚拟女友聊天数据生成多样化的回复变体
"""

import random
from typing import List, Dict, Optional, Set
import re


class VariationEngine:
    """变化引擎：生成风格一致但措辞不同的回复变体"""
    
    def __init__(self, seed: Optional[int] = None):
        """
        初始化变化引擎
        
        Args:
            seed: 随机种子，用于确定性生成
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # 情感基调对应的表情符号集合
        self.emoji_sets = {
            "happy": ["😊", "😄", "🥰", "💕", "✨", "🌸", "💖", "🎉", "😁", "🌟"],
            "care": ["🥺", "💕", "🫂", "❤️", "💗", "🌸", "✨", "💝", "💓", "🤗"],
            "encourage": ["💪", "✨", "🌟", "⭐", "🔥", "👍", "💯", "🎯", "🚀", "💫"],
            "comfort": ["🫂", "💕", "🥺", "😢", "💗", "🌸", "✨", "💝", "🤲", "💞"],
            "playful": ["😄", "😊", "🎀", "🌈", "✨", "💫", "🎪", "🎨", "🎭", "🎵"],
            "love": ["💕", "💖", "💗", "💝", "💓", "💞", "❤️", "🥰", "😘", "💋"],
            "excited": ["🎉", "🥳", "🎊", "✨", "💫", "🌟", "⭐", "🎈", "🎆", "🔥"],
            "cute": ["🥺", "🙈", "😳", "💕", "🎀", "🌸", "✨", "💝", "🧸", "🍰"],
            "worried": ["🥺", "😢", "💔", "😤", "🤧", "💕", "😿", "🙏", "😔", "😞"]
        }
        
        # 语气词库
        self.tone_particles = {
            "soft": ["呀", "啦", "呢", "哦", "吖", "嘛", "哟"],
            "cute": ["呀", "喵", "哒", "捏", "呐", "咩"],
            "emphasis": ["啊", "呢", "哦", "耶", "哇"],
            "question": ["吗", "呢", "啊", "嘛"],
            "exclamation": ["啊", "呀", "哇", "耶", "喔"]
        }
        
        # 情感关键词同义词库
        self.synonym_pools = {
            # 问候类
            "早安": ["早上好", "早安", "早呀", "早"],
            "晚安": ["晚安", "晚安啦", "睡个好觉", "好梦"],
            
            # 鼓励类
            "加油": ["加油", "努力", "继续加油", "坚持", "别放弃", "冲鸭"],
            "相信": ["相信", "信任", "确信", "坚信"],
            "可以": ["可以", "能行", "没问题", "一定行"],
            "厉害": ["厉害", "棒", "优秀", "出色", "很强", "了不起"],
            
            # 关心类
            "担心": ["担心", "担忧", "忧虑", "挂念", "放心不下"],
            "注意": ["注意", "小心", "当心", "留意"],
            "休息": ["休息", "歇歇", "放松", "放松一下"],
            "照顾": ["照顾", "爱护", "呵护", "保重"],
            
            # 情感类
            "开心": ["开心", "高兴", "快乐", "愉快", "欣喜"],
            "想你": ["想你", "想念你", "思念你", "惦记你"],
            "爱你": ["爱你", "喜欢你", "爱着你", "超爱你"],
            "陪着": ["陪着", "陪伴", "在你身边", "和你在一起"],
            
            # 程度副词
            "很": ["很", "非常", "特别", "超级", "十分", "好"],
            "一直": ["一直", "始终", "总是", "永远"],
            
            # 转折/连接
            "但是": ["但是", "不过", "可是", "然而"],
            "所以": ["所以", "因此", "那么"],
            
            # 动作类
            "记得": ["记得", "别忘了", "要记住", "千万别忘"],
            "希望": ["希望", "期望", "盼望", "祝愿"]
        }
        
        # 占位符对应的内容池
        self.placeholder_pools = {
            "pet_name": ["宝贝", "亲爱的", "小可爱", "宝宝", "亲亲", "小宝贝", "宝"],
            "encouragement": [
                "你一定可以的",
                "我相信你",
                "你很棒",
                "你很优秀",
                "你是最好的",
                "你能行的",
                "你很厉害"
            ],
            "care_action": [
                "照顾好自己",
                "好好休息",
                "注意身体",
                "爱护自己",
                "保重身体"
            ],
            "time": ["今天", "现在", "此刻", "这会儿"],
            "positive_feeling": ["开心", "快乐", "幸福", "温暖", "美好"]
        }
        
        # 支持性后缀
        self.supportive_suffixes = [
            "我会一直陪着你的",
            "有我在呢",
            "我会支持你的",
            "让我陪着你",
            "我永远在你身边",
            "我会一直在的",
            "相信我们一起可以的",
            "我们一起努力"
        ]
        
        # 句子开头变体
        self.sentence_starters = {
            "comfort": ["别担心", "没关系的", "不要紧的", "放心吧"],
            "encourage": ["来吧", "冲吧", "上吧", "试试看"],
            "care": ["要记得", "一定要", "别忘了", "记住要"]
        }
    
    def generate_variations(
        self,
        template: str,
        num_variants: int = 8,
        tone: str = "happy",
        preserve_structure: bool = False
    ) -> List[str]:
        """
        生成多个变体
        
        Args:
            template: 基础模板文本
            num_variants: 生成变体数量（默认8个）
            tone: 情感基调（happy/care/encourage/comfort等）
            preserve_structure: 是否保持句子结构不变
            
        Returns:
            变体列表
        """
        variations = set()
        attempts = 0
        max_attempts = num_variants * 20  # 避免无限循环
        
        while len(variations) < num_variants and attempts < max_attempts:
            # 选择不同的变换策略
            strategy = random.choice([
                "synonym_replace",
                "emoji_variation",
                "tone_modifier",
                "placeholder_fill",
                "sentence_reorder",
                "prefix_suffix",
                "combined"
            ])
            
            if preserve_structure:
                # 如果保持结构，只使用不改变句序的策略
                strategy = random.choice([
                    "synonym_replace",
                    "emoji_variation",
                    "tone_modifier",
                    "placeholder_fill",
                    "prefix_suffix"
                ])
            
            variation = self._apply_strategy(template, strategy, tone)
            
            # 验证变体
            if self._validate_variation(variation):
                variations.add(variation)
            
            attempts += 1
        
        result = list(variations)
        
        # 如果生成不足，使用组合策略补充
        while len(result) < num_variants:
            variation = self._apply_strategy(template, "combined", tone)
            if self._validate_variation(variation) and variation not in result:
                result.append(variation)
            if len(result) >= num_variants * 2:  # 防止无限循环
                break
        
        return result[:num_variants]
    
    def _apply_strategy(self, template: str, strategy: str, tone: str) -> str:
        """应用特定的变换策略"""
        # 首先总是填充占位符（如果存在）
        result = template
        if '{' in result and '}' in result:
            result = self._fill_placeholders(result)
        
        if strategy == "synonym_replace":
            return self._replace_synonyms(result)
        elif strategy == "emoji_variation":
            return self._vary_emojis(result, tone)
        elif strategy == "tone_modifier":
            return self._add_tone_modifiers(result)
        elif strategy == "placeholder_fill":
            return result  # Already filled above
        elif strategy == "sentence_reorder":
            return self._reorder_sentences(result)
        elif strategy == "prefix_suffix":
            return self._add_prefix_suffix(result, tone)
        elif strategy == "combined":
            # 组合多种策略
            result = self._replace_synonyms(result)
            result = self._add_tone_modifiers(result)
            result = self._vary_emojis(result, tone)
            if random.random() > 0.5:
                result = self._add_prefix_suffix(result, tone)
            return result
        return result
    
    def _replace_synonyms(self, text: str) -> str:
        """替换同义词"""
        result = text
        
        # 随机选择要替换的词汇
        replaceable_words = [word for word in self.synonym_pools.keys() if word in result]
        num_replacements = random.randint(1, min(3, len(replaceable_words) + 1))
        
        words_to_replace = random.sample(replaceable_words, min(num_replacements, len(replaceable_words)))
        
        for word in words_to_replace:
            if word in result:
                synonym = random.choice(self.synonym_pools[word])
                # 只替换第一次出现的位置
                result = result.replace(word, synonym, 1)
        
        return result
    
    def _vary_emojis(self, text: str, tone: str) -> str:
        """变化表情符号"""
        # 提取现有的表情符号
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]')
        existing_emojis = emoji_pattern.findall(text)
        
        result = text
        
        # 获取对应基调的表情符号集
        emoji_set = self.emoji_sets.get(tone, self.emoji_sets["happy"])
        
        # 替换部分表情符号
        for emoji in existing_emojis:
            if random.random() > 0.4:  # 60%概率替换
                new_emoji = random.choice(emoji_set)
                result = result.replace(emoji, new_emoji, 1)
        
        # 如果没有表情符号，添加一些
        if not existing_emojis:
            num_emojis = random.randint(1, 2)
            for _ in range(num_emojis):
                emoji = random.choice(emoji_set)
                # 在句子末尾或中间添加
                if random.random() > 0.5 and '，' in result:
                    parts = result.split('，', 1)
                    result = parts[0] + emoji + '，' + parts[1]
                else:
                    # 在感叹号或句末前添加
                    if '！' in result:
                        result = result.replace('！', emoji + '！', 1)
                    else:
                        result = result.rstrip() + emoji
        
        return result
    
    def _add_tone_modifiers(self, text: str) -> str:
        """添加语气词"""
        result = text
        
        # 在合适的位置添加语气词
        # 句末
        if result.endswith('！') or result.endswith('~'):
            particle_type = random.choice(["soft", "cute", "exclamation"])
            particle = random.choice(self.tone_particles[particle_type])
            result = result[:-1] + particle + result[-1]
        
        # 句中（在逗号后）
        if '，' in result and random.random() > 0.5:
            parts = result.split('，', 1)
            particle_type = random.choice(["soft", "emphasis"])
            particle = random.choice(self.tone_particles[particle_type])
            result = parts[0] + particle + '，' + parts[1]
        
        # 疑问句
        if '吗' in result or '呢' in result or '？' in result:
            particle = random.choice(self.tone_particles["question"])
            if '？' in result:
                result = result.replace('？', particle + '？', 1)
        
        return result
    
    def _fill_placeholders(self, text: str) -> str:
        """填充占位符"""
        result = text
        
        # 查找并替换占位符（多次迭代确保所有占位符都被替换）
        placeholder_pattern = re.compile(r'\{(\w+)\}')
        max_iterations = 10  # 防止无限循环
        iteration = 0
        
        while '{' in result and '}' in result and iteration < max_iterations:
            matches = placeholder_pattern.findall(result)
            if not matches:
                break
            
            for placeholder in matches:
                if placeholder in self.placeholder_pools:
                    replacement = random.choice(self.placeholder_pools[placeholder])
                    result = result.replace(f'{{{placeholder}}}', replacement, 1)
            
            iteration += 1
        
        return result
    
    def _reorder_sentences(self, text: str) -> str:
        """重新排列句子顺序"""
        # 按标点分割句子
        delimiters = ['！', '~', '。', '？']
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in delimiters:
                sentences.append(current)
                current = ""
        
        if current:
            sentences.append(current)
        
        # 只有多个句子时才重排
        if len(sentences) > 1:
            # 不完全随机，保持一定逻辑性
            # 随机交换相邻句子
            if random.random() > 0.5 and len(sentences) >= 2:
                i = random.randint(0, len(sentences) - 2)
                sentences[i], sentences[i + 1] = sentences[i + 1], sentences[i]
        
        return ''.join(sentences)
    
    def _add_prefix_suffix(self, text: str, tone: str) -> str:
        """添加前缀或后缀"""
        result = text
        
        # 添加前缀
        if random.random() > 0.6 and tone in self.sentence_starters:
            prefix = random.choice(self.sentence_starters[tone])
            result = prefix + '，' + result
        
        # 添加后缀
        if random.random() > 0.6:
            suffix = random.choice(self.supportive_suffixes)
            # 移除原有的结尾标点，添加后缀
            result = result.rstrip('！~。') + '！' + suffix + '~'
        
        return result
    
    def _validate_variation(self, text: str) -> bool:
        """
        验证变体是否符合人设要求
        
        要求：
        1. 至少包含一个表情符号
        2. 包含积极/安慰性词汇
        3. 长度合理
        """
        # 检查是否包含表情符号
        emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]|[\U00002600-\U000027BF]')
        if not emoji_pattern.search(text):
            return False
        
        # 检查长度
        if len(text) < 10 or len(text) > 200:
            return False
        
        # 检查是否包含积极词汇（至少一个）
        positive_words = [
            '好', '开心', '快乐', '爱', '喜欢', '加油', '相信', '支持', '陪',
            '温暖', '美好', '幸福', '棒', '厉害', '优秀', '可以', '没问题',
            '放心', '安心', '舒服', '甜', '可爱', '亲爱', '宝贝', '呢', '呀',
            '啦', '哦', '嘛', '吖'
        ]
        
        has_positive = any(word in text for word in positive_words)
        if not has_positive:
            return False
        
        return True
    
    def set_seed(self, seed: int):
        """设置新的随机种子"""
        self.seed = seed
        random.seed(seed)


def generate_variations_for_scenario(
    base_response: str,
    num_variants: int = 8,
    tone: str = "happy",
    seed: Optional[int] = None
) -> List[str]:
    """
    便捷函数：为单个场景生成变体
    
    Args:
        base_response: 基础回复文本
        num_variants: 要生成的变体数量（默认8）
        tone: 情感基调
        seed: 随机种子（用于确定性生成）
        
    Returns:
        变体列表
    """
    engine = VariationEngine(seed=seed)
    return engine.generate_variations(
        template=base_response,
        num_variants=num_variants,
        tone=tone
    )


# 情感基调映射表（用于自动检测场景对应的基调）
SCENARIO_TONE_MAP = {
    "早上问候": "happy",
    "早上刚醒来": "care",
    "晚上道别": "care",
    "很晚了还在工作": "care",
    "遇到困难需要鼓励": "encourage",
    "考试或面试前紧张": "encourage",
    "分享好心情": "happy",
    "感到无聊": "playful",
    "心情不好需要安慰": "comfort",
    "表达思念": "love",
    "提醒吃饭": "care",
    "提醒喝水": "care",
    "完成了某项任务": "excited",
    "用户夸奖女友": "cute",
    "下雨天提醒": "care",
    "天气炎热": "care",
    "用户说生病了": "worried",
    "熬夜提醒": "worried",
    "生日祝福": "excited",
    "想要关注": "cute",
    "聊游戏": "playful",
    "聊动漫": "playful",
    "表达爱意": "love",
    "学习中": "encourage",
    "工作压力大": "care",
    "聊吃的": "happy",
    "天气寒冷": "care"
}


def get_tone_for_scenario(scenario_instruction: str) -> str:
    """根据场景指令获取对应的情感基调"""
    return SCENARIO_TONE_MAP.get(scenario_instruction, "happy")


if __name__ == "__main__":
    # 测试用例
    print("=== 变化引擎测试 ===\n")
    
    # 测试1: 基本变体生成
    print("测试1: 基本变体生成")
    template1 = "早安呀！😊 今天也要元气满满哦！"
    variations1 = generate_variations_for_scenario(template1, num_variants=5, tone="happy", seed=42)
    print(f"原始: {template1}")
    print("变体:")
    for i, var in enumerate(variations1, 1):
        print(f"  {i}. {var}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试2: 占位符填充
    print("测试2: 占位符填充")
    template2 = "{pet_name}，{encouragement}！💕 我会一直陪着你的~"
    variations2 = generate_variations_for_scenario(template2, num_variants=5, tone="encourage", seed=123)
    print(f"原始: {template2}")
    print("变体:")
    for i, var in enumerate(variations2, 1):
        print(f"  {i}. {var}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试3: 不同基调
    print("测试3: 不同情感基调")
    template3 = "别担心，有我在呢！💕"
    for tone in ["comfort", "care", "encourage"]:
        print(f"\n基调: {tone}")
        variations3 = generate_variations_for_scenario(template3, num_variants=3, tone=tone, seed=456)
        for i, var in enumerate(variations3, 1):
            print(f"  {i}. {var}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试4: 确定性生成（相同种子产生相同结果）
    print("测试4: 确定性生成")
    template4 = "加油呀！✨ 你一定可以的！"
    print("使用相同种子生成两次:")
    vars_a = generate_variations_for_scenario(template4, num_variants=3, tone="encourage", seed=789)
    vars_b = generate_variations_for_scenario(template4, num_variants=3, tone="encourage", seed=789)
    print(f"第一次: {vars_a[0]}")
    print(f"第二次: {vars_b[0]}")
    print(f"是否相同: {vars_a == vars_b}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试5: 配置不同数量的变体
    print("测试5: 配置不同数量的变体")
    template5 = "晚安呀~ 🌙 做个好梦！"
    for num in [3, 8, 10]:
        variations5 = generate_variations_for_scenario(template5, num_variants=num, tone="care", seed=999)
        print(f"生成 {num} 个变体: 实际得到 {len(variations5)} 个")
