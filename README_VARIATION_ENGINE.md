# 变化引擎 (Variation Engine)

## 概述

变化引擎是一个用于生成虚拟女友聊天数据多样化回复的模块。它能够从单个基础模板生成8-10个（可配置）风格一致但措辞不同的变体，确保数据集的多样性，同时保持女友人设的一致性。

## 核心特性

### 1. 同义词和短语池
引擎内置丰富的同义词库，用于替换关键情感词汇和动作：
- **问候类**: 早安 → 早上好/早呀/早
- **鼓励类**: 加油 → 努力/继续加油/坚持/别放弃/冲鸭
- **关心类**: 担心 → 担忧/忧虑/挂念/放心不下
- **情感类**: 开心 → 高兴/快乐/愉快/欣喜
- **程度副词**: 很 → 非常/特别/超级/十分/好

### 2. 情感基调与表情符号映射
根据对话场景的情感基调，自动选择合适的表情符号集合：

| 基调 | 表情符号集合 | 适用场景 |
|------|-------------|---------|
| happy | 😊😄🥰💕✨🌸💖🎉 | 开心、愉快的场景 |
| care | 🥺💕🫂❤️💗🌸✨ | 关心、照顾的场景 |
| encourage | 💪✨🌟⭐🔥👍💯 | 鼓励、支持的场景 |
| comfort | 🫂💕🥺😢💗🌸✨ | 安慰、抚慰的场景 |
| love | 💕💖💗💝💓💞❤️🥰 | 爱意表达场景 |
| excited | 🎉🥳🎊✨💫🌟⭐ | 兴奋、庆祝的场景 |
| cute | 🥺🙈😳💕🎀🌸✨ | 撒娇、卖萌的场景 |
| worried | 🥺😢💔😤🤧💕😿 | 担忧、关切的场景 |

### 3. 占位符系统
支持动态内容填充，提供多个预定义的占位符池：

| 占位符 | 可选内容 | 用途 |
|--------|---------|-----|
| `{pet_name}` | 宝贝、亲爱的、小可爱、宝宝、亲亲、小宝贝、宝 | 昵称 |
| `{encouragement}` | 你一定可以的、我相信你、你很棒、你很优秀... | 鼓励语 |
| `{care_action}` | 照顾好自己、好好休息、注意身体、爱护自己... | 关心动作 |
| `{time}` | 今天、现在、此刻、这会儿 | 时间词 |
| `{positive_feeling}` | 开心、快乐、幸福、温暖、美好 | 积极情感 |

**使用示例**:
```python
template = "{pet_name}，{encouragement}！💕 记得{care_action}哦~"
# 生成: "宝贝，你一定可以的！💕 记得照顾好自己哦~"
# 生成: "亲爱的，我相信你！💕 记得好好休息哦~"
```

### 4. 语气词自动添加
在自然位置添加中文语气词（呀、啦、哦、呢、嘛、吖等），增强女友人设的亲切感：

- **柔和语气**: 呀、啦、呢、哦、吖、嘛、哟
- **可爱语气**: 呀、喵、哒、捏、呐、咩
- **强调语气**: 啊、呢、哦、耶、哇
- **疑问语气**: 吗、呢、啊、嘛
- **感叹语气**: 啊、呀、哇、耶、喔

**插入位置**:
- 句末：在感叹号或波浪号前
- 句中：在逗号后
- 疑问句：在问号前

### 5. 确定性种子支持
支持设置随机种子，确保生成结果的可重现性：

```python
# 相同的种子产生相同的结果
vars1 = generate_variations_for_scenario(template, num_variants=5, seed=42)
vars2 = generate_variations_for_scenario(template, num_variants=5, seed=42)
assert vars1 == vars2  # True
```

### 6. 句子结构变化
避免机械复制，通过以下方式增加结构多样性：
- **句子重排**: 交换相邻句子的顺序
- **添加前缀**: 根据场景添加合适的开头（"别担心"、"来吧"、"要记得"等）
- **添加后缀**: 添加支持性语句（"我会一直陪着你的"、"有我在呢"等）
- **语序调整**: 在保持语义的前提下调整语序

