# 虚拟女友聊天数据集生成器

## 📝 项目说明

本项目提供了一个Python脚本，用于自动生成虚拟二次元女友的聊天数据集，适用于训练AI对话模型。

## ✨ 特性

- 🎯 自动生成500条高质量聊天数据
- 💕 符合二次元女友人设：温柔体贴、俏皮可爱、阳光开朗
- 🌸 包含丰富的场景类型（27+种不同场景）
- 😊 98%以上的回复包含emoji表情
- 🚀 **NEW! 变化引擎**：智能生成8-10个风格一致但措辞不同的变体
- 🔧 可配置变体数量、随机种子等参数
- 📊 JSON格式输出，易于解析和使用

## 🚀 使用方法

### 快速开始

```bash
# 生成500条数据，使用变化引擎，每个场景8个变体（默认）
python3 generate_girlfriend_dataset.py

# 生成1000条数据，每个场景10个变体
python3 generate_girlfriend_dataset.py --num-samples 1000 --variants 10

# 使用固定种子确保可重现性
python3 generate_girlfriend_dataset.py --seed 42

# 禁用变化引擎，使用原始固定回复
python3 generate_girlfriend_dataset.py --no-variation-engine
```

### 命令行选项

- `--num-samples N`: 生成N条数据（默认500）
- `--variants N`: 每个场景生成N个变体（默认8，仅在启用变化引擎时有效）
- `--seed N`: 设置随机种子，用于确定性生成
- `--no-variation-engine`: 禁用变化引擎，使用固定回复

### 输出位置

生成的数据集将保存在：
```
train_data/dataset/girlfriend_chat_dataset_<timestamp>.json
```

文件名包含时间戳，避免覆盖之前生成的数据。

## 📋 数据结构

每条数据包含三个字段：

```json
{
  "instruction": "对话场景/指令",
  "input": "用户输入（可为空）",
  "output": "女友的回复"
}
```

### 示例

```json
{
  "instruction": "早上问候",
  "input": "早上好",
  "output": "早安呀！☀️ 今天也要元气满满哦！我会一直陪在你身边的~"
}
```

## 🎭 场景类型

数据集包含以下场景类型：

### 日常问候
- 早上问候
- 晚上道别
- 日常聊天

### 情感支持
- 遇到困难需要鼓励
- 考试或面试前紧张
- 心情不好需要安慰
- 表达思念

### 生活关心
- 提醒吃饭
- 提醒喝水
- 天气关心（下雨、炎热、寒冷）
- 健康关心（生病、熬夜）

### 工作学习
- 学习中
- 工作压力大
- 很晚了还在工作

### 兴趣爱好
- 聊游戏
- 聊动漫
- 聊美食

### 其他
- 称赞夸奖
- 撒娇卖萌
- 表白/爱意表达
- 节日祝福

## 📊 数据集特点

### 1. 多样性
- 27种不同的对话场景
- **变化引擎**：每个场景可生成8-10个（可配置）不同的回复变体
- 同义词替换、语序调整、表情符号变化等多种技术确保多样性
- 随机组合生成，避免过度重复

### 2. 人设一致性
所有回复都保持以下特点：
- 温柔体贴的语气
- 俏皮可爱的表达
- 阳光开朗的态度
- 如冬天里的一抹暖阳
- **智能验证**：每个变体都经过人设检查，确保符合女友角色

### 3. 丰富的表情
- 98%以上的回复包含emoji
- 适当使用语气词（呀、啦、哦、呢等）
- 情感基调自动映射（happy/care/encourage/love等8种基调）
- 增强情感表达

### 4. 变化引擎特性 🆕
- **同义词库**：丰富的同义词和短语替换（50+词条）
- **占位符系统**：支持{pet_name}、{encouragement}等动态内容
- **语气词**：自动在自然位置添加语气词
- **句子重排**：避免机械复制，调整语序和结构
- **确定性生成**：支持随机种子，结果可重现

## 🛠️ 技术细节

### 依赖项
- Python 3.6+
- 标准库：json, random, datetime, typing

无需安装额外的第三方库！

### 代码结构
```
generate_girlfriend_dataset.py
├── generate_dataset()              # 主要生成逻辑
│   ├── 场景模板定义
│   ├── 变化引擎集成
│   ├── 随机组合
│   └── 数据生成
└── main()                         # 入口函数
    ├── 命令行参数解析
    ├── 调用生成器
    ├── 创建输出目录
    └── 保存JSON文件

variation_engine.py                 # 变化引擎模块
├── VariationEngine                # 核心引擎类
│   ├── generate_variations()      # 生成变体
│   ├── _replace_synonyms()        # 同义词替换
│   ├── _vary_emojis()             # 表情符号变化
│   ├── _add_tone_modifiers()      # 语气词添加
│   ├── _fill_placeholders()       # 占位符填充
│   └── _validate_variation()      # 人设验证
└── generate_variations_for_scenario() # 便捷函数
```

### 变化引擎详细文档

查看 [README_VARIATION_ENGINE.md](README_VARIATION_ENGINE.md) 了解变化引擎的完整文档和API说明。

## 📈 数据集统计

- 总条数：500条
- 场景类型：27种
- Emoji覆盖率：98%+
- 文件大小：约81KB
- 格式：UTF-8 编码的JSON

## 🎯 使用场景

本数据集适用于：

1. **微调大语言模型**
   - 训练特定人设的对话AI
   - 提升模型的情感表达能力

2. **对话系统开发**
   - 构建虚拟女友聊天机器人
   - 开发陪伴类应用

3. **研究和学习**
   - 研究对话生成
   - 学习prompt工程

## 📝 自定义和扩展

### 修改生成数量

使用命令行参数：

```bash
python3 generate_girlfriend_dataset.py --num-samples 1000
```

### 配置变体数量

```bash
# 每个场景生成10个变体
python3 generate_girlfriend_dataset.py --variants 10
```

### 添加新场景

在 `generate_girlfriend_dataset.py` 中添加新的场景模板：

```python
new_scenarios = [
    {
        "instruction": "你的新场景",
        "input": "用户输入",
        "outputs": [
            "基础回复1",  # 第一个回复会被用作变化引擎的模板
            "基础回复2",
            # ...
        ]
    }
]
```

或使用 `base_output` 字段：

```python
new_scenarios = [
    {
        "instruction": "你的新场景",
        "input": "用户输入",
        "base_output": "{pet_name}，{encouragement}！💕"  # 可使用占位符
    }
]
```

### 扩展变化引擎

编辑 `variation_engine.py` 添加新的同义词、占位符或表情符号集合。详见 [README_VARIATION_ENGINE.md](README_VARIATION_ENGINE.md)。

## 📄 许可证

本项目遵循项目主仓库的许可证。

## 🤝 贡献

欢迎提交issue和pull request来改进数据集质量！

## ⚠️ 注意事项

1. 生成的数据仅供学习和研究使用
2. 使用时请确保符合相关法律法规
3. 建议根据实际需求对数据进行人工审核和筛选

---

💕 愿这个数据集能帮助你创建一个温暖的虚拟女友！
