"""
虚拟女友模型推理接口
Virtual Girlfriend Model Inference Interface

提供加载和调用大模型生成回复的功能
"""
import sys
import random
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scenarios import SCENARIO_CATALOG


class GirlfriendChatModel:
    """虚拟女友聊天模型"""
    
    def __init__(self, model_path=None, use_mock=True):
        """
        初始化模型
        
        Args:
            model_path: 模型路径（如果使用真实模型）
            use_mock: 是否使用模拟模式（默认True，用于演示）
        """
        self.model_path = model_path
        self.use_mock = use_mock
        self.model = None
        self.tokenizer = None
        
        if not use_mock and model_path:
            self._load_model()
        
    def _load_model(self):
        """加载真实的大模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"正在加载模型: {self.model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            print("模型加载完成！")
        except ImportError:
            print("警告: 未安装 transformers 库，将使用模拟模式")
            self.use_mock = True
        except Exception as e:
            print(f"模型加载失败: {e}，将使用模拟模式")
            self.use_mock = True
    
    def generate_reply(self, user_message, context=None):
        """
        生成虚拟女友的回复
        
        Args:
            user_message: 用户输入的消息
            context: 对话上下文（可选）
            
        Returns:
            str: 虚拟女友的回复
        """
        if self.use_mock:
            return self._generate_mock_reply(user_message)
        else:
            return self._generate_model_reply(user_message, context)
    
    def _generate_mock_reply(self, user_message):
        """生成模拟回复（用于演示）"""
        message_lower = user_message.lower()
        
        # 根据关键词匹配场景并返回回复
        for scenario in SCENARIO_CATALOG:
            scenario_dict = scenario.to_dict() if hasattr(scenario, 'to_dict') else scenario
            instruction = scenario_dict.get("instruction", "")
            templates = scenario_dict.get("response_templates", [])
            
            # 简单的关键词匹配
            if any(keyword in message_lower for keyword in self._extract_keywords(instruction)):
                if templates:
                    return random.choice(templates)
        
        # 如果没有匹配到，返回通用回复
        default_replies = [
            "嗯嗯，我在听呢~ 😊",
            "你说的对哦！💕",
            "好哒好哒~ ✨",
            "哈哈，真有意思呀~ 🌸",
            "我也这么想呢！💖",
            "是嘛是嘛~ 说来听听呀~ 🎀",
            "嘿嘿，你好可爱呀~ 💗",
            "我明白你的意思啦~ 😘",
            "真的吗？快跟我说说~ 🌟",
            "好开心听你说这些~ 💝"
        ]
        
        return random.choice(default_replies)
    
    def _extract_keywords(self, text):
        """从文本中提取关键词"""
        keywords = []
        common_words = ['早上', '晚上', '开心', '难过', '工作', '学习', '吃饭', '睡觉', 
                       '天气', '下雨', '喜欢', '爱', '想', '累', '加油', '生病', '感冒']
        
        for word in common_words:
            if word in text:
                keywords.append(word)
        
        return keywords
    
    def _generate_model_reply(self, user_message, context=None):
        """使用真实模型生成回复"""
        if not self.model or not self.tokenizer:
            return self._generate_mock_reply(user_message)
        
        try:
            # 构建提示词
            system_prompt = """你是一个温柔体贴的虚拟女友，性格特点：
- 温柔体贴，善解人意
- 俏皮可爱，充满活力
- 阳光开朗，积极向上
- 关心对方，给予支持

请用自然、亲密的语气回复，适当使用表情符号和语气词（呀、啦、呢、哦等）。"""
            
            # 添加上下文
            conversation = system_prompt + "\n\n"
            if context:
                for msg in context[-5:]:  # 只保留最近5条对话
                    role = "用户" if msg.get("role") == "user" else "女友"
                    conversation += f"{role}: {msg.get('content')}\n"
            
            conversation += f"用户: {user_message}\n女友: "
            
            # 生成回复
            inputs = self.tokenizer(conversation, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.8,
                top_p=0.9,
                do_sample=True
            )
            
            reply = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # 提取女友的回复部分
            reply = reply.split("女友: ")[-1].strip()
            
            return reply
            
        except Exception as e:
            print(f"模型推理失败: {e}")
            return self._generate_mock_reply(user_message)


# 全局模型实例（延迟加载）
_model_instance = None


def get_model_instance(model_path=None, use_mock=True):
    """获取模型实例（单例模式）"""
    global _model_instance
    if _model_instance is None:
        _model_instance = GirlfriendChatModel(model_path, use_mock)
    return _model_instance


def generate_girlfriend_reply(user_message, context=None, model_path=None):
    """
    生成虚拟女友回复的便捷函数
    
    Args:
        user_message: 用户消息
        context: 对话上下文
        model_path: 模型路径（可选）
        
    Returns:
        str: 虚拟女友的回复
    """
    model = get_model_instance(model_path)
    return model.generate_reply(user_message, context)
