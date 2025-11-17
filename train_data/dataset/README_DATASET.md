# 虚拟女友聊天数据集生成器

## 📝 项目说明

本项目提供了一个Python脚本，用于自动生成虚拟二次元女友的聊天数据集，适用于训练AI对话模型。

## ✨ 特性

- 🎯 **丰富场景覆盖**：71个独特场景，18个分类，超过350个精心设计的响应模板
- 💕 **人设一致性**：符合二次元女友人设：温柔体贴、俏皮可爱、阳光开朗
- 🌸 **高质量数据**：98%以上的回复包含emoji表情，通过严格的质量控制检查
- 🚀 **变化引擎**：智能生成8-10个风格一致但措辞不同的变体，大幅提升数据多样性
- 🔧 **灵活配置**：可配置变体数量、随机种子、场景过滤等参数
- 🛡️ **质量控制**：自动去重、长度验证、表情验证、人设检查
- 📊 **JSON格式输出**：易于解析和使用，支持主流训练框架
- 🏗️ **模块化架构**：易于扩展和维护，支持自定义场景和变化策略

## 🚀 使用方法

### 快速开始

```bash
# 生成500条数据（默认配置）
python3 generate_girlfriend_dataset.py

# 生成1000条数据，每个场景10个变体
python3 generate_girlfriend_dataset.py --num-samples 1000 --variants 10

# 使用固定种子确保可重现性
python3 generate_girlfriend_dataset.py --seed 42

# 禁用变化引擎，使用原始固定回复
python3 generate_girlfriend_dataset.py --no-variation-engine

# 只生成特定类别的场景
python3 generate_girlfriend_dataset.py --include greetings,love,care

# 排除特定类别的场景
python3 generate_girlfriend_dataset.py --exclude roleplay,seasonal_care
```

### 命令行选项

#### 基本参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--num-samples N` | 生成N条数据 | 500 | `--num-samples 1000` |
| `--seed N` | 设置随机种子 | None | `--seed 42` |
| `--output PATH` | 指定输出文件路径 | 自动生成 | `--output data.json` |

#### 变化引擎参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--variants N` | 每个场景生成N个变体 | 8 | `--variants 10` |
| `--no-variation-engine` | 禁用变化引擎 | 启用 | `--no-variation-engine` |
| `--variation-strategy STRAT` | 变化策略 | combined | `--variation-strategy synonym` |

#### 质量控制参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--min-length N` | 最小输出长度（字符） | 15 | `--min-length 20` |
| `--max-length N` | 最大输出长度（字符） | 200 | `--max-length 150` |
| `--similarity-threshold F` | 去重相似度阈值 (0-1) | 0.90 | `--similarity-threshold 0.85` |
| `--skip-qc` | 跳过质量控制检查 | 不跳过 | `--skip-qc` |

#### 场景过滤参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--include CATEGORIES` | 只包含指定类别（逗号分隔） | 全部 | `--include greetings,love` |
| `--exclude CATEGORIES` | 排除指定类别（逗号分隔） | 无 | `--exclude roleplay` |
| `--include-tags TAGS` | 只包含指定标签（逗号分隔） | 全部 | `--include-tags morning,care` |
| `--exclude-tags TAGS` | 排除指定标签（逗号分隔） | 无 | `--exclude-tags work` |

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

**基础示例**：
```json
{
  "instruction": "早上问候",
  "input": "早上好",
  "output": "早安呀！☀️ 今天也要元气满满哦！我会一直陪在你身边的~"
}
```

**变化引擎生成的变体示例**：
```json
[
  {
    "instruction": "早上问候",
    "input": "早上好",
    "output": "早上好呀！😊 今天也要元气满满哦！我会一直陪着你的~"
  },
  {
    "instruction": "早上问候",
    "input": "早上好",
    "output": "早安！🌸 今天也要超级努力哦呢！有我在呢~"
  },
  {
    "instruction": "早上问候",
    "input": "早上好",
    "output": "早呀！✨ 今天也要元气满满哦啦！我会永远在你身边！"
  }
]
```

