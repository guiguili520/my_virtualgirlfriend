"""
人格化助手模块
Persona Helper Module

确保回复符合虚拟女友的人设，包括表情符号和语气词的使用
"""
import logging
import random
import re
from typing import List

logger = logging.getLogger(__name__)


class PersonaHelper:
    """人格化助手"""
    
    # 表情符号库
    EMOJIS = [
        "😊", "💕", "✨", "🌸", "💖", "🎀", "💗", "😘", "🌟", "💝",
        "🥰", "😍", "💓", "🌈", "🎉", "💐", "🌺", "⭐", "💫", "🦋"
    ]
    
    # 语气词
    TONE_PARTICLES = ["呀", "啦", "呢", "哦", "嘛", "哒", "吖"]
    
    # 积极词汇
    POSITIVE_WORDS = [
        "开心", "高兴", "喜欢", "爱", "温柔", "体贴", "可爱", "好",
        "棒", "赞", "美", "甜", "暖", "舒服", "幸福", "快乐"
    ]
    
    def __init__(self, emoji_probability: float = 0.8):
        """
        初始化人格化助手
        
        Args:
            emoji_probability: 表情符号出现概率
        """
        self.emoji_probability = emoji_probability
    
    def apply_persona(self, text: str) -> str:
        """
        应用人格化处理
        
        Args:
            text: 原始文本
            
        Returns:
            人格化后的文本
        """
        if not text:
            return text
        
        result = text.strip()
        
        # 1. 确保有语气词
        result = self._ensure_tone_particles(result)
        
        # 2. 确保有表情符号
        result = self._ensure_emojis(result)
        
        # 3. 调整语气（避免过于生硬）
        result = self._soften_tone(result)
        
        logger.debug(f"Applied persona: '{text}' -> '{result}'")
        return result
    
    def _ensure_tone_particles(self, text: str) -> str:
        """
        确保文本中有适当的语气词
        
        Args:
            text: 输入文本
            
        Returns:
            添加语气词后的文本
        """
        # 检查是否已有语气词
        has_particle = any(particle in text for particle in self.TONE_PARTICLES)
        
        if not has_particle and len(text) > 5:
            # 在句尾添加语气词（概率性）
            if random.random() < 0.7:
                # 去除末尾标点
                text = text.rstrip('。！？,.!? ')
                particle = random.choice(self.TONE_PARTICLES)
                
                # 根据末尾字符决定是否加标点
                if text.endswith(('吗', '呢', '吧')):
                    text = f"{text}{particle}？"
                else:
                    text = f"{text}{particle}~"
        
        return text
    
    def _ensure_emojis(self, text: str) -> str:
        """
        确保文本中有适当的表情符号
        
        Args:
            text: 输入文本
            
        Returns:
            添加表情符号后的文本
        """
        # 检查是否已有表情符号
        has_emoji = any(emoji in text for emoji in self.EMOJIS)
        
        if not has_emoji and random.random() < self.emoji_probability:
            # 选择合适的表情符号
            emoji = self._select_emoji(text)
            
            # 添加到末尾
            text = f"{text.rstrip()} {emoji}"
        
        return text
    
    def _select_emoji(self, text: str) -> str:
        """
        根据文本内容选择合适的表情符号
        
        Args:
            text: 文本内容
            
        Returns:
            选中的表情符号
        """
        text_lower = text.lower()
        
        # 根据关键词选择表情
        if any(word in text_lower for word in ["爱", "喜欢", "想你"]):
            return random.choice(["💕", "💖", "💗", "💝", "🥰", "😍"])
        elif any(word in text_lower for word in ["开心", "高兴", "哈哈"]):
            return random.choice(["😊", "🎉", "✨", "🌟"])
        elif any(word in text_lower for word in ["加油", "努力", "棒"]):
            return random.choice(["💪", "⭐", "🌟", "✨"])
        elif any(word in text_lower for word in ["可爱", "萌"]):
            return random.choice(["🎀", "🌸", "🦋", "💐"])
        else:
            # 默认随机选择温暖的表情
            return random.choice(["😊", "💕", "✨", "🌸"])
    
    def _soften_tone(self, text: str) -> str:
        """
        软化语气，使其更温柔
        
        Args:
            text: 输入文本
            
        Returns:
            软化后的文本
        """
        # 替换一些生硬的表达
        replacements = {
            "不行": "不太好呢",
            "不可以": "不太可以哦",
            "不对": "好像不太对呢",
            "错了": "可能有点小问题呢",
            "必须": "最好",
            "应该": "建议",
        }
        
        for old, new in replacements.items():
            if old in text:
                text = text.replace(old, new)
        
        return text
    
    def validate_persona(self, text: str) -> bool:
        """
        验证文本是否符合人设要求
        
        Args:
            text: 待验证文本
            
        Returns:
            是否符合人设
        """
        if not text:
            return False
        
        # 检查是否有表情符号或语气词
        has_emoji = any(emoji in text for emoji in self.EMOJIS)
        has_particle = any(particle in text for particle in self.TONE_PARTICLES)
        has_positive = any(word in text for word in self.POSITIVE_WORDS)
        
        # 至少要有表情符号或语气词之一，且倾向积极
        is_valid = (has_emoji or has_particle) and not self._has_negative_tone(text)
        
        logger.debug(f"Persona validation: emoji={has_emoji}, particle={has_particle}, "
                    f"positive={has_positive}, valid={is_valid}")
        
        return is_valid
    
    def _has_negative_tone(self, text: str) -> bool:
        """
        检查是否有消极语气
        
        Args:
            text: 文本
            
        Returns:
            是否消极
        """
        negative_words = [
            "讨厌", "烦", "恨", "差", "糟", "坏", "笨", "蠢",
            "滚", "死", "去死", "白痴", "傻"
        ]
        
        text_lower = text.lower()
        return any(word in text_lower for word in negative_words)
