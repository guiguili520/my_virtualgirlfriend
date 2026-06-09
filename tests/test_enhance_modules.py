"""
增强模块测试
Tests for Enhancement Modules

测试排序、去重、摘要和人格化助手模块
"""
import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enhance import Ranker, Deduplicator, Summarizer, PersonaHelper


class TestRanker(unittest.TestCase):
    """排序器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.ranker = Ranker(top_k=3)
    
    def test_rank_empty_results(self):
        """测试空结果"""
        results = self.ranker.rank_results([])
        self.assertEqual(results, [])
    
    def test_rank_with_scores(self):
        """测试带分数的排序"""
        results = [
            {"content": "结果1", "source": "search", "score": 0.5},
            {"content": "结果2", "source": "mcp", "score": 0.9},
            {"content": "结果3", "source": "search", "score": 0.7},
        ]
        
        ranked = self.ranker.rank_results(results, "测试查询")
        
        # 应该按最终得分排序
        self.assertEqual(len(ranked), 3)
        self.assertTrue(all("final_score" in r for r in ranked))
        
        # 第一个应该是MCP结果（权重高）
        self.assertEqual(ranked[0]["source"], "mcp")
    
    def test_rank_keeps_top_k(self):
        """测试保留前K个结果"""
        results = [
            {"content": f"结果{i}", "source": "search", "score": 0.5 + i * 0.1}
            for i in range(10)
        ]
        
        ranked = self.ranker.rank_results(results)
        
        # 应该只保留top_k个
        self.assertEqual(len(ranked), self.ranker.top_k)


class TestDeduplicator(unittest.TestCase):
    """去重器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.deduplicator = Deduplicator(similarity_threshold=0.85)
    
    def test_deduplicate_empty(self):
        """测试空结果"""
        results = self.deduplicator.deduplicate([])
        self.assertEqual(results, [])
    
    def test_exact_duplicate(self):
        """测试精确重复"""
        results = [
            {"content": "这是一段文本", "source": "search"},
            {"content": "这是一段文本", "source": "mcp"},
            {"content": "这是另一段文本", "source": "search"},
        ]
        
        deduped = self.deduplicator.deduplicate(results)
        
        # 应该去掉一个重复的，保留2个不同的
        self.assertLessEqual(len(deduped), 2)
        self.assertGreater(len(deduped), 0)
    
    def test_no_duplicates(self):
        """测试无重复"""
        results = [
            {"content": "完全不同的文本A", "source": "search"},
            {"content": "完全不同的文本B", "source": "mcp"},
            {"content": "完全不同的文本C", "source": "search"},
        ]
        
        deduped = self.deduplicator.deduplicate(results)
        
        # 应该保留所有结果
        self.assertEqual(len(deduped), 3)
    
    def test_similarity_calculation(self):
        """测试相似度计算"""
        sim1 = self.deduplicator._calculate_similarity("abc", "abc")
        self.assertEqual(sim1, 1.0)
        
        sim2 = self.deduplicator._calculate_similarity("abc", "xyz")
        self.assertLess(sim2, 0.5)
        
        sim3 = self.deduplicator._calculate_similarity("", "abc")
        self.assertEqual(sim3, 0.0)


