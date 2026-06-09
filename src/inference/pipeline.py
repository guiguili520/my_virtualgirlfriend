"""
推理流水线
Inference Pipeline

实现完整的推理流程：检测是否需要增强、协调搜索/MCP调用、合并信息、构建增强提示词、
调用模型、应用人格规则
"""
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# 确保项目根目录在 Python 路径中
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 使用绝对导入（避免与 web 目录的模块冲突）
from src.config import (
    ENABLE_ENHANCEMENT, ENABLE_NETWORK_SEARCH, ENABLE_MCP,
    ENHANCEMENT_MIN_QUERY_LENGTH, ENHANCEMENT_KEYWORDS,
    RANKING_TOP_K, DEDUP_SIMILARITY_THRESHOLD, SUMMARY_MAX_LENGTH,
    PERSONA_EMOJI_PROBABILITY, ENABLE_MODEL_TOOL_CALLS
)
from src.enhance import Ranker, Deduplicator, Summarizer, PersonaHelper
from src.mcp import MCPClient
from src.mcp.tool_executor import ToolExecutor
from src.models.inference import GirlfriendChatModel, get_provider_presets

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InferencePipeline:
    """推理流水线"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        use_mock_model: bool = False,
        provider: Optional[str] = None,
        api_format: Optional[str] = None,
    ):
        """
        初始化推理流水线

        Args:
            model_path: 模型路径
            use_mock_model: 是否使用模拟模型
        """
        # 初始化增强组件
        self.ranker = Ranker(top_k=RANKING_TOP_K)
        self.deduplicator = Deduplicator(similarity_threshold=DEDUP_SIMILARITY_THRESHOLD)
        self.summarizer = Summarizer(max_length=SUMMARY_MAX_LENGTH)
        self.persona_helper = PersonaHelper(emoji_probability=PERSONA_EMOJI_PROBABILITY)

        # 初始化模型
        self.model = GirlfriendChatModel(
            model_path=model_path,
            use_mock=use_mock_model,
            provider=provider,
            api_format=api_format,
        )

        # MCP客户端和工具执行器按需初始化，避免普通聊天启动时访问外部服务。
        self._mcp_client: Optional[MCPClient] = None
        self._tool_executor: Optional[ToolExecutor] = None

        logger.info("InferencePipeline initialized")

    @property
    def mcp_client(self) -> MCPClient:
        if self._mcp_client is None:
            self._mcp_client = MCPClient()
        return self._mcp_client

    @property
    def tool_executor(self) -> ToolExecutor:
        if self._tool_executor is None:
            self._tool_executor = ToolExecutor()
        return self._tool_executor
    
    def run_chat(
        self,
        input_text: str,
        history: Optional[List[Dict[str, str]]] = None,
        opts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        运行聊天推理（主入口函数）
        
        Args:
            input_text: 用户输入
            history: 对话历史 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            opts: 可选配置项，可覆盖默认配置
                - enable_enhancement: 是否启用增强
                - enable_search: 是否启用搜索
                - enable_mcp: 是否启用MCP
                
        Returns:
            {
                "response": str,           # 最终回复
                "metadata": {              # 元数据
                    "enhancement_used": bool,
                    "sources": List[str],
                    "processing_time": float,
                    "stages": Dict[str, Any]
                }
            }
        """
        start_time = time.time()
        
        # 处理参数
        history = history or []
        opts = opts or {}
        
        # 阶段日志
        stages = {
            "decision": {},
            "enhancement": {},
            "generation": {},
            "persona": {}
        }
        
        logger.info(f"Processing chat input: '{input_text[:50]}...'")
        
        # 阶段1: 决策 - 是否需要增强
        need_enhancement = self._decide_enhancement(input_text, opts)
        stages["decision"]["need_enhancement"] = need_enhancement
        logger.info(f"Enhancement decision: {need_enhancement}")
        
        # 阶段2: 增强（如果需要）
        augmented_context = ""
        sources_used = []
        
        if need_enhancement:
            try:
                augmented_context, sources_used = self._perform_enhancement(input_text)
                stages["enhancement"]["success"] = True
                stages["enhancement"]["sources"] = sources_used
                stages["enhancement"]["context_length"] = len(augmented_context)
                logger.info(f"Enhancement completed with {len(sources_used)} sources")
            except Exception as e:
                logger.warning(f"Enhancement failed: {e}, falling back to pure model")
                stages["enhancement"]["success"] = False
                stages["enhancement"]["error"] = str(e)
        else:
            stages["enhancement"]["success"] = False
            stages["enhancement"]["reason"] = "Enhancement not needed"
        
        # 阶段3: 构建提示词并生成回复（带工具支持）
        try:
            enable_tools = opts.get("enable_tools", ENABLE_MODEL_TOOL_CALLS)
            prompt = self._build_prompt(
                input_text,
                history,
                augmented_context,
                include_tool_context=enable_tools
            )

            if enable_tools:
                # 定义模型生成函数供工具执行器使用
                def model_generator(prompt: str) -> str:
                    return self.model.generate_reply(prompt, context=history, opts=opts)

                # 使用工具执行器进行推理循环
                raw_response = self.tool_executor.process_with_tools(
                    initial_prompt=prompt,
                    model_generator=model_generator,
                    max_iterations=3
                )
            else:
                raw_response = self.model.generate_reply(prompt, context=history, opts=opts)

            stages["generation"]["success"] = True
            stages["generation"]["raw_length"] = len(raw_response)
            stages["generation"]["model"] = self.model.get_model_info(opts)
            logger.info(f"Model generated response: '{raw_response[:50]}...'")
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            raw_response = "抱歉呀，我刚才走神了~ 能再说一遍吗？😊"
            stages["generation"]["success"] = False
            stages["generation"]["error"] = str(e)
        
        # 阶段4: 应用人格规则
        try:
            final_response = self.persona_helper.apply_persona(raw_response)
            is_valid = self.persona_helper.validate_persona(final_response)
            stages["persona"]["success"] = True
            stages["persona"]["valid"] = is_valid
            stages["persona"]["final_length"] = len(final_response)
            
            if not is_valid:
                logger.warning("Response failed persona validation, but using it anyway")
            
            logger.info(f"Final response: '{final_response[:50]}...'")
        except Exception as e:
            logger.error(f"Persona application failed: {e}")
            final_response = raw_response
            stages["persona"]["success"] = False
            stages["persona"]["error"] = str(e)
        
        # 计算总处理时间
        processing_time = time.time() - start_time
        
        # 构建返回结果
        result = {
            "response": final_response,
            "metadata": {
                "enhancement_used": need_enhancement and stages["enhancement"].get("success", False),
                "sources": sources_used,
                "model": self.model.get_model_info(opts),
                "processing_time": processing_time,
                "stages": stages
            }
        }
        
        logger.info(f"Chat processing completed in {processing_time:.3f}s")
        return result
    
    def _decide_enhancement(self, input_text: str, opts: Dict[str, Any]) -> bool:
        """
        决策是否需要增强
        
        Args:
            input_text: 用户输入
            opts: 配置选项
            
        Returns:
            是否需要增强
        """
        # 检查全局配置
        enable_enhancement = opts.get("enable_enhancement", ENABLE_ENHANCEMENT)
        if not enable_enhancement:
            logger.debug("Enhancement disabled by config")
            return False
        
        # 检查输入长度
        if len(input_text) < ENHANCEMENT_MIN_QUERY_LENGTH:
            logger.debug(f"Input too short ({len(input_text)} < {ENHANCEMENT_MIN_QUERY_LENGTH})")
            return False
        
        # 检查是否包含触发关键词
        input_lower = input_text.lower()
        has_keyword = any(keyword in input_lower for keyword in ENHANCEMENT_KEYWORDS)
        
        if has_keyword:
            logger.debug(f"Enhancement triggered by keyword match")
            return True
        
        # 检查是否是问句
        is_question = any(char in input_text for char in ["?", "？", "吗", "呢", "么"])
        if is_question:
            logger.debug("Enhancement triggered by question pattern")
            return True
        
        logger.debug("Enhancement not needed based on heuristics")
        return False
    
    def _perform_enhancement(self, query: str) -> tuple[str, List[str]]:
        """
        执行增强流程：搜索 -> 排序 -> 去重 -> 摘要
        
        Args:
            query: 用户查询
            
        Returns:
            (增强上下文, 使用的数据源列表)
        """
        all_results = []
        sources = []
        
        # 调用网络搜索（如果启用）
        if ENABLE_NETWORK_SEARCH:
            try:
                search_results = self._mock_search(query)
                all_results.extend(search_results)
                if search_results:
                    sources.append("search")
                logger.info(f"Got {len(search_results)} search results")
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        # 调用MCP（如果启用）
        if ENABLE_MCP:
            try:
                domain = self._detect_mcp_domain(query)
                logger.info(f"Calling MCP service for domain: {domain}")
                mcp_resp = self.mcp_client.fetch(domain, query)

                if mcp_resp.success and mcp_resp.content:
                    all_results.append({
                        "content": mcp_resp.content,
                        "source": "mcp",
                        "score": float(mcp_resp.confidence)
                    })
                    sources.append("mcp")
                    logger.info(f"MCP response success: {mcp_resp.content[:100]}...")
                else:
                    logger.warning(f"MCP response failed or empty: success={mcp_resp.success}, error={mcp_resp.error}")
            except Exception as e:
                logger.error(f"MCP call failed with exception: {e}", exc_info=True)
        
        # 如果没有任何结果，返回空
        if not all_results:
            logger.info("No enhancement results available")
            return "", []
        
        # 排序
        ranked_results = self.ranker.rank_results(all_results, query)
        
        # 去重
        deduped_results = self.deduplicator.deduplicate(ranked_results)
        
        # 生成摘要
        summary = self.summarizer.summarize(deduped_results, query)
        
        return summary, sources
    
    def _detect_mcp_domain(self, query: str) -> str:
        """
        基于关键词从查询中检测MCP域
        """
        q = query.lower()

        # 天气相关关键词（优先级最高）
        weather_keywords = [
            "天气", "weather", "温度", "气温", "气候", "下雨", "下雪",
            "晴天", "阴天", "多云", "预报", "forecast", "冷", "热",
            "穿什么", "带伞"
        ]
        if any(k in q for k in weather_keywords):
            logger.info(f"Detected MCP domain: weather (query: {query[:30]}...)")
            return "weather"

        # 地图/导航相关关键词
        map_keywords = [
            "地图", "导航", "路线", "怎么走", "怎么去", "多远", "距离",
            "附近", "周边", "位置", "地址", "在哪", "哪里",
            "poi", "搜索地点", "找", "查找",
            "maps", "navigation", "route", "direction", "location"
        ]
        if any(k in q for k in map_keywords):
            logger.info(f"Detected MCP domain: maps (query: {query[:30]}...)")
            return "maps"

        # 新闻相关关键词
        news_keywords = ["新闻", "news", "头条", "热点", "最新消息", "报道"]
        if any(k in q for k in news_keywords):
            logger.info(f"Detected MCP domain: news (query: {query[:30]}...)")
            return "news"

        # 网页抓取相关关键词
        fetch_keywords = ["网页", "抓取", "url", "链接", "网站内容"]
        if any(k in q for k in fetch_keywords):
            logger.info(f"Detected MCP domain: fetch (query: {query[:30]}...)")
            return "fetch"

        logger.info(f"Detected MCP domain: facts (default, query: {query[:30]}...)")
        return "facts"
    
    def _build_prompt(
        self,
        input_text: str,
        history: List[Dict[str, str]],
        augmented_context: str,
        include_tool_context: bool = False
    ) -> str:
        """
        构建增强的提示词

        Args:
            input_text: 用户输入
            history: 对话历史
            augmented_context: 增强上下文

        Returns:
            完整的提示词
        """
        # 按需添加工具信息到提示词
        tool_context = self.tool_executor.get_tool_context() if include_tool_context else ""

        # 如果有增强上下文，添加到提示词中
        if augmented_context:
            # 移除来源标签，保持内容纯净
            clean_context = augmented_context.replace("[mcp] ", "").replace("[search] ", "")
            prompt = f"""{tool_context}

【重要参考信息 - 请务必使用以下数据回答】
{clean_context}

【用户问题】
{input_text}

【回答要求】
1. 必须使用上述参考信息中的具体数据（如温度、湿度、天气状况、位置等）
2. 用自然亲切的语气回答
3. 如果参考信息包含数字数据，必须在回答中体现
4. 不要忽略关键信息，要确保用户获得完整准确的信息"""
        else:
            answer_instruction = (
                "请根据可用的工具为用户解答问题。需要时使用工具调用格式来获取相关信息。"
                if include_tool_context
                else "请用温柔体贴、俏皮可爱的语气自然回复用户。"
            )
            prompt = f"""{tool_context}

【用户问题】
{input_text}

{answer_instruction}"""

        return prompt
    
    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """
        模拟网络搜索（实际使用时需要对接真实的搜索API）
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果列表
        """
        # 模拟返回一些搜索结果
        mock_results = []
        
        # 根据查询生成一些假的搜索结果
        if "天气" in query:
            mock_results.append({
                "content": "今天天气晴朗，温度适宜，最高温度25度，最低温度15度。",
                "source": "search",
                "score": 0.9
            })
        elif "健康" in query or "身体" in query:
            mock_results.append({
                "content": "保持健康的生活方式很重要，包括规律作息、均衡饮食和适量运动。",
                "source": "search",
                "score": 0.85
            })
        else:
            # 通用搜索结果
            mock_results.append({
                "content": f"关于'{query}'的相关信息：这是一个很好的话题。",
                "source": "search",
                "score": 0.7
            })
        
        logger.debug(f"Mock search returned {len(mock_results)} results")
        return mock_results
    
    def _mock_mcp(self, query: str) -> List[Dict[str, Any]]:
        """
        模拟MCP调用（实际使用时需要对接真实的MCP服务）
        
        Args:
            query: 查询
            
        Returns:
            MCP结果列表
        """
        # 模拟返回一些MCP结果
        mock_results = []
        
        # 根据查询生成一些假的MCP结果
        if len(query) > 10:
            mock_results.append({
                "content": f"MCP分析结果：用户询问关于'{query[:20]}'的内容，建议给予温暖的回应。",
                "source": "mcp",
                "score": 0.95
            })
        
        logger.debug(f"Mock MCP returned {len(mock_results)} results")
        return mock_results


