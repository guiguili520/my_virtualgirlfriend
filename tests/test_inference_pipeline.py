"""
推理流水线测试
Tests for Inference Pipeline

测试推理流水线的各个功能：决策逻辑、增强、人格化、降级处理等
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from inference.pipeline import InferencePipeline, run_chat
from enhance import PersonaHelper


class TestInferencePipeline(unittest.TestCase):
    """推理流水线测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.pipeline = InferencePipeline(use_mock_model=True)
    
    def test_pipeline_initialization(self):
        """测试流水线初始化"""
        self.assertIsNotNone(self.pipeline.ranker)
        self.assertIsNotNone(self.pipeline.deduplicator)
        self.assertIsNotNone(self.pipeline.summarizer)
        self.assertIsNotNone(self.pipeline.persona_helper)
        self.assertIsNotNone(self.pipeline.model)
    
    def test_run_chat_basic(self):
        """测试基本聊天功能"""
        result = self.pipeline.run_chat("你好呀")
        
        self.assertIn("response", result)
        self.assertIn("metadata", result)
        self.assertIsInstance(result["response"], str)
        self.assertTrue(len(result["response"]) > 0)
        
        # 检查元数据
        metadata = result["metadata"]
        self.assertIn("enhancement_used", metadata)
        self.assertIn("sources", metadata)
        self.assertIn("processing_time", metadata)
        self.assertIn("stages", metadata)
    
    def test_enhancement_decision_short_input(self):
        """测试短输入不触发增强"""
        result = self.pipeline.run_chat("嗨")
        self.assertFalse(result["metadata"]["enhancement_used"])
    
    def test_enhancement_decision_with_keyword(self):
        """测试关键词触发增强"""
        result = self.pipeline.run_chat("今天的天气怎么样？")
        # 应该触发增强决策（虽然mock结果可能不实际增强）
        stages = result["metadata"]["stages"]
        self.assertIn("decision", stages)
    
    def test_enhancement_decision_with_question(self):
        """测试问句触发增强"""
        result = self.pipeline.run_chat("你知道最近有什么好看的电影吗？")
        stages = result["metadata"]["stages"]
        self.assertIn("decision", stages)
    
    def test_non_enhanced_query(self):
        """测试非增强查询仍能正常工作"""
        result = self.pipeline.run_chat("我好开心啊", opts={"enable_enhancement": False})
        
        self.assertIn("response", result)
        self.assertFalse(result["metadata"]["enhancement_used"])
        self.assertIsInstance(result["response"], str)
        self.assertTrue(len(result["response"]) > 0)
    
    def test_with_history(self):
        """测试带对话历史的聊天"""
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好呀~ 😊"},
            {"role": "user", "content": "今天天气真好"},
        ]
        
        result = self.pipeline.run_chat("是呀，要不要出去走走？", history=history)
        
        self.assertIn("response", result)
        self.assertTrue(len(result["response"]) > 0)
    
    def test_persona_enforcement(self):
        """测试人格化强制执行"""
        result = self.pipeline.run_chat("你好")
        response = result["response"]
        
        # 检查是否有表情符号或语气词
        has_emoji = any(emoji in response for emoji in PersonaHelper.EMOJIS)
        has_particle = any(particle in response for particle in PersonaHelper.TONE_PARTICLES)
        
        # 至少应该有其中之一
        self.assertTrue(has_emoji or has_particle, 
                       f"Response lacks persona markers: {response}")
    
    def test_enhancement_with_mock_search(self):
        """测试使用模拟搜索的增强"""
        result = self.pipeline.run_chat("今天天气怎么样？")
        
        # 验证响应存在
        self.assertIn("response", result)
        
        # 如果增强被使用，应该有sources
        if result["metadata"]["enhancement_used"]:
            self.assertTrue(len(result["metadata"]["sources"]) > 0)
    
    def test_enhancement_with_mock_mcp(self):
        """测试使用模拟MCP的增强"""
        result = self.pipeline.run_chat("请告诉我关于健康生活的建议")
        
        # 验证响应存在
        self.assertIn("response", result)
        self.assertIsInstance(result["response"], str)
    
    def test_fallback_on_enhancement_failure(self):
        """测试增强失败时的降级处理"""
        # Mock增强方法使其抛出异常
        with patch.object(self.pipeline, '_perform_enhancement', 
                         side_effect=Exception("Mock enhancement error")):
            result = self.pipeline.run_chat("今天天气怎么样？")
            
            # 即使增强失败，也应该返回有效响应
            self.assertIn("response", result)
            self.assertTrue(len(result["response"]) > 0)
            self.assertFalse(result["metadata"]["enhancement_used"])
    
    def test_fallback_on_model_failure(self):
        """测试模型失败时的降级处理"""
        # Mock模型使其抛出异常
        with patch.object(self.pipeline.model, 'generate_reply',
                         side_effect=Exception("Mock model error")):
            result = self.pipeline.run_chat("你好")
            
            # 应该返回默认错误响应
            self.assertIn("response", result)
            self.assertIn("抱歉", result["response"])
    
    def test_structured_logging(self):
        """测试结构化日志记录"""
        result = self.pipeline.run_chat("你好吗？")
        
        # 检查stages信息
        stages = result["metadata"]["stages"]
        self.assertIn("decision", stages)
        self.assertIn("enhancement", stages)
        self.assertIn("generation", stages)
        self.assertIn("persona", stages)
        
        # 检查decision阶段
        self.assertIn("need_enhancement", stages["decision"])
        
        # 检查generation阶段
        self.assertIn("success", stages["generation"])
        
        # 检查persona阶段
        self.assertIn("success", stages["persona"])
    
    def test_processing_time_recorded(self):
        """测试处理时间被记录"""
        result = self.pipeline.run_chat("你好")
        
        processing_time = result["metadata"]["processing_time"]
        self.assertIsInstance(processing_time, float)
        self.assertGreater(processing_time, 0)
        self.assertLess(processing_time, 10)  # 应该在10秒内完成
    
    def test_custom_opts_override(self):
        """测试自定义选项覆盖"""
        # 禁用增强
        result1 = self.pipeline.run_chat(
            "今天天气怎么样？",
            opts={"enable_enhancement": False}
        )
        self.assertFalse(result1["metadata"]["enhancement_used"])
        
        # 启用增强
        result2 = self.pipeline.run_chat(
            "今天天气怎么样？",
            opts={"enable_enhancement": True}
        )
        # 决策应该被触发
        self.assertIn("decision", result2["metadata"]["stages"])