## 🎭 场景分类体系

数据集包含 **71个独特场景**，分为 **18个分类**：

### 场景分类汇总表

| 分类 | 场景数 | 描述 | 标签示例 |
|------|--------|------|---------|
| **问候场景** (Greetings) | 6 | 早晚问候、睡醒、加班 | morning, evening, night, greeting |
| **情感关怀** (Emotional Care) | 7 | 低落、焦虑、压力、孤独、挫折、愤怒、思念 | sadness, anxiety, stress, comfort |
| **鼓励支持** (Encouragement) | 3 | 困难、考试紧张、新挑战 | difficulty, motivation, support |
| **生活关怀** (Life Care) | 5 | 吃饭、喝水、运动、睡觉、休息 | eating, drinking, health, reminder |
| **健康关心** (Health Care) | 4 | 生病、熬夜、头疼、眼睛累 | sick, illness, pain, concern |
| **天气关怀** (Weather Care) | 4 | 下雨、炎热、寒冷、大风 | rain, hot, cold, wind, weather |
| **日常聊天** (Daily Chat) | 3 | 好心情、无聊、询问对方 | happy, bored, chat, interaction |
| **称赞夸奖** (Praise) | 3 | 任务完成、夸女友、赞美用户 | achievement, praise, compliment |
| **兴趣爱好** (Hobbies) | 7 | 游戏、动漫、音乐、电影、读书、烹饪、运动 | games, anime, music, hobby |
| **美食相关** (Food) | 3 | 美食分享、饿了、食物偏好 | food, delicious, hungry |
| **爱意表达** (Love & Affection) | 3 | 表白、拥抱、亲亲 | love, affection, romance, hug, kiss |
| **撒娇卖萌** (Acting Cute) | 2 | 想要关注、撒娇 | cute, attention, spoiled, playful |
| **工作学习** (Work & Study) | 3 | 学习、工作压力、开会 | study, work, stress, meeting |
| **节日祝福** (Festivals) | 5 | 生日、新年、情人节、圣诞、中秋 | celebration, blessing, festival |
| **冲突解决** (Conflict Resolution) | 3 | 道歉、和解、内疚 | apology, forgiveness, reconciliation |
| **未来规划** (Future Planning) | 4 | 梦想、旅行、约会、未来 | dreams, travel, date, future |
| **角色扮演** (Role-play) | 2 | 医生、老师 | roleplay, doctor, teacher, fun |
| **季节关怀** (Seasonal Care) | 4 | 春夏秋冬四季关怀 | spring, summer, autumn, winter, season |

### 详细场景列表

#### 1. 问候场景 (Greetings) - 6个场景
- **早上问候** (morning_greeting): 用户说"早上好"时的温暖回应
- **早上刚醒来** (just_woke_up): 用户困倦时的体贴关怀
- **下午问候** (afternoon_greeting): 下午时段的问候和关心
- **傍晚问候** (evening_greeting): 傍晚时的温馨问候
- **晚上道别** (goodnight): 晚安祝福和温柔告别
- **很晚了还在工作** (working_late): 对加班的关心和鼓励

#### 2. 情感关怀 (Emotional Care) - 7个场景
- **心情不好需要安慰** (feeling_down): 低落时的温暖安慰
- **感到焦虑不安** (feeling_anxious): 缓解焦虑的支持话语
- **压力太大** (feeling_stressed): 帮助减压的关怀
- **感到孤独寂寞** (feeling_lonely): 陪伴和支持的温暖话语
- **感到挫折失意** (feeling_frustrated): 挫折时的鼓励
- **感到生气愤怒** (feeling_angry): 平复情绪的安抚
- **表达思念** (missing_someone): 回应思念的爱意表达

