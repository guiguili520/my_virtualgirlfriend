# 脚本目录 / Scripts Directory

## 📁 目录说明

本目录包含项目的各类自动化脚本和工具。

This directory contains automation scripts and utilities for the project.

## 📜 脚本清单 / Script List

### 1. generate_dataset.py
**功能**: 生成虚拟女友训练数据集

**用法**:
```bash
# 基础生成 (500 样本, 8 变体/场景)
python scripts/generate_dataset.py

# 自定义参数
python scripts/generate_dataset.py --num-samples 1000 --variants 10 --seed 42

# 按类别筛选
python scripts/generate_dataset.py --include greetings,love
python scripts/generate_dataset.py --exclude roleplay,seasonal_care

# 按标签筛选
python scripts/generate_dataset.py --include-tags morning,care
python scripts/generate_dataset.py --exclude-tags work

# 质量控制调优
python scripts/generate_dataset.py --min-length 20 --max-length 150 --similarity-threshold 0.85
```

**输出**: `data/train/girlfriend_chat_dataset_<timestamp>.json`

### 2. fine_tune.py
**功能**: 全参数微调脚本 (预留)

**用法**:
```bash
python scripts/fine_tune.py --model Qwen2.5-7B-Instruct --data data/train/girlfriend_chat_dataset_*.json
```

**注意**: 需要较大的 GPU 内存 (40GB+)

### 3. lora_train.py
**功能**: LoRA 微调脚本 (推荐)

**用法**:
```bash
python scripts/lora_train.py --model Qwen2.5-7B-Instruct --data data/train/girlfriend_chat_dataset_*.json
```

**优点**: 
- 显存需求低 (12GB+ GPU)
- 训练速度快
- 保存空间小

### 4. cross_dedup_check.py
**功能**: 跨数据集去重检查

**用法**:
```bash
python scripts/cross_dedup_check.py --train data/train/*.json --validation data/validation/*.json
```

### 5. example_variation_usage.py
**功能**: 变体引擎使用示例

**用法**:
```bash
python scripts/example_variation_usage.py
```

### 6. clear_memory.py
**功能**: 清理内存工具

**用法**:
```bash
python scripts/clear_memory.py
```

## 🔧 依赖关系

所有脚本依赖于 `src/` 目录下的核心模块：

```
scripts/
├── generate_dataset.py → src/generator.py, src/scenarios.py, src/variation_engine.py
├── fine_tune.py → src/config.py
├── lora_train.py → src/config.py
└── ...
```

## 📝 开发新脚本

创建新脚本时，请遵循以下规范：

1. **导入 src 模块**:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import PROJECT_ROOT
from generator import GirlfriendDatasetGenerator
```

2. **使用配置文件**: 从 `src/config.py` 读取配置参数

3. **命令行参数**: 使用 `argparse` 提供清晰的 CLI 接口

4. **错误处理**: 提供友好的错误信息

5. **文档注释**: 添加函数和模块的文档字符串

## 🚀 快速开始

```bash
# 1. 生成训练数据
python scripts/generate_dataset.py

# 2. 训练模型 (LoRA 推荐)
python scripts/lora_train.py

# 3. 测试模型 (功能开发中)
# python scripts/test_model.py
```

## 📚 相关文档

- 数据集文档: `data/README.md`
- 配置说明: `src/config.py`
- 项目架构: `docs/ARCHITECTURE.md`