class TestRunChatFunction(unittest.TestCase):
    """测试run_chat便捷函数"""
    
    def test_run_chat_function(self):
        """测试run_chat函数"""
        result = run_chat("你好呀")
        
        self.assertIn("response", result)
        self.assertIn("metadata", result)
        self.assertIsInstance(result["response"], str)
    
    def test_run_chat_with_all_params(self):
        """测试带所有参数的run_chat"""
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好呀~ 😊"}
        ]
        opts = {"enable_enhancement": False}
        
        result = run_chat("你今天怎么样？", history=history, opts=opts)
        
        self.assertIn("response", result)
        self.assertFalse(result["metadata"]["enhancement_used"])


class TestPersonaValidation(unittest.TestCase):
    """测试人格化验证"""
    
    def setUp(self):
        """测试前准备"""
        self.pipeline = InferencePipeline(use_mock_model=True)
    
    def test_persona_has_emoji(self):
        """测试响应包含表情符号"""
        # 多次测试以应对随机性
        results = [self.pipeline.run_chat("你好") for _ in range(5)]
        
        # 至少一些响应应该有表情符号
        has_emoji_count = sum(
            1 for r in results 
            if any(emoji in r["response"] for emoji in PersonaHelper.EMOJIS)
        )
        
        self.assertGreater(has_emoji_count, 0)
    
    def test_persona_has_tone_particles(self):
        """测试响应包含语气词"""
        results = [self.pipeline.run_chat("你在干嘛？") for _ in range(5)]
        
        # 至少一些响应应该有语气词
        has_particle_count = sum(
            1 for r in results
            if any(particle in r["response"] for particle in PersonaHelper.TONE_PARTICLES)
        )
        
        self.assertGreater(has_particle_count, 0)


class TestEnhancementDecision(unittest.TestCase):
    """测试增强决策逻辑"""
    
    def setUp(self):
        """测试前准备"""
        self.pipeline = InferencePipeline(use_mock_model=True)
    
    def test_decision_with_short_text(self):
        """测试短文本不触发增强"""
        need = self.pipeline._decide_enhancement("嗨", {})
        self.assertFalse(need)
    
    def test_decision_with_keyword(self):
        """测试关键词触发增强"""
        # 使用足够长的查询
        need = self.pipeline._decide_enhancement("今天的天气怎么样呢？", {})
        self.assertTrue(need)
    
    def test_decision_with_question_mark(self):
        """测试问号触发增强"""
        # 使用足够长的查询（至少10个字符）
        need = self.pipeline._decide_enhancement("你知道这个东西是什么吗？", {})
        self.assertTrue(need)
    
    def test_decision_disabled_by_config(self):
        """测试配置禁用增强"""
        need = self.pipeline._decide_enhancement(
            "今天天气怎么样？",
            {"enable_enhancement": False}
        )
        self.assertFalse(need)


class TestMockSearchAndMCP(unittest.TestCase):
    """测试模拟搜索和MCP"""
    
    def setUp(self):
        """测试前准备"""
        self.pipeline = InferencePipeline(use_mock_model=True)
    
    def test_mock_search_returns_results(self):
        """测试模拟搜索返回结果"""
        results = self.pipeline._mock_search("天气")
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("content", results[0])
            self.assertIn("source", results[0])
            self.assertIn("score", results[0])
    
    def test_mock_mcp_returns_results(self):
        """测试模拟MCP返回结果"""
        results = self.pipeline._mock_mcp("请告诉我关于健康的建议")
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("content", results[0])
            self.assertIn("source", results[0])
            self.assertIn("score", results[0])


if __name__ == '__main__':
    unittest.main()