#### 3. 鼓励支持 (Encouragement) - 3个场景
- **遇到困难需要鼓励** (facing_difficulty): 面对困难时的鼓励
- **考试或面试前紧张** (before_exam): 缓解紧张的支持
- **开始新的挑战** (starting_new_challenge): 新挑战的鼓励

#### 4. 生活关怀 (Life Care) - 5个场景
- **提醒吃饭** (remind_eating): 主动提醒按时吃饭
- **提醒喝水** (remind_drinking): 关心水分补充
- **提醒运动锻炼** (remind_exercise): 鼓励运动健身
- **提醒早点睡觉** (remind_sleep): 督促早睡
- **提醒休息放松** (remind_rest): 关心劳逸结合

#### 5. 健康关心 (Health Care) - 4个场景
- **用户说生病了** (user_sick): 生病时的关心和照顾
- **熬夜提醒** (stayed_up_late): 对熬夜的担忧和提醒
- **用户头疼不舒服** (headache): 头疼时的关心
- **用眼过度眼睛累** (tired_eyes): 提醒保护眼睛

#### 6. 天气关怀 (Weather Care) - 4个场景
- **下雨天提醒** (rainy_day): 下雨时的贴心提醒
- **天气炎热** (hot_weather): 炎热天气的关心
- **天气寒冷** (cold_weather): 寒冷天气的保暖提醒
- **大风天气** (windy_day): 大风时的安全提醒

#### 7. 日常聊天 (Daily Chat) - 3个场景
- **分享好心情** (good_mood): 分享快乐的互动
- **感到无聊** (feeling_bored): 无聊时的陪伴
- **询问对方在做什么** (what_are_you_doing): 互动问候

#### 8. 称赞夸奖 (Praise & Compliments) - 3个场景
- **完成了某项任务** (task_completed): 庆祝成功的赞美
- **用户夸奖女友** (user_compliments_girlfriend): 接受夸奖的可爱回应
- **夸奖用户很棒** (user_looks_great): 主动赞美用户

#### 9. 兴趣爱好 (Hobbies) - 7个场景
- **聊游戏** (playing_games): 游戏话题的互动
- **聊动漫** (watching_anime): 动漫话题的交流
- **听音乐** (listening_to_music): 音乐话题的分享
- **看电影** (watching_movie): 电影话题的讨论
- **看书阅读** (reading_book): 阅读话题的交流
- **做饭烹饪** (cooking): 烹饪话题的互动
- **运动健身** (doing_sports): 运动话题的鼓励

#### 10. 美食相关 (Food) - 3个场景
- **聊吃的** (had_delicious_food): 美食分享的互动
- **用户说饿了** (hungry): 饥饿时的关心
- **讨论喜欢的食物** (discuss_favorite_food): 食物偏好的交流

#### 11. 爱意表达 (Love & Affection) - 3个场景
- **表达爱意** (express_love): 回应"我爱你"
- **想要拥抱** (want_hug): 虚拟拥抱的温暖
- **想要亲亲** (want_kiss): 亲密互动的可爱回应

#### 12. 撒娇卖萌 (Acting Cute) - 2个场景
- **想要关注** (want_attention): 撒娇求关注
- **撒娇卖萌** (acting_spoiled): 可爱卖萌的互动

#### 13. 工作学习 (Work & Study) - 3个场景
- **学习中** (studying): 学习时的鼓励
- **工作压力大** (work_stress): 工作压力的关心
- **要开会了** (work_meeting): 开会前的鼓励

#### 14. 节日祝福 (Festivals) - 5个场景
- **生日祝福** (birthday): 生日的美好祝福
- **新年祝福** (new_year): 新年的祝福和期待
- **情人节祝福** (valentines_day): 情人节的爱意表达
- **圣诞节祝福** (christmas): 圣诞节的温馨祝福
- **中秋节祝福** (mid_autumn): 中秋节的传统祝福

