# 推理流水线文档
# Inference Pipeline Documentation

## 概述 / Overview

推理流水线是虚拟女友项目的核心推理引擎，提供完整的对话生成流程，包括：
- 智能增强决策
- 网络搜索和MCP集成
- 多源信息整合（排序、去重、摘要）
- 人格化处理
- 结构化日志记录

The inference pipeline is the core inference engine of the Virtual Girlfriend project, providing a complete dialogue generation process.

## 架构 / Architecture

```
用户输入 (User Input)
    ↓
[决策模块] Decision Logic
    ↓
[增强模块] Enhancement (Optional)
    ├─ 网络搜索 (Search)
    ├─ MCP调用 (MCP)
    ├─ 排序 (Ranking)
    ├─ 去重 (Deduplication)
    └─ 摘要 (Summarization)
    ↓
[提示词构建] Prompt Building
    ↓
[模型推理] Model Inference
    ↓
[人格化处理] Persona Enhancement
    ↓
最终回复 (Final Response)
```

## 目录结构 / Directory Structure

```
src/
├── inference/              # 推理模块
│   ├── __init__.py        # 导出接口
│   └── pipeline.py        # 主流水线逻辑
├── enhance/               # 增强模块
│   ├── __init__.py
│   ├── ranker.py         # 结果排序
│   ├── deduplicator.py   # 去重
│   ├── summarizer.py     # 摘要生成
│   └── persona_helper.py # 人格化助手
└── config.py             # 配置文件（包含增强配置）
```

## 快速开始 / Quick Start

### 基本使用

```python
from inference import run_chat

# 简单对话
result = run_chat("你好呀~")
print(result["response"])  # 女友的回复

# 带对话历史
history = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好呀~ 😊"}
]
result = run_chat("今天天气真好", history=history)
print(result["response"])

# 自定义选项
opts = {
    "enable_enhancement": True,  # 启用增强
}
result = run_chat("今天天气怎么样？", opts=opts)
```

### 运行演示

```bash
# 运行完整演示
python demo_inference_pipeline.py

# 运行测试
python tests/test_inference_pipeline.py
python tests/test_enhance_modules.py
```

## 核心功能 / Core Features

### 1. 智能增强决策

自动判断是否需要增强处理：
- **长度检查**: 查询长度 ≥ 10 字符
- **关键词匹配**: 包含疑问词（什么、怎么、为什么等）
- **问句检测**: 包含问号或语气词（吗、呢、么）

```python
# 触发增强的例子
"今天的天气怎么样？"      # 包含关键词 + 问句
"告诉我关于健康的建议"    # 包含关键词 + 足够长

# 不触发增强的例子
"你好"                    # 太短
"我很开心"                # 普通陈述
```

### 2. 增强流程

当决定增强时，系统会：

#### 2.1 数据获取
- **网络搜索**: 调用搜索API（目前为模拟）
- **MCP调用**: 调用MCP服务（目前为模拟）

#### 2.2 信息整合
- **排序 (Ranker)**: 根据来源、相关性、长度等因素综合评分
- **去重 (Deduplicator)**: 精确去重 + 相似度去重（阈值0.85）
- **摘要 (Summarizer)**: 生成简短摘要（最大200字符）

#### 2.3 提示词增强
```
[参考信息: {增强内容摘要}]

{用户输入}
```

### 3. 人格化处理

确保所有回复符合虚拟女友人设：

#### 特征
- 温柔体贴
- 俏皮可爱
- 阳光开朗
- 善解人意

#### 自动处理
- **表情符号**: 自动添加适当的emoji（概率80%）
- **语气词**: 确保使用呀、啦、呢、哦等语气词
- **语气软化**: 将生硬的表达替换为温柔的表达
- **上下文选择**: 根据内容选择合适的表情

```python
# 示例
输入: "这个不行"
输出: "这个不太好呢~ 😊"

输入: "你说错了"
输出: "可能有点小问题呢 💕"
```

### 4. 结构化日志

每次对话都会记录详细的元数据：

```python
{
    "response": "最终回复",
    "metadata": {
        "enhancement_used": True/False,      # 是否使用了增强
        "sources": ["search", "mcp"],       # 使用的数据源
        "processing_time": 0.123,           # 处理时间（秒）
        "stages": {                         # 各阶段详情
            "decision": {
                "need_enhancement": True
            },
            "enhancement": {
                "success": True,
                "sources": ["search", "mcp"],
                "context_length": 88
            },
            "generation": {
                "success": True,
                "raw_length": 20
            },
            "persona": {
                "success": True,
                "valid": True,
                "final_length": 25
            }
        }
    }
}
```

## 配置选项 / Configuration

在 `src/config.py` 中配置：

```python
# 推理增强配置
ENABLE_ENHANCEMENT = True                    # 全局开关
ENHANCEMENT_MIN_QUERY_LENGTH = 10           # 最小查询长度
ENHANCEMENT_KEYWORDS = [...]                # 触发关键词

# 网络搜索配置
ENABLE_NETWORK_SEARCH = True
SEARCH_MAX_RESULTS = 3
SEARCH_TIMEOUT = 5

# MCP配置
ENABLE_MCP = True
MCP_TIMEOUT = 3

# 增强模块配置
RANKING_TOP_K = 5                           # 保留前K个结果
DEDUP_SIMILARITY_THRESHOLD = 0.85           # 去重相似度阈值
SUMMARY_MAX_LENGTH = 200                    # 摘要最大长度
PERSONA_EMOJI_PROBABILITY = 0.8             # 表情符号概率
```

