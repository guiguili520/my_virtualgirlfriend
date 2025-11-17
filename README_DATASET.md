# 虚拟女友聊天数据集生成器

## 📝 项目说明

本项目提供了一个Python脚本，用于自动生成虚拟二次元女友的聊天数据集，适用于训练AI对话模型。

## ✨ 特性

- 🎯 自动生成500条高质量聊天数据
- 💕 符合二次元女友人设：温柔体贴、俏皮可爱、阳光开朗
- 🌸 **包含丰富的场景类型（71个不同场景，18个分类）**
- 😊 98%以上的回复包含emoji表情
- 🚀 **NEW! 变化引擎**：智能生成8-10个风格一致但措辞不同的变体
- 🔧 可配置变体数量、随机种子等参数
- 📊 JSON格式输出，易于解析和使用
- 🏗️ **模块化架构设计，易于扩展和维护**
- 🔍 **支持场景分类、标签管理和元数据查询**

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

数据集包含 **71个独特场景**，分为 **18个分类**：

### 1. 问候场景 (Greetings)
- 早上/下午/晚上问候
- 刚醒来、晚安
- 加班工作

### 2. 情感关怀 (Emotional Care)
- 心情低落、焦虑、压力
- 孤独、挫折、愤怒
- 表达思念

### 3. 鼓励支持 (Encouragement)
- 面对困难、考试前紧张
- 开始新挑战

### 4. 生活关怀 (Life Care)
- 提醒吃饭、喝水、运动
- 提醒睡觉、休息

### 5. 健康关心 (Health Care)
- 生病、熬夜、头疼
- 眼睛疲劳

### 6. 天气关怀 (Weather Care)
- 下雨、炎热、寒冷、大风

### 7. 日常聊天 (Daily Chat)
- 分享好心情、感到无聊
- 询问对方

### 8. 称赞夸奖 (Praise)
- 完成任务、夸奖女友
- 赞美用户

### 9. 兴趣爱好 (Hobbies)
- 游戏、动漫、音乐、电影
- 阅读、烹饪、运动

### 10. 美食相关 (Food)
- 分享美食、饿了
- 讨论喜好

### 11. 爱意表达 (Love & Affection)
- 表达爱意、想要拥抱
- 想要亲亲

### 12. 撒娇卖萌 (Acting Cute)
- 想要关注、撒娇卖萌

### 13. 工作学习 (Work & Study)
- 学习中、工作压力
- 开会

### 14. 节日祝福 (Festivals)
- 生日、新年、情人节
- 圣诞节、中秋节

### 15. 冲突解决 (Conflict Resolution)
- 道歉、和解、感到内疚

### 16. 未来规划 (Future Planning)
- 讨论梦想、旅行计划
- 约会提议、未来展望

### 17. 角色扮演 (Role-play)
- 医生、老师等角色

### 18. 季节关怀 (Seasonal Care)
- 春夏秋冬四季关怀

## 📊 数据集特点

### 1. 多样性
- **71个独特场景**，涵盖18个分类
- 每个场景有多个不同的回复变体
- 随机组合生成，避免过度重复
- **支持确定性生成**，可按场景顺序遍历

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

### 4. 结构化管理
- 场景分类清晰，易于检索
- 每个场景有唯一的名称和指令
- 支持按分类、标签查询场景
- 可编程访问元数据

## 🛠️ 技术细节

### 依赖项
- Python 3.6+
- 标准库：json, random, datetime, typing

无需安装额外的第三方库！

### 代码结构（模块化架构）
```
.
├── scenarios.py                    # 场景数据定义模块
│   ├── Scenario类                  # 场景数据结构
│   ├── SCENARIO_CATALOG           # 71个场景定义
│   ├── validate_catalog()         # 场景验证
│   └── 查询函数                    # 按分类、标签查询
│
├── generator.py                    # 数据集生成器模块
│   ├── GirlfriendDatasetGenerator # 生成器类
│   ├── generate_deterministic_dataset()  # 确定性生成
│   ├── generate_random_dataset()         # 随机生成
│   ├── generate_balanced_dataset()       # 平衡生成
│   └── get_statistics()                  # 统计信息
│
└── generate_girlfriend_dataset.py  # 主入口程序
    ├── 创建生成器
    ├── 验证场景数量
    ├── 生成数据集
    └── 保存文件
```

详细架构文档请参考：[ARCHITECTURE.md](ARCHITECTURE.md)

## 📈 数据集统计

- 总条数：500条（可配置）
- 场景数量：**71个独特场景**
- 分类数：**18个分类**
- 标签数：**120个标签**
- Emoji覆盖率：98%+
- 文件大小：约75-85KB
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

### 添加新场景

在 `scenarios.py` 的 `SCENARIO_CATALOG` 中添加新场景：

```python
Scenario(
    name="unique_scenario_name",           # 唯一标识
    instruction="场景描述",                 # 指令文本
    input_text="用户输入示例",              # 可为空字符串
    response_templates=[                   # 响应模板列表
        "响应1 💕",
        "响应2 ✨",
        "响应3 😊"
    ],
    category="category_name",              # 分类
    tags=["tag1", "tag2", "tag3"]         # 标签
)
```

### 按分类生成数据集

```python
from generator import GirlfriendDatasetGenerator
from scenarios import get_scenarios_by_category

# 只生成问候场景的数据
greeting_scenarios = get_scenarios_by_category("greetings")
generator = GirlfriendDatasetGenerator(scenarios=greeting_scenarios)
dataset = generator.generate_random_dataset(num_samples=100)
```

### 按标签生成数据集

```python
from scenarios import get_scenarios_by_tag

# 只生成包含"love"标签的场景
love_scenarios = get_scenarios_by_tag("love")
generator = GirlfriendDatasetGenerator(scenarios=love_scenarios)
dataset = generator.generate_random_dataset(num_samples=100)
```

### 确定性生成（用于测试）

```python
from generator import GirlfriendDatasetGenerator

generator = GirlfriendDatasetGenerator()
# 按场景顺序生成，每个场景生成一次
dataset = generator.generate_deterministic_dataset(variations_per_scenario=1)
```

### 平衡生成

```python
# 每个场景生成相同数量的样本
dataset = generator.generate_balanced_dataset(samples_per_scenario=10)
```

更多API使用示例请参考：[ARCHITECTURE.md](ARCHITECTURE.md)

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