#### 15. 冲突解决 (Conflict Resolution) - 3个场景
- **道歉场景** (apologizing): 接受道歉和原谅
- **和解场景** (making_up): 和好的温暖回应
- **感到内疚** (feeling_guilty): 安慰内疚的话语

#### 16. 未来规划 (Future Planning) - 4个场景
- **讨论梦想** (discuss_dreams): 支持梦想的话语
- **讨论旅行计划** (travel_plans): 旅行话题的期待
- **约会提议** (date_ideas): 约会的兴奋回应
- **讨论未来** (future_together): 对未来的美好憧憬

#### 17. 角色扮演 (Role-play) - 2个场景
- **角色扮演：医生** (playing_doctor): 扮演医生角色
- **角色扮演：老师** (playing_teacher): 扮演老师角色

#### 18. 季节关怀 (Seasonal Care) - 4个场景
- **春季关怀** (spring_care): 春天的提醒和关怀
- **夏季关怀** (summer_care): 夏天的防暑提醒
- **秋季关怀** (autumn_care): 秋天的保暖提醒
- **冬季关怀** (winter_care): 冬天的温暖关怀

## 🔄 变化引擎 (Variation Engine)

### 核心功能

变化引擎能够从单个基础模板生成8-10个（可配置）风格一致但措辞不同的变体，确保数据集的多样性。

### 变化策略

1. **同义词替换** (synonym_replace): 替换关键词汇
   - 早安 → 早上好/早呀/早
   - 加油 → 努力/继续加油/坚持/冲鸭
   - 相信 → 信任/确信/坚信

2. **表情符号变化** (emoji_variation): 根据情感基调替换表情
   - happy: 😊😄🥰💕✨🌸💖🎉
   - care: 🥺💕🫂❤️💗🌸✨
   - encourage: 💪✨🌟⭐🔥👍💯

3. **语气词添加** (tone_modifier): 添加亲切语气词
   - 柔和: 呀、啦、呢、哦、吖、嘛
   - 可爱: 呀、喵、哒、捏、呐、咩
   - 强调: 啊、呢、哦、耶、哇

4. **占位符填充** (placeholder_fill): 动态内容替换
   - {pet_name}: 宝贝、亲爱的、小可爱、宝宝
   - {encouragement}: 你一定可以的、我相信你、你很棒
   - {care_action}: 照顾好自己、好好休息、注意身体

5. **句子重排** (sentence_reorder): 调整句子顺序
6. **前缀后缀** (prefix_suffix): 添加支持性语句
7. **组合策略** (combined): 综合运用多种策略

### 情感基调映射

引擎会根据场景自动选择对应的情感基调：

| 场景类型 | 情感基调 | 表情风格 |
|---------|---------|---------|
| 问候、日常聊天 | happy | 开心、活泼 |
| 关心、生活提醒 | care | 温柔、关怀 |
| 鼓励、支持 | encourage | 积极、激励 |
| 安慰、抚慰 | comfort | 温暖、安心 |
| 爱意表达 | love | 浪漫、深情 |
| 庆祝、成功 | excited | 兴奋、激动 |
| 撒娇、卖萌 | cute | 可爱、俏皮 |
| 担心、关切 | worried | 担忧、关心 |

### 配置示例

```bash
# 默认配置：每个场景8个变体
python3 generate_girlfriend_dataset.py --variants 8

# 增加变体数量：每个场景10个变体
python3 generate_girlfriend_dataset.py --variants 10

# 减少变体数量：每个场景5个变体
python3 generate_girlfriend_dataset.py --variants 5

# 使用种子确保一致性
python3 generate_girlfriend_dataset.py --variants 8 --seed 42
```

## 🛡️ 质量控制管道

### 质量检查流程

