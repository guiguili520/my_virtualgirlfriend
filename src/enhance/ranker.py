"""
排序模块
Ranking Module

对来自网络搜索和MCP的结果进行排序和筛选
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Ranker:
    """结果排序器"""
    
    def __init__(self, top_k: int = 5):
        """
        初始化排序器
        
        Args:
            top_k: 保留前K个结果
        """
        self.top_k = top_k
    
    def rank_results(self, results: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
        """
        对结果进行排序
        
        Args:
            results: 待排序的结果列表，每个结果应包含 'content', 'source', 'score' 等字段
            query: 用户查询（用于相关性计算）
            
        Returns:
            排序后的结果列表
        """
        if not results:
            logger.info("No results to rank")
            return []
        
        # 计算每个结果的综合得分
        scored_results = []
        for result in results:
            score = self._calculate_score(result, query)
            result_with_score = result.copy()
            result_with_score['final_score'] = score
            scored_results.append(result_with_score)
        
        # 按得分降序排序
        sorted_results = sorted(scored_results, key=lambda x: x['final_score'], reverse=True)
        
        # 保留前K个
        top_results = sorted_results[:self.top_k]
        
        logger.info(f"Ranked {len(results)} results, kept top {len(top_results)}")
        return top_results
    
    def _calculate_score(self, result: Dict[str, Any], query: str) -> float:
        """
        计算结果的综合得分
        
        Args:
            result: 单个结果
            query: 用户查询
            
        Returns:
            综合得分
        """
        # 基础得分（如果result已有score字段）
        base_score = result.get('score', 0.5)
        
        # 来源权重
        source = result.get('source', 'unknown')
        source_weight = {
            'mcp': 1.2,      # MCP结果权重较高
            'search': 1.0,   # 搜索结果标准权重
            'unknown': 0.8   # 未知来源权重较低
        }.get(source, 0.8)
        
        # 内容长度权重（适中长度得分更高）
        content = result.get('content', '')
        length = len(content)
        if 50 <= length <= 500:
            length_weight = 1.0
        elif length < 50:
            length_weight = 0.7
        else:
            length_weight = 0.9
        
        # 相关性得分（简单关键词匹配）
        relevance_score = self._calculate_relevance(content, query)
        
        # 综合得分
        final_score = base_score * source_weight * length_weight * (1 + relevance_score * 0.5)
        
        return final_score
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """
        计算内容与查询的相关性
        
        Args:
            content: 内容文本
            query: 查询文本
            
        Returns:
            相关性得分 (0-1)
        """
        if not query or not content:
            return 0.5
        
        content_lower = content.lower()
        query_lower = query.lower()
        
        # 统计查询词在内容中出现的次数
        query_chars = set(query_lower)
        matched_chars = sum(1 for char in query_chars if char in content_lower)
        
        if not query_chars:
            return 0.5
        
        relevance = matched_chars / len(query_chars)
        return min(relevance, 1.0)
