# 虚拟女友数据集生成器 - 架构文档

## 概述

本项目采用模块化架构设计，将场景定义、生成逻辑和主入口分离，支持结构化的对话场景管理和灵活的数据集生成方式。

## 项目结构

```
my_virtualgirlfriend/
├── README.md                      # 项目总体说明
├── main.py                        # 应用统一入口
├── requirements.txt               # Python依赖
├── models/                        # 大模型文件存放
├── data/                          # 数据集存放
│   ├── train/                     # 训练数据集
│   ├── validation/                # 验证数据集
│   ├── role/                      # 角色人设定义文件
│   └── README.md
├── scripts/                       # 自动化脚本
│   ├── generate_dataset.py        # 数据集生成脚本
│   ├── train.py                   # 训练脚本
│   ├── fine_tune.py               # 全参数微调
│   ├── lora_train.py              # LoRA微调
│   └── README.md
├── web/                           # Web UI
│   ├── app.py                     # Flask应用
│   └── README.md
├── src/                           # 核心业务代码
│   ├── config.py                  # 配置文件
│   ├── scenarios.py               # 场景定义
│   ├── generator.py               # 数据集生成器
│   └── variation_engine.py        # 变化引擎
├── tests/                         # 测试代码
└── docs/                          # 项目文档
    ├── ARCHITECTURE.md            # 本文档
    ├── README_VARIATION_ENGINE.md # 变化引擎文档
    └── QC_PIPELINE_SUMMARY.md     # 质量控制文档
```

## 核心模块说明

### 1. src/scenarios.py - 场景目录模块

**路径**: `src/scenarios.py`  
**功能**: 定义所有对话场景的结构化数据

#### Scenario 类
```python
class Scenario:
    name: str                    # 场景唯一标识
    instruction: str             # 规范化指令文本
    input: str                   # 用户输入示例（可为空）
    response_templates: List[str] # 响应模板列表
    category: str                # 主分类
    tags: List[str]              # 标签列表
```

#### 场景目录 (SCENARIO_CATALOG)
- **总场景数**: 71个（超过要求的50个）
- **分类数**: 18个
- **标签数**: 120个

#### 场景分类

1. **greetings** - 问候场景
   - 早上/下午/晚上问候
   - 刚醒来/晚安/加班等

2. **emotional_care** - 情感关怀
   - 心情低落、焦虑、压力、孤独、挫折、愤怒
   - 思念表达

3. **encouragement** - 鼓励支持
   - 面对困难、考试前紧张、新挑战

4. **life_care** - 生活关怀
   - 提醒吃饭、喝水、运动、睡觉、休息

5. **health_care** - 健康关心
   - 生病、熬夜、头疼、眼睛累

6. **weather_care** - 天气关怀
   - 下雨、炎热、寒冷、大风

7. **daily_chat** - 日常聊天
   - 分享好心情、感到无聊、询问对方

8. **praise** - 称赞夸奖
   - 完成任务、夸奖女友、赞美用户

9. **hobbies** - 兴趣爱好
   - 游戏、动漫、音乐、电影、阅读、烹饪、运动

10. **food** - 美食相关
    - 分享美食、饿了、讨论喜好

11. **love** - 爱意表达
    - 表达爱意、想要拥抱、想要亲亲

12. **acting_cute** - 撒娇卖萌
    - 想要关注、撒娇卖萌

13. **work_study** - 工作学习
    - 学习中、工作压力、开会

14. **festivals** - 节日祝福
    - 生日、新年、情人节、圣诞节、中秋节

15. **conflict_resolution** - 冲突解决
    - 道歉、和解、感到内疚

16. **future_planning** - 未来规划
    - 讨论梦想、旅行计划、约会提议、未来展望

17. **roleplay** - 角色扮演
    - 医生、老师等角色

18. **seasonal_care** - 季节关怀
    - 春夏秋冬四季关怀

#### 关键函数