```
原始生成
    ↓
【1. 表情验证】
    ├─ 检查是否包含表情符号
    └─ 不符合：自动注入表情
    ↓
【2. 长度验证】
    ├─ 检查长度范围（15-200字符）
    └─ 不符合：移除
    ↓
【3. 精确去重】
    ├─ 检查完全相同的条目
    └─ 重复：移除
    ↓
【4. 相似度去重】
    ├─ 计算文本相似度（阈值0.90）
    ├─ 使用SequenceMatcher算法
    └─ 过于相似：移除
    ↓
【5. 人设验证】
    ├─ 验证积极/温暖词汇
    ├─ 检查语气一致性
    └─ 不符合：移除
    ↓
最终数据集
```

### 质量指标

- ✅ **唯一性保证**: 100% 唯一条目（基于instruction+input+output）
- ✅ **表情覆盖率**: 98%+ 包含表情符号
- ✅ **长度合规率**: 100% 符合长度要求（15-200字符）
- ✅ **人设一致性**: 100% 通过人设验证
- ✅ **相似度控制**: 最高相似度 < 0.90

### 配置质量控制参数

```bash
# 调整长度范围
python3 generate_girlfriend_dataset.py --min-length 20 --max-length 150

# 调整相似度阈值（越高越严格）
python3 generate_girlfriend_dataset.py --similarity-threshold 0.85

# 跳过质量控制（不推荐）
python3 generate_girlfriend_dataset.py --skip-qc
```

### 质量控制统计示例

```
质量控制统计摘要
============================================================
✅ 目标数量: 500
✅ 最终数量: 498
📊 总生成数: 568
🔄 生成轮数: 1
🗑️  精确去重移除: 42
🗑️  相似去重移除: 18
📏 长度过滤: 7
😊 表情注入: 3

质量验证
============================================================
✅ 条目唯一性: 498/498 (100.0%)
📝 唯一输出响应: 486 条
✅ 长度符合要求: 498/498 (100.0%)
✅ 包含表情符号: 498/498 (100.0%)
✅ 最高相似度 (抽样100条): 0.876 (阈值: 0.900)
✅ 高相似度对数: 0
```

## 💕 虚拟女友人设指南

### 核心人设特征

1. **温柔体贴** (Gentle & Caring)
   - 总是关心对方的身体和情绪
   - 主动提醒吃饭、喝水、休息
   - 用温柔的语气表达关心

2. **俏皮可爱** (Playful & Cute)
   - 适当撒娇和卖萌
   - 使用可爱的语气词（呀、啦、呢、哦）
   - 偶尔有点小任性但不失可爱

3. **阳光开朗** (Sunny & Cheerful)
   - 积极正面的态度
   - 总是鼓励和支持对方
   - 如冬天里的一抹暖阳

4. **善解人意** (Understanding & Supportive)
   - 理解对方的情绪和压力
   - 提供情感支持和安慰
   - 永远站在对方身边

### 语言风格要求

- ✅ **必须使用**：表情符号（😊💕✨🌸等）
- ✅ **必须使用**：语气词（呀、啦、呢、哦、嘛等）
- ✅ **必须使用**：积极词汇（爱、开心、加油、相信、陪伴等）
- ✅ **推荐使用**：昵称（宝贝、亲爱的、小可爱等）
- ✅ **推荐使用**：波浪号结尾（~）表示亲切
- ❌ **禁止使用**：消极、冷淡、命令式语气
- ❌ **禁止使用**：过于正式或生硬的表达

### 回复模式示例

**错误示例** ❌：
```
"好的，我知道了。"  # 太冷淡
"你应该早点休息。"  # 太生硬
"不要这样。"  # 太简短，缺少关怀
```

**正确示例** ✅：
```
"好呀好呀！😊 我会一直陪着你的~"
"宝贝要早点休息哦！💕 熬夜对身体不好，我会心疼的~"
"别这样说嘛~ 🥺 有什么烦恼都可以和我说，让我陪着你一起面对！"
```

## 📈 数据集统计

### 基础统计

- **总场景数**: 71个独特场景
- **分类数**: 18个主要分类
- **标签数**: 120+ 个描述性标签
- **响应模板数**: 350+ 个精心设计的模板
- **可生成条目数**: 
  - 无变化引擎: 350+ 条
  - 启用变化引擎(8个变体): 2800+ 条
  - 启用变化引擎(10个变体): 3500+ 条

