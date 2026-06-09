"""
去重模块
Deduplication Module

对来自不同源的信息进行去重处理
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Deduplicator:
    """结果去重器"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        初始化去重器
        
        Args:
            similarity_threshold: 相似度阈值，超过此值认为是重复内容
        """
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对结果进行去重
        
        Args:
            results: 结果列表
            
        Returns:
            去重后的结果列表
        """
        if not results:
            logger.info("No results to deduplicate")
            return []
        
        # 使用哈希进行精确去重
        unique_results = self._exact_dedup(results)
        
        # 使用相似度进行模糊去重
        final_results = self._fuzzy_dedup(unique_results)
        
        logger.info(f"Deduplicated {len(results)} results to {len(final_results)}")
        return final_results
    
    def _exact_dedup(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        精确去重（基于内容哈希）
        
        Args:
            results: 结果列表
            
        Returns:
            去重后的结果列表
        """
        seen_contents = set()
        unique_results = []
        
        for result in results:
            content = result.get('content', '')
            content_hash = hash(content.strip().lower())
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _fuzzy_dedup(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        模糊去重（基于相似度）
        
        Args:
            results: 结果列表
            
        Returns:
            去重后的结果列表
        """
        if len(results) <= 1:
            return results
        
        final_results = []
        
        for i, result in enumerate(results):
            is_duplicate = False
            content_i = result.get('content', '')
            
            # 与已保留的结果比较
            for kept_result in final_results:
                content_kept = kept_result.get('content', '')
                similarity = self._calculate_similarity(content_i, content_kept)
                
                if similarity >= self.similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"Found duplicate (similarity={similarity:.2f})")
                    break
            
            if not is_duplicate:
                final_results.append(result)
        
        return final_results
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两段文本的相似度（简化版Jaccard相似度）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 转为字符集合
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        # Jaccard相似度
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