- `validate_catalog()`: 验证场景目录完整性和唯一性
- `get_scenario_by_name(name)`: 根据名称获取场景
- `get_scenarios_by_category(category)`: 根据分类获取场景列表
- `get_scenarios_by_tag(tag)`: 根据标签获取场景列表
- `get_all_categories()`: 获取所有分类
- `get_all_tags()`: 获取所有标签
- `get_catalog_metadata()`: 获取场景目录元数据

#### 验证机制

场景目录包含以下验证：
- ✅ 场景数量 ≥ 50
- ✅ 场景名称唯一性
- ✅ 指令文本唯一性
- ✅ 每个场景包含完整字段
- ✅ 每个场景至少有一个响应模板

### 2. src/generator.py - 生成器模块

**路径**: `src/generator.py`  
**功能**: 提供数据集生成的核心逻辑

#### GirlfriendDatasetGenerator 类

##### 生成模式

1. **确定性生成** (deterministic)
   ```python
   generate_deterministic_dataset(variations_per_scenario=1)
   ```
   - 按场景顺序生成
   - 适合验证和测试
   - 每个场景生成指定数量的变体

2. **随机生成** (random)
   ```python
   generate_random_dataset(num_samples=500, seed=None)
   ```
   - 随机选择场景和响应
   - 适合生成多样化数据集
   - 支持随机种子以复现

3. **平衡生成** (balanced)
   ```python
   generate_balanced_dataset(samples_per_scenario=10)
   ```
   - 每个场景生成相同数量样本
   - 保证场景覆盖均衡

##### 主要方法

- `generate_single_entry()`: 从单个场景生成一条数据
- `generate_dataset_with_metadata()`: 生成带元数据的数据集
- `save_dataset()`: 保存数据集到JSON文件
- `get_statistics()`: 获取数据集统计信息
- `print_sample_data()`: 打印示例数据

##### 统计信息

生成器可提供以下统计：
- 总样本数
- 唯一指令数
- 指令分布
- Emoji覆盖率
- 空输入比例
- 平均输出长度

### 3. scripts/generate_dataset.py - 数据集生成脚本

**路径**: `scripts/generate_dataset.py`  
**功能**: 提供命令行入口，整合场景和生成器模块

#### 主要流程

1. 解析命令行参数
2. 创建生成器实例
3. 显示场景目录信息
4. 验证场景数量 (≥50)
5. 生成数据集（支持变化引擎）
6. 质量控制（去重、验证）
7. 保存到文件（data/train/目录）
8. 显示统计信息和示例数据

#### 使用方式

```bash
# 默认生成500条数据
python scripts/generate_dataset.py

# 生成1000条数据
python scripts/generate_dataset.py --dataset-size 1000

# 查看所有选项
python scripts/generate_dataset.py --help
```

## 数据格式

### 输出格式

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

## 女友角色设定 (Persona)

所有响应模板都遵循以下角色设定：

1. **温柔体贴** (Gentle and caring)
   - 关心用户的健康和心情
   - 给予温暖的支持和鼓励

2. **俏皮可爱** (Playful and cute)
   - 使用可爱的语气词：呀、啦、哦、呢、嘛
   - 适时撒娇和卖萌

3. **阳光开朗** (Sunny and cheerful)
   - 积极乐观的态度
   - 传递正能量

4. **Emoji和语气词**
   - 98%+ 的响应包含emoji
   - 自然融入中文语气词
   - 表达丰富的情感

## 扩展指南

### 添加新场景

在 `src/scenarios.py` 中添加新的 `Scenario` 对象到 `SCENARIO_CATALOG`：

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

### 添加新分类

1. 在场景中使用新的 `category` 值
2. 自动被 `get_all_categories()` 识别
3. 可通过 `get_scenarios_by_category()` 查询

### 添加新标签

1. 在场景中添加新的标签到 `tags` 列表
2. 自动被 `get_all_tags()` 识别
3. 可通过 `get_scenarios_by_tag()` 查询

## 测试