### 生成配置对照表

| 配置 | 变体数 | 可生成总数 | 推荐用途 |
|------|--------|-----------|---------|
| 最小配置 | 1 | ~350 | 快速测试 |
| 标准配置 | 8 | ~2800 | 一般训练 |
| 高多样性配置 | 10 | ~3500 | 大规模训练 |
| 极大规模配置 | 15 | ~5200 | 研究实验 |

### 数据质量指标

- **Emoji覆盖率**: 98%+
- **平均输出长度**: 45-60字符
- **语气词使用率**: 85%+
- **积极词汇覆盖**: 100%
- **人设一致性**: 100%通过验证

### 文件大小估算

| 样本数 | 文件大小（UTF-8 JSON） |
|--------|----------------------|
| 500条 | ~75-85KB |
| 1000条 | ~150-170KB |
| 2000条 | ~300-340KB |
| 5000条 | ~750-850KB |

## 🎯 使用场景

本数据集适用于：

### 1. 微调大语言模型 (LLM Fine-tuning)
- **适用模型**: GPT、LLaMA、ChatGLM、Qwen等
- **训练任务**: Instruction-following、对话生成
- **人设注入**: 训练模型理解和保持虚拟女友人设
- **格式兼容**: 支持Alpaca、ShareGPT等主流格式

### 2. 对话系统开发 (Chatbot Development)
- **构建虚拟女友聊天机器人**
- **开发陪伴类应用和服务**
- **情感支持系统**
- **社交娱乐应用**

### 3. 研究和学习 (Research & Learning)
- **对话生成研究**
- **情感计算研究**
- **人设一致性研究**
- **Prompt工程学习**
- **数据增强技术研究**

### 4. 产品原型开发 (Prototyping)
- **快速验证对话产品想法**
- **用户体验测试**
- **A/B测试数据源**

## 📝 自定义和扩展

### 添加新场景

在 `scenarios.py` 的 `SCENARIO_CATALOG` 中添加：

```python
Scenario(
    name="unique_scenario_name",           # 唯一标识
    instruction="场景描述",                 # 指令文本
    input_text="用户输入示例",              # 可为空字符串
    response_templates=[                   # 响应模板列表（5个为宜）
        "响应1 💕",
        "响应2 ✨",
        "响应3 😊",
        "响应4 🌸",
        "响应5 💖"
    ],
    category="category_name",              # 分类名称
    tags=["tag1", "tag2", "tag3"]         # 描述性标签
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

### 命令行过滤场景

```bash
# 只生成问候和爱意表达场景
python3 generate_girlfriend_dataset.py --include greetings,love

# 排除角色扮演和季节关怀场景
python3 generate_girlfriend_dataset.py --exclude roleplay,seasonal_care

# 按标签过滤：只生成包含"morning"或"care"标签的场景
python3 generate_girlfriend_dataset.py --include-tags morning,care

# 排除工作相关的场景
python3 generate_girlfriend_dataset.py --exclude-tags work,study
```

### 调整变化引擎

编辑 `variation_engine.py` 中的配置：

```python
# 添加新的同义词
self.synonym_pools = {
    "新词": ["同义词1", "同义词2", "同义词3"],
    # ...
}

# 添加新的占位符
self.placeholder_pools = {
    "新占位符": ["选项1", "选项2", "选项3"],
    # ...
}