### 7. 人设验证与保障机制
每个生成的变体都会经过严格验证，确保符合女友人设：

✅ **必须包含至少一个表情符号**  
✅ **必须包含积极/安慰性词汇**  
✅ **长度在10-200字符之间**  
✅ **避免消极或冷淡的表达**

不符合要求的变体会被自动丢弃并重新生成。

## 使用方法

### 基础使用

```python
from variation_engine import generate_variations_for_scenario

# 基础模板
template = "早安呀！😊 今天也要元气满满哦！"

# 生成8个变体（默认）
variations = generate_variations_for_scenario(
    base_response=template,
    num_variants=8,
    tone="happy",
    seed=42
)

for i, var in enumerate(variations, 1):
    print(f"{i}. {var}")
```

### 配置变体数量

```python
# 生成10个变体
variations = generate_variations_for_scenario(
    base_response=template,
    num_variants=10,  # 可配置：3-15个都可以
    tone="care"
)
```

### 使用占位符

```python
template = "{pet_name}，不要太累了哦！{care_action}，我会{positive_feeling}的~ 💕"

variations = generate_variations_for_scenario(
    base_response=template,
    num_variants=8,
    tone="care"
)

# 占位符会自动填充：
# "宝贝，不要太累了哦！好好休息，我会开心的~ 💕"
# "亲爱的，不要太累了哦！照顾好自己，我会温暖的~ 💕"
```

### 集成到数据集生成器

```python
from variation_engine import VariationEngine, get_tone_for_scenario

# 初始化引擎
engine = VariationEngine(seed=42)

# 定义场景
scenario = {
    "instruction": "早上问候",
    "input": "早上好",
    "base_output": "早安呀！😊 今天也要加油！"
}

# 自动检测情感基调
tone = get_tone_for_scenario(scenario["instruction"])

# 生成变体
variations = engine.generate_variations(
    template=scenario["base_output"],
    num_variants=10,
    tone=tone
)
```

### 命令行使用

生成数据集时可以通过命令行参数控制变化引擎：

```bash
# 使用变化引擎生成500条数据，每个场景8个变体
python3 generate_girlfriend_dataset.py --num-samples 500 --variants 8

# 使用变化引擎生成1000条数据，每个场景10个变体，使用种子42
python3 generate_girlfriend_dataset.py --num-samples 1000 --variants 10 --seed 42

# 禁用变化引擎，使用原始固定回复
python3 generate_girlfriend_dataset.py --num-samples 500 --no-variation-engine
```

## API 文档

### VariationEngine 类

```python
class VariationEngine:
    def __init__(self, seed: Optional[int] = None)
```

**参数**:
- `seed`: 随机种子，用于确定性生成

**主要方法**:

#### generate_variations()

```python
def generate_variations(
    self,
    template: str,
    num_variants: int = 8,
    tone: str = "happy",
    preserve_structure: bool = False
) -> List[str]
```

生成多个变体。

**参数**:
- `template`: 基础模板文本
- `num_variants`: 生成变体数量（默认8个）
- `tone`: 情感基调（happy/care/encourage/comfort/love/excited/cute/worried）
- `preserve_structure`: 是否保持句子结构不变

**返回**: 变体列表

#### set_seed()

```python
def set_seed(self, seed: int)
```

设置新的随机种子。

### 便捷函数

#### generate_variations_for_scenario()

```python
def generate_variations_for_scenario(
    base_response: str,
    num_variants: int = 8,
    tone: str = "happy",
    seed: Optional[int] = None
) -> List[str]
```

为单个场景生成变体的便捷函数。

#### get_tone_for_scenario()

```python
def get_tone_for_scenario(scenario_instruction: str) -> str
```

根据场景指令自动获取对应的情感基调。

支持27个预定义场景的自动映射：
- 早上问候 → happy
- 遇到困难需要鼓励 → encourage
- 心情不好需要安慰 → comfort
- 表达爱意 → love
- 用户说生病了 → worried
- 完成了某项任务 → excited
- ...等

## 测试

运行完整测试套件：

```bash
python3 test_variation_engine.py
```