### 运行场景验证

```bash
python -c "import sys; sys.path.insert(0, 'src'); from scenarios import validate_catalog; validate_catalog()"
```

验证结果：
- ✅ 场景数量 ≥ 50
- ✅ 场景名称唯一
- ✅ 指令唯一
- ✅ 字段完整性

### 运行测试套件

```bash
# 运行接受标准测试
python tests/test_acceptance_criteria.py

# 运行变化引擎测试
python tests/test_variation_engine.py
```

### 运行完整数据集生成

```bash
python scripts/generate_dataset.py
```

## API使用示例

### 基本使用

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from generator import GirlfriendDatasetGenerator

# 创建生成器
generator = GirlfriendDatasetGenerator()

# 生成500条随机数据
dataset = generator.generate_random_dataset(num_samples=500)

# 保存数据集
output_file = generator.save_dataset(dataset)
```

### 确定性生成

```python
# 每个场景生成一次
dataset = generator.generate_deterministic_dataset(variations_per_scenario=1)

# 每个场景生成5个变体
dataset = generator.generate_deterministic_dataset(variations_per_scenario=5)
```

### 平衡生成

```python
# 每个场景生成10条数据
dataset = generator.generate_balanced_dataset(samples_per_scenario=10)
```

### 按分类生成

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scenarios import get_scenarios_by_category
from generator import GirlfriendDatasetGenerator

# 只生成问候场景的数据集
greeting_scenarios = get_scenarios_by_category("greetings")
generator = GirlfriendDatasetGenerator(scenarios=greeting_scenarios)
dataset = generator.generate_random_dataset(num_samples=100)
```

### 按标签生成

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scenarios import get_scenarios_by_tag
from generator import GirlfriendDatasetGenerator

# 只生成包含"love"标签的场景
love_scenarios = get_scenarios_by_tag("love")
generator = GirlfriendDatasetGenerator(scenarios=love_scenarios)
dataset = generator.generate_random_dataset(num_samples=100)
```

### 获取统计信息

```python
# 生成数据集
dataset = generator.generate_random_dataset(num_samples=500)

# 获取统计
stats = generator.get_statistics(dataset)
print(f"总样本数: {stats['total_samples']}")
print(f"唯一指令数: {stats['unique_instructions']}")
print(f"Emoji覆盖率: {stats['emoji_coverage']}")
```

## 性能考虑

- **内存占用**: 所有场景加载到内存，约 100KB
- **生成速度**: 500条数据生成时间 < 1秒
- **文件大小**: 500条数据约 75-85KB (JSON格式)

## 验收标准

✅ **场景数量**: 71个场景（超过要求的50个）
✅ **唯一指令**: 每个场景有唯一的instruction字符串
✅ **元数据访问**: 可通过编程方式访问场景名称、分类、标签
✅ **确定性枚举**: 支持确定性遍历所有场景
✅ **Persona一致性**: 所有响应模板包含emoji和温柔语气
✅ **模块化结构**: 场景定义和生成逻辑分离
✅ **验证机制**: 内置验证保证目录质量

## 未来扩展建议

1. **多语言支持**: 添加英文、日文等其他语言场景
2. **动态场景**: 支持从配置文件或数据库加载场景
3. **场景组合**: 支持多轮对话场景的生成
4. **情感标注**: 为每个场景添加情感强度标注
5. **质量评估**: 添加生成数据的自动质量评估
6. **Web界面**: 提供可视化的场景管理和生成界面
7. **A/B测试**: 支持不同响应模板的效果对比
8. **用户反馈**: 集成用户反馈来优化响应模板

## 许可证

请参考项目根目录的许可证文件。

## 贡献指南

欢迎贡献新的场景！请确保：
1. 场景名称唯一
2. 指令文本唯一
3. 响应模板符合女友persona
4. 包含至少一个emoji
5. 添加适当的分类和标签
6. 通过测试验证：`python tests/test_acceptance_criteria.py`