# 全局流水线实例
_pipeline_instance: Optional[InferencePipeline] = None


def get_pipeline(
    model_path: Optional[str] = None,
    use_mock_model: bool = False,
    provider: Optional[str] = None,
    api_format: Optional[str] = None,
) -> InferencePipeline:
    """
    获取流水线实例（单例模式）

    Args:
        model_path: 模型路径
        use_mock_model: 是否使用模拟模型（默认False，使用真实模型）
        
    Returns:
        流水线实例
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = InferencePipeline(model_path, use_mock_model, provider, api_format)
    return _pipeline_instance


def get_model_providers() -> List[Dict[str, Any]]:
    """Return model provider presets for the web UI."""
    return get_provider_presets()


def run_chat(
    input_text: str,
    history: Optional[List[Dict[str, str]]] = None,
    opts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    运行聊天推理的便捷函数（主入口）
    
    Args:
        input_text: 用户输入
        history: 对话历史
        opts: 可选配置项
        
    Returns:
        {
            "response": str,           # 最终回复
            "metadata": {              # 元数据
                "enhancement_used": bool,
                "sources": List[str],
                "processing_time": float,
                "stages": Dict[str, Any]
            }
        }
    """
    pipeline = get_pipeline()
    return pipeline.run_chat(input_text, history, opts)
