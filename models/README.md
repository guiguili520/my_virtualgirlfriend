# 模型文件目录 / Models Directory

## 📁 目录说明

2.0 版本的聊天推理默认使用在线模型 API，本目录不再是 Web 聊天的必需项。
本目录仍可用于训练脚本、LoRA 实验或离线模型资产存放。

Virtual Girlfriend 2.0 uses online model APIs for chat serving by default. This
directory remains useful for training scripts and offline model experiments.

## 🌐 2.0 在线模型配置

```bash
export VG_MODEL_PROVIDER=openai      # openai / anthropic / deepseek / glm / kimi
export OPENAI_API_KEY=your-key

export VG_MODEL_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-key
```

也可以通过 `VG_MODEL_BASE_URL`、`VG_MODEL_NAME`、`VG_MODEL_API_FORMAT` 接入自定义 OpenAI/Anthropic 兼容服务。

## 🤖 推荐模型 / Recommended Models

### Qwen2.5-7B-Instruct
- **来源**: 阿里云通义千问 (Alibaba Cloud Qwen)
- **大小**: ~14GB
- **用途**: 基础对话模型
- **下载地址**: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct

### LoRA 微调权重
- **目录**: `qwen-ai-girlfriend-lora/`
- **用途**: 虚拟女友人设微调权重
- **生成方式**: 使用 `scripts/lora_train.py` 训练生成

## 📂 文件结构

```
models/
├── Qwen2.5-7B-Instruct/           # 基础模型
│   ├── config.json
│   ├── tokenizer.json
│   ├── model-*.safetensors
│   └── ...
│
├── qwen-ai-girlfriend-lora/       # LoRA 微调权重
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── ...
│
└── README.md                      # 本文件
```

## 🔧 使用方法

### 1. 下载基础模型

```bash
# 使用 git lfs 下载 (推荐)
git lfs install
git clone https://huggingface.co/Qwen/Qwen2.5-7B-Instruct models/Qwen2.5-7B-Instruct

# 或使用 huggingface-cli
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir models/Qwen2.5-7B-Instruct
```

### 2. 训练 LoRA 权重

```bash
# 使用训练脚本
python scripts/lora_train.py

# 或使用微调脚本
python scripts/fine_tune.py
```

## ⚠️ 注意事项

1. **文件大小**: 模型文件通常较大 (10GB+)，请确保有足够的磁盘空间
2. **Git 管理**: 模型文件已在 `.gitignore` 中排除，不会上传到 Git 仓库
3. **下载时间**: 根据网络速度，下载可能需要较长时间
4. **存储建议**: 建议使用 SSD 以提高模型加载速度

## 📝 模型配置

模型相关配置在 `src/config.py` 中定义：

```python
MODEL_NAME = "Qwen2.5-7B-Instruct"
LORA_NAME = "qwen-ai-girlfriend-lora"
MODELS_DIR = PROJECT_ROOT / "models"
```

## 🔗 相关链接

- [Qwen 官方文档](https://qwen.readthedocs.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [PEFT/LoRA 文档](https://huggingface.co/docs/peft)
