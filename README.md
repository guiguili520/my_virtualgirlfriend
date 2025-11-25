# 虚拟AI女友 (Virtual AI Girlfriend)

虚拟AI 二次元女友聊天数据集生成器

## 📝 项目简介

本项目提供一个完整的虚拟女友聊天数据集生成系统，用于训练具有温柔体贴、俏皮可爱人设的AI对话模型。

## ✨ 核心特性

- 🎯 **71个独特场景**：涵盖18个分类，超过350个精心设计的响应模板
- 💕 **人设一致性**：温柔体贴、俏皮可爱、阳光开朗的二次元女友人设
- 🚀 **智能变化引擎**：自动生成8-10个风格一致但措辞不同的变体
- 🛡️ **严格质量控制**：自动去重、长度验证、表情验证、人设检查
- 🔧 **灵活配置**：支持CLI参数配置变体数量、质量阈值、场景过滤等
- 📊 **高质量输出**：98%+表情覆盖率，100%人设一致性
- 🌐 **Web聊天界面**：基于Flask的二次元风格聊天界面，支持文本、图片、历史记录
- 🧠 **智能推理流水线**：集成搜索增强、MCP支持、多源信息整合、自动人格化处理
- 🔌 **MCP服务集成**：多服务内容提供者，支持天气、新闻等外部知识源增强

## 🚀 快速开始

### 安装要求

- Python 3.6+
- 数据集生成：仅使用标准库，无需安装额外依赖
- 模型训练（可选）：见 `requirements.txt`

```bash
# 安装所有依赖（用于模型训练）
pip install -r requirements.txt
```

### 启动应用

```bash
# 查看欢迎页面和可用功能
python main.py

# 启动 Web 聊天界面
./start_web.sh
# 或
python web/app.py
# 访问 http://localhost:5555
```

### 生成数据集

```bash
# 默认配置生成500条数据
python scripts/generate_dataset.py

# 生成1000条数据，每个场景10个变体
python scripts/generate_dataset.py --dataset-size 1000

# 使用固定种子确保可重现性（TODO: 需要添加seed参数）
# python scripts/generate_dataset.py --seed 42

# 更多选项请查看文档
python scripts/generate_dataset.py --help
```

### 使用推理流水线

```bash
# 运行推理流水线演示
python demo_inference_pipeline.py

# 在代码中使用
from inference import run_chat

# 简单对话
result = run_chat("你好呀~")
print(result["response"])

# 带增强的查询
result = run_chat("今天天气怎么样？", opts={"enable_enhancement": True})
print(result["response"])

# 查看完整文档
# 详见 docs/INFERENCE_PIPELINE_README.md
```

### 输出示例

生成的数据集保存在 `data/train/girlfriend_chat_dataset_<timestamp>.json`

```json
{
  "instruction": "早上问候",
  "input": "早上好",
  "output": "早安呀！☀️ 今天也要元气满满哦！我会一直陪在你身边的~"
}
```

## 📋 场景分类

数据集包含 **71个独特场景**，分为 **18个主要分类**：

| 分类 | 场景数 | 描述 |
|------|--------|------|
| 问候场景 | 6 | 早晚问候、睡醒、加班 |
| 情感关怀 | 7 | 低落、焦虑、压力、孤独、挫折、愤怒、思念 |
| 鼓励支持 | 3 | 困难、考试紧张、新挑战 |
| 生活关怀 | 5 | 吃饭、喝水、运动、睡觉、休息 |
| 健康关心 | 4 | 生病、熬夜、头疼、眼睛累 |
| 天气关怀 | 4 | 下雨、炎热、寒冷、大风 |
| 日常聊天 | 3 | 好心情、无聊、询问对方 |
| 称赞夸奖 | 3 | 任务完成、夸女友、赞美用户 |
| 兴趣爱好 | 7 | 游戏、动漫、音乐、电影、读书、烹饪、运动 |
| 美食相关 | 3 | 美食分享、饿了、食物偏好 |
| 爱意表达 | 3 | 表白、拥抱、亲亲 |
| 撒娇卖萌 | 2 | 想要关注、撒娇 |
| 工作学习 | 3 | 学习、工作压力、开会 |
| 节日祝福 | 5 | 生日、新年、情人节、圣诞、中秋 |
| 冲突解决 | 3 | 道歉、和解、内疚 |
| 未来规划 | 4 | 梦想、旅行、约会、未来 |
| 角色扮演 | 2 | 医生、老师 |
| 季节关怀 | 4 | 春夏秋冬四季关怀 |

## 🔄 变化引擎

变化引擎使用7种智能策略生成多样化变体：

1. **同义词替换**：替换关键词汇（加油→努力/坚持/冲鸭）
2. **表情符号变化**：根据情感基调替换表情
3. **语气词添加**：添加亲切语气词（呀、啦、呢、哦）
4. **占位符填充**：动态内容替换（宝贝、亲爱的等）
5. **句子重排**：调整句子顺序
6. **前缀后缀**：添加支持性语句
7. **组合策略**：综合运用多种策略

## 🛡️ 质量控制

严格的5步质量控制管道：

1. **表情验证** - 确保包含表情符号，不符合则自动注入
2. **长度验证** - 检查长度范围（15-200字符）
3. **精确去重** - 移除完全相同的条目
4. **相似度去重** - 使用SequenceMatcher算法，阈值0.90
5. **人设验证** - 验证积极词汇和语气一致性

**质量指标**：
- ✅ 唯一性：100%
- ✅ 表情覆盖率：98%+
- ✅ 长度合规率：100%
- ✅ 人设一致性：100%

## 📚 详细文档

