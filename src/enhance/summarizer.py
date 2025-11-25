"""
摘要模块
Summarizer Module

将多个信息源合并为简短摘要，用于增强提示词
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class Summarizer:
    """摘要生成器"""
    
    def __init__(self, max_length: int = 200):
        """
        初始化摘要生成器
        
        Args:
            max_length: 摘要最大长度（字符数）
        """
        self.max_length = max_length
    
    def summarize(self, results: List[Dict[str, Any]], query: str = "") -> str:
        """
        生成结果摘要
        
        Args:
            results: 待摘要的结果列表
            query: 用户查询（用于上下文）
            
        Returns:
            摘要文本
        """
        if not results:
            logger.info("No results to summarize")
            return ""
        
        # 提取关键信息
        key_points = []
        total_length = 0
        
        for result in results:
            content = result.get('content', '')
            source = result.get('source', 'unknown')
            
            # 截取适当长度
            snippet = self._extract_snippet(content, query)
            
            # 检查是否超出最大长度
            point_text = f"[{source}] {snippet}"
            if total_length + len(point_text) > self.max_length:
                # 如果加上这条会超长，则截断或跳过
                remaining = self.max_length - total_length
                if remaining > 50:  # 至少留50个字符才添加
                    point_text = point_text[:remaining] + "..."
                    key_points.append(point_text)
                break
            
            key_points.append(point_text)
            total_length += len(point_text)
        
        # 合并成摘要
        if not key_points:
            summary = ""
        else:
            summary = " ".join(key_points)
        
        logger.info(f"Generated summary of {len(summary)} characters from {len(results)} results")
        return summary
    
    def _extract_snippet(self, content: str, query: str, max_snippet_length: int = 100) -> str:
        """
        从内容中提取关键片段
        
        Args:
            content: 完整内容
            query: 查询文本
            max_snippet_length: 片段最大长度
            
        Returns:
            提取的片段
        """
        if not content:
            return ""
        
        content = content.strip()
        
        # 如果内容本身就很短，直接返回
        if len(content) <= max_snippet_length:
            return content
        
        # 尝试找到与查询相关的部分
        if query:
            query_lower = query.lower()
            content_lower = content.lower()
            
            # 找到查询词首次出现的位置
            pos = content_lower.find(query_lower[:10])  # 使用查询前10个字符
            if pos != -1:
                # 以查询位置为中心提取片段
                start = max(0, pos - max_snippet_length // 2)
                end = min(len(content), start + max_snippet_length)
                snippet = content[start:end]
                
                # 添加省略号
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                
                return snippet.strip()
        
        # 如果没有找到相关部分，返回开头
        return content[:max_snippet_length] + "..."