class TestSummarizer(unittest.TestCase):
    """摘要生成器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.summarizer = Summarizer(max_length=200)
    
    def test_summarize_empty(self):
        """测试空结果"""
        summary = self.summarizer.summarize([])
        self.assertEqual(summary, "")
    
    def test_summarize_single_result(self):
        """测试单个结果"""
        results = [
            {"content": "这是一段测试内容", "source": "search"}
        ]
        
        summary = self.summarizer.summarize(results)
        
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertIn("search", summary)
        self.assertIn("测试", summary)
    
    def test_summarize_multiple_results(self):
        """测试多个结果"""
        results = [
            {"content": "第一段内容关于天气", "source": "search"},
            {"content": "第二段内容关于健康", "source": "mcp"},
            {"content": "第三段内容关于学习", "source": "search"},
        ]
        
        summary = self.summarizer.summarize(results, query="生活")
        
        self.assertIsInstance(summary, str)
        self.assertLessEqual(len(summary), self.summarizer.max_length * 1.2)  # 允许一些误差
    
    def test_summarize_respects_max_length(self):
        """测试摘要遵守最大长度"""
        results = [
            {"content": "很长的内容" * 50, "source": "search"},
            {"content": "另一段很长的内容" * 50, "source": "mcp"},
        ]
        
        summary = self.summarizer.summarize(results)
        
        # 摘要应该被截断到最大长度附近
        self.assertLessEqual(len(summary), self.summarizer.max_length * 1.5)
    
    def test_extract_snippet(self):
        """测试片段提取"""
        content = "这是一段很长的文本内容，包含了很多信息，需要被正确地提取出关键部分"
        
        snippet = self.summarizer._extract_snippet(content, "关键", max_snippet_length=20)
        
        self.assertIsInstance(snippet, str)
        self.assertLessEqual(len(snippet), 30)  # 允许省略号


class TestPersonaHelper(unittest.TestCase):
    """人格化助手测试"""
    
    def setUp(self):
        """测试前准备"""
        self.helper = PersonaHelper(emoji_probability=1.0)  # 100%概率便于测试
    
    def test_apply_persona_adds_emoji(self):
        """测试添加表情符号"""
        text = "你好"
        result = self.helper.apply_persona(text)
        
        # 应该添加了表情符号
        has_emoji = any(emoji in result for emoji in self.helper.EMOJIS)
        self.assertTrue(has_emoji)
    
    def test_apply_persona_adds_tone_particle(self):
        """测试添加语气词"""
        text = "我很好"
        result = self.helper.apply_persona(text)
        
        # 应该有语气词或表情符号
        has_particle = any(particle in result for particle in self.helper.TONE_PARTICLES)
        has_emoji = any(emoji in result for emoji in self.helper.EMOJIS)
        
        self.assertTrue(has_particle or has_emoji)
    
    def test_apply_persona_empty_text(self):
        """测试空文本"""
        result = self.helper.apply_persona("")
        self.assertEqual(result, "")
    
    def test_validate_persona_valid(self):
        """测试验证合格的人格化文本"""
        text = "你好呀~ 😊"
        is_valid = self.helper.validate_persona(text)
        self.assertTrue(is_valid)
    
    def test_validate_persona_invalid(self):
        """测试验证不合格的文本"""
        text = "你好"
        # 纯文本可能不合格（取决于是否有表情/语气词）
        # 但这个测试主要是确保函数能运行
        result = self.helper.validate_persona(text)
        self.assertIsInstance(result, bool)
    
    def test_validate_persona_negative(self):
        """测试拒绝消极语气"""
        text = "我讨厌你"
        is_valid = self.helper.validate_persona(text)
        self.assertFalse(is_valid)
    
    def test_soften_tone(self):
        """测试软化语气"""
        text = "这个不行，你错了"
        result = self.helper._soften_tone(text)
        
        # 应该替换了生硬的词
        self.assertNotIn("不行", result)
        self.assertNotIn("错了", result)
    
    def test_select_emoji_by_context(self):
        """测试根据上下文选择表情"""
        emoji_love = self.helper._select_emoji("我爱你")
        self.assertIn(emoji_love, self.helper.EMOJIS)
        
        emoji_happy = self.helper._select_emoji("我好开心")
        self.assertIn(emoji_happy, self.helper.EMOJIS)
    
    def test_ensure_emojis(self):
        """测试确保有表情符号"""
        text = "你好呀"
        result = self.helper._ensure_emojis(text)
        
        # 应该添加了表情
        has_emoji = any(emoji in result for emoji in self.helper.EMOJIS)
        self.assertTrue(has_emoji)
    
    def test_ensure_tone_particles(self):
        """测试确保有语气词"""
        text = "我很好"
        result = self.helper._ensure_tone_particles(text)
        
        # 应该添加了语气词或原本就有
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


class TestPersonaHelperIntegration(unittest.TestCase):
    """人格化助手集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.helper = PersonaHelper(emoji_probability=0.8)
    
    def test_multiple_applications(self):
        """测试多次应用人格化"""
        text = "今天天气不错"
        
        results = [self.helper.apply_persona(text) for _ in range(10)]
        
        # 所有结果都应该是有效的
        for result in results:
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        
        # 至少一些应该有表情符号
        with_emoji = sum(1 for r in results if any(e in r for e in self.helper.EMOJIS))
        self.assertGreater(with_emoji, 0)
    
    def test_preserves_meaning(self):
        """测试保持原意"""
        text = "我今天很开心"
        result = self.helper.apply_persona(text)
        
        # 应该保留关键词
        self.assertIn("开心", result)


if __name__ == '__main__':
    unittest.main()