## API 参考 / API Reference

### run_chat()

主入口函数，执行完整的聊天推理流程。

```python
def run_chat(
    input_text: str,
    history: Optional[List[Dict[str, str]]] = None,
    opts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Args:
        input_text: 用户输入
        history: 对话历史 [{"role": "user", "content": "..."}, ...]
        opts: 可选配置
            - enable_enhancement: 是否启用增强
            - enable_search: 是否启用搜索
            - enable_mcp: 是否启用MCP
    
    Returns:
        {
            "response": str,        # 最终回复
            "metadata": {...}       # 元数据
        }
    """
```

### InferencePipeline 类

```python
# 获取单例实例
from inference import get_pipeline
pipeline = get_pipeline(use_mock_model=True)

# 直接调用
result = pipeline.run_chat("你好")
```

### 增强模块

```python
from enhance import Ranker, Deduplicator, Summarizer, PersonaHelper

# 排序器
ranker = Ranker(top_k=5)
ranked = ranker.rank_results(results, query="查询")

# 去重器
deduplicator = Deduplicator(similarity_threshold=0.85)
deduped = deduplicator.deduplicate(results)

# 摘要生成器
summarizer = Summarizer(max_length=200)
summary = summarizer.summarize(results, query="查询")

# 人格化助手
helper = PersonaHelper(emoji_probability=0.8)
enhanced_text = helper.apply_persona("你好")
is_valid = helper.validate_persona("你好呀~ 😊")
```

## 降级处理 / Fallback Mechanisms

系统在各个环节都有完善的降级处理：

1. **增强失败**: 降级为纯模型推理
2. **搜索失败**: 仅使用MCP或跳过增强
3. **MCP失败**: 仅使用搜索或跳过增强
4. **模型失败**: 返回预设的友好错误消息
5. **人格化失败**: 使用原始模型输出

所有失败都会被记录在日志中，但不会影响最终输出。

## 测试 / Testing

### 运行所有测试

```bash
# 增强模块测试
python tests/test_enhance_modules.py

# 推理流水线测试
python tests/test_inference_pipeline.py
```

### 测试覆盖

- ✅ 基本聊天功能
- ✅ 增强决策逻辑
- ✅ 带历史的多轮对话
- ✅ 人格化强制执行
- ✅ 降级处理
- ✅ 结构化日志
- ✅ 配置覆盖
- ✅ 排序、去重、摘要功能
- ✅ 人格化验证

## 性能 / Performance

- 非增强查询: < 10ms
- 增强查询: < 100ms（取决于搜索/MCP响应时间）
- 内存占用: < 100MB（使用mock模型）

## 扩展 / Extensions

### 添加新的数据源

```python
# 在 pipeline.py 中添加新的数据源方法
def _call_new_source(self, query: str) -> List[Dict[str, Any]]:
    # 实现数据源调用
    return results

# 在 _perform_enhancement 中集成
def _perform_enhancement(self, query: str):
    # ... existing code ...
    new_results = self._call_new_source(query)
    all_results.extend(new_results)
```

### 自定义排序策略

```python
# 继承 Ranker 并覆盖 _calculate_score
from enhance import Ranker

class CustomRanker(Ranker):
    def _calculate_score(self, result, query):
        # 自定义评分逻辑
        return custom_score
```

### 自定义人格化规则

```python
# 继承 PersonaHelper 并覆盖方法
from enhance import PersonaHelper

class CustomPersonaHelper(PersonaHelper):
    def apply_persona(self, text):
        # 自定义人格化逻辑
        return enhanced_text
```

## 常见问题 / FAQ

### Q: 如何禁用增强？
```python
result = run_chat("查询", opts={"enable_enhancement": False})
```

### Q: 如何只使用搜索不使用MCP？
在 `config.py` 中设置:
```python
ENABLE_MCP = False
```

### Q: 如何调整表情符号出现频率？
在 `config.py` 中调整:
```python
PERSONA_EMOJI_PROBABILITY = 0.5  # 50% 概率
```

### Q: 如何对接真实的搜索API？
替换 `pipeline.py` 中的 `_mock_search` 方法为真实的API调用。

### Q: 如何使用真实模型？
```python
from inference import get_pipeline
pipeline = get_pipeline(
    model_path="/path/to/model",
    use_mock_model=False
)
```

## 后续计划 / Roadmap

- [ ] 对接真实的搜索API
- [ ] 对接真实的MCP服务
- [ ] 支持流式输出
- [ ] 添加缓存机制
- [ ] 支持多语言
- [ ] 优化性能
- [ ] 添加更多人格化规则
- [ ] 支持自定义人设

## 贡献 / Contributing

欢迎提交问题和Pull Request！

## 许可 / License

遵循项目主许可证。