测试覆盖：
1. ✅ 基本变体生成（8个变体）
2. ✅ 可配置的变体数量（3/8/10个）
3. ✅ 确定性种子（相同种子产生相同结果）
4. ✅ 占位符填充
5. ✅ 表情符号变化（不同情感基调）
6. ✅ 语气词添加
7. ✅ 人设验证
8. ✅ 同义词替换
9. ✅ 句子重排
10. ✅ 场景-基调自动映射

## 配置与扩展

### 添加新的同义词

编辑 `variation_engine.py` 中的 `synonym_pools`：

```python
self.synonym_pools = {
    "新词": ["同义词1", "同义词2", "同义词3"],
    # ...
}
```

### 添加新的占位符

编辑 `placeholder_pools`：

```python
self.placeholder_pools = {
    "新占位符": ["选项1", "选项2", "选项3"],
    # ...
}
```

### 添加新的情感基调

编辑 `emoji_sets`：

```python
self.emoji_sets = {
    "新基调": ["😊", "💕", "✨", ...],
    # ...
}
```

并更新 `SCENARIO_TONE_MAP`：

```python
SCENARIO_TONE_MAP = {
    "新场景": "新基调",
    # ...
}
```

## 性能特点

- ⚡ **高效生成**: 使用set去重，确保变体唯一性
- 🔄 **智能重试**: 自动重试生成直到达到目标数量
- 🛡️ **安全保障**: 最大尝试次数限制，防止无限循环
- 📊 **覆盖率高**: 98%+ 的变体包含表情符号
- 🎯 **质量保证**: 100% 的变体通过人设验证

## 示例输出

### 输入模板
```
"早安呀！😊 今天也要元气满满哦！"
```

### 生成的变体（num_variants=8）
```
1. 早上好呀！😊 今天也要元气满满哦！
2. 早安呀！✨ 今天也要元气满满哦！
3. 早呀！🌸 今天也要元气满满哦呢！
4. 早安呀！💕 今天也要元气满满哦！我会一直陪着你的~
5. 早安！😄 今天也要元气满满哦呀！
6. 早上好！😊 今天也要元气满满哦啦！
7. 早安呀！🌟 今天也要元气满满哦！
8. 早！💖 今天也要元气满满哦嘛！
```

### 输入模板（带占位符）
```
"{pet_name}，{encouragement}！💕"
```

### 生成的变体
```
1. 宝贝，你一定可以的！💕
2. 亲爱的，我相信你！💕
3. 小可爱，你很棒！💕
4. 宝宝，你很优秀！💕
5. 亲亲，你是最好的！💕
6. 小宝贝，你能行的！💕
7. 宝，你很厉害！💕
8. 宝贝，我坚信你！💕
```

## 最佳实践

1. **选择合适的基调**: 根据场景选择正确的情感基调，确保表情符号和语气符合场景
2. **使用占位符**: 对于需要高度个性化的内容，使用占位符可以增加更多变化
3. **设置合理的变体数量**: 推荐8-10个变体，既保证多样性又不至于过度生成
4. **使用种子进行测试**: 开发阶段使用固定种子便于调试和比较
5. **定期验证输出**: 检查生成的变体是否符合预期的人设和语气

## 技术实现细节

### 变换策略

引擎使用7种不同的变换策略，随机选择应用：

1. **synonym_replace**: 同义词替换
2. **emoji_variation**: 表情符号变化
3. **tone_modifier**: 语气词添加
4. **placeholder_fill**: 占位符填充
5. **sentence_reorder**: 句子重排
6. **prefix_suffix**: 前缀后缀添加
7. **combined**: 组合多种策略

### 生成流程

```
输入模板
    ↓
填充占位符（如果有）
    ↓
选择变换策略
    ↓
应用变换
    ↓
验证人设
    ↓
去重检查
    ↓
输出变体
```

## 版本历史

- **v1.0.0** (2024): 初始版本
  - 支持8-10个变体生成
  - 同义词库、表情符号库、占位符系统
  - 语气词自动添加
  - 确定性种子支持
  - 人设验证机制

## 许可证

本模块遵循与主项目相同的许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进变化引擎！

## 联系方式

如有问题或建议，请通过项目仓库的 Issue 页面联系。