### 使用文档
- [data/README.md](data/README.md) - 数据集说明和使用指南
- [models/README.md](models/README.md) - 模型文件说明
- [scripts/README.md](scripts/README.md) - 脚本使用说明
- [web/README.md](web/README.md) - Web聊天界面完整文档

### 技术文档
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计文档
- [docs/README_VARIATION_ENGINE.md](docs/README_VARIATION_ENGINE.md) - 变化引擎详细文档
- [docs/QC_PIPELINE_SUMMARY.md](docs/QC_PIPELINE_SUMMARY.md) - 质量控制管道说明

## 🎯 使用场景

- **大语言模型微调**：训练GPT、LLaMA、ChatGLM等模型
- **对话系统开发**：构建虚拟女友聊天机器人
- **Web聊天应用**：开箱即用的聊天界面，支持文本和图片
- **研究和学习**：对话生成、情感计算、人设一致性研究
- **产品原型开发**：快速验证对话产品想法

## 💕 人设特征

- **温柔体贴**：关心对方身体和情绪，主动提醒关怀
- **俏皮可爱**：适当撒娇卖萌，使用可爱语气词
- **阳光开朗**：积极正面态度，总是鼓励和支持
- **善解人意**：理解情绪压力，提供情感支持

## 🛠️ 项目结构

```
my_virtualgirlfriend/
├── README.md                      # 项目总体说明
├── requirements.txt               # Python 依赖
├── main.py                        # 应用启动文件
│
├── models/                        # 🤖 大模型文件存放
│   ├── .gitkeep                   # 占位符
│   └── README.md                  # 模型说明
│
├── data/                          # 📊 数据集存放
│   ├── train/                     # 训练集
│   │   └── girlfriend_chat_dataset_*.json
│   ├── validation/                # 验证集
│   │   └── girlfriend_chat_validation_*.json
│   └── README.md                  # 数据说明
│
├── scripts/                       # 🔧 自动化脚本
│   ├── generate_dataset.py        # 数据生成脚本
│   ├── train.py                   # 训练脚本（预留）
│   ├── fine_tune.py               # 全参数微调
│   ├── lora_train.py              # LoRA 微调
│   └── README.md                  # 脚本说明
│
├── web/                           # 🌐 Web UI
│   ├── app.py                     # Flask 应用（预留）
│   ├── static/                    # 静态文件（预留）
│   ├── templates/                 # HTML 模板（预留）
│   └── README.md                  # Web 说明
│
├── src/                           # 📚 核心业务代码
│   ├── __init__.py
│   ├── config.py                  # 配置文件
│   ├── scenarios.py               # 71个场景定义
│   ├── variation_engine.py        # 变化引擎核心
│   ├── generator.py               # 数据集生成器
│   ├── models/                    # 模型定义
│   └── utils/                     # 工具函数
│
├── tests/                         # ✅ 测试代码
│   ├── __init__.py
│   ├── test_acceptance_criteria.py
│   ├── test_variation_engine.py
│   └── test_run.py
│
└── docs/                          # 📖 项目文档
    ├── ARCHITECTURE.md            # 架构设计
    ├── README_VARIATION_ENGINE.md # 变化引擎
    └── QC_PIPELINE_SUMMARY.md     # 质量控制
```

## 📊 数据集统计

- **总场景数**：71个独特场景
- **分类数**：18个主要分类
- **标签数**：120+个描述性标签
- **响应模板数**：350+个精心设计的模板
- **可生成条目数**：
  - 无变化引擎：350+条
  - 启用变化引擎(8个变体)：2800+条
  - 启用变化引擎(10个变体)：3500+条

## 🔧 命令行选项

### 数据集生成参数 (scripts/generate_dataset.py)

```bash
# 基本参数
--dataset-size N          # 生成N条数据（默认500）
--output-dir PATH         # 指定输出目录（默认data/train）
--output-prefix PREFIX    # 文件名前缀（默认girlfriend_chat_dataset）

# 质量控制参数
--min-length N            # 最小输出长度（默认15）
--max-length N            # 最大输出长度（默认200）
--similarity-threshold F  # 去重相似度阈值（默认0.65）
```

详细使用说明请参考：
- [data/README.md](data/README.md) - 数据集完整文档
- [scripts/README.md](scripts/README.md) - 脚本使用说明
- [docs/INFERENCE_PIPELINE_README.md](docs/INFERENCE_PIPELINE_README.md) - 推理流水线完整文档

## ⚠️ 注意事项

1. 生成的数据仅供学习和研究使用
2. 使用时请确保符合相关法律法规和平台规则
3. 建议根据实际需求对数据进行人工审核和筛选
4. 商业使用前请确认许可证条款

## 🤝 贡献

欢迎提交issue和pull request来改进项目！

贡献方向：
- 添加新的对话场景
- 改进响应模板质量
- 优化变化引擎策略
- 改进质量控制算法
- 完善文档说明

## 📄 许可证

本项目遵循项目仓库的许可证。

## 📊 更新日志

- **v3.0** (2024-11):
  - 🏗️ 重构为标准应用架构
  - 📁 清晰的目录结构（models/, data/, scripts/, web/, src/, tests/）
  - 🚀 新增 main.py 应用入口
  - ⚙️ 新增 src/config.py 配置管理
  - 📝 完善各模块 README 文档
  - 🌐 预留 Web UI 开发框架
  - 📦 新增 requirements.txt 依赖管理

- **v2.0** (2024):
  - 新增变化引擎，支持自动生成变体
  - 场景数量从27个扩展到71个
  - 新增18个场景分类
  - 完善质量控制管道
  - 添加CLI参数支持
  - 新增场景过滤功能

- **v1.0** (2024):
  - 初始版本
  - 27个基础场景
  - 基础质量控制

---

💕 愿这个项目能帮助你创建一个温暖的虚拟女友！如有问题或建议，欢迎通过Issue反馈。