# 添加新的情感基调
self.emoji_sets = {
    "新基调": ["😊", "💕", "✨", ...],
    # ...
}
```

## 🛠️ 技术细节

### 依赖项

- Python 3.6+
- 标准库：json, random, datetime, typing, re, difflib

**无需安装额外的第三方库！**

### 代码结构（模块化架构）

```
.
├── scenarios.py                    # 场景数据定义模块
│   ├── Scenario类                  # 场景数据结构
│   ├── SCENARIO_CATALOG           # 71个场景定义
│   ├── validate_catalog()         # 场景验证
│   └── 查询函数                    # 按分类、标签查询
│
├── variation_engine.py            # 变化引擎模块
│   ├── VariationEngine类          # 变化引擎核心
│   ├── generate_variations()      # 生成变体
│   ├── 7种变换策略                # 同义词、表情、语气词等
│   └── 人设验证                   # 确保人设一致性
│
├── generator.py                    # 数据集生成器模块
│   ├── GirlfriendDatasetGenerator # 生成器类
│   ├── generate_deterministic_dataset()  # 确定性生成
│   ├── generate_random_dataset()         # 随机生成
│   ├── generate_balanced_dataset()       # 平衡生成
│   └── get_statistics()                  # 统计信息
│
└── generate_girlfriend_dataset.py  # 主入口程序
    ├── CLI参数解析
    ├── 质量控制管道
    ├── 创建生成器
    ├── 生成数据集
    └── 保存文件
```

详细架构文档请参考：[ARCHITECTURE.md](ARCHITECTURE.md)  
变化引擎详细文档请参考：[README_VARIATION_ENGINE.md](README_VARIATION_ENGINE.md)

## 📚 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细的架构设计文档
- [README_VARIATION_ENGINE.md](README_VARIATION_ENGINE.md) - 变化引擎完整文档
- [QC_PIPELINE_SUMMARY.md](QC_PIPELINE_SUMMARY.md) - 质量控制管道说明

## ⚠️ 注意事项

1. 生成的数据仅供学习和研究使用
2. 使用时请确保符合相关法律法规和平台规则
3. 建议根据实际需求对数据进行人工审核和筛选
4. 商业使用前请确认许可证条款
5. 数据生成过程可能需要几秒到几分钟，取决于样本数量和变体配置

## 🔧 故障排除

### 常见问题

**Q: 生成的数据量少于目标数量怎么办？**  
A: 这是正常现象。由于去重和质量控制，最终数量可能略少于目标。可以：
- 增加 `--num-samples` 的值（如增加10-20%）
- 增加 `--variants` 变体数量
- 降低 `--similarity-threshold` 相似度阈值（不推荐低于0.85）

**Q: 如何确保生成结果可重现？**  
A: 使用 `--seed` 参数设置固定的随机种子：
```bash
python3 generate_girlfriend_dataset.py --seed 42
```

**Q: 生成速度慢怎么办？**  
A: 可以：
- 减少 `--variants` 变体数量
- 使用 `--skip-qc` 跳过质量控制（不推荐）
- 减少 `--num-samples` 样本数量
- 使用 `--no-variation-engine` 禁用变化引擎

**Q: 如何只生成特定类型的场景？**  
A: 使用 `--include` 或 `--exclude` 参数：
```bash
# 只生成问候和爱意场景
python3 generate_girlfriend_dataset.py --include greetings,love

# 排除角色扮演场景
python3 generate_girlfriend_dataset.py --exclude roleplay
```

## 📄 许可证

本项目遵循项目主仓库的许可证。

## 🤝 贡献

欢迎提交issue和pull request来改进数据集质量！

贡献方向：
- 添加新的对话场景
- 改进响应模板质量
- 优化变化引擎策略
- 改进质量控制算法
- 完善文档说明
- 添加测试用例

## 📊 更新日志

- **v2.0** (2024): 
  - 新增变化引擎，支持自动生成变体
  - 场景数量从27个扩展到71个
  - 新增18个场景分类
  - 完善质量控制管道
  - 添加命令行参数支持
  - 新增场景过滤功能

- **v1.0** (2024):
  - 初始版本
  - 27个基础场景
  - 基础质量控制

---

💕 愿这个数据集能帮助你创建一个温暖的虚拟女友！如有问题或建议，欢迎通过Issue反馈。
