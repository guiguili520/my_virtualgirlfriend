from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer,
    DataCollatorForLanguageModeling, TrainerCallback, EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch
import numpy as np
from sklearn.metrics import accuracy_score
import evaluate

# 配置参数
model_path = "./models"  # 从项目根目录的 models 目录加载基础模型
output_dir = "./models/qwen-ai-girlfriend-lora"
dataset_path = "./data/train/girlfriend_chat_dataset_20251117_055552.json"  # 2000条训练数据

print("加载模型和tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# 添加pad token如果不存在
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 针对 MPS 优化模型加载
if torch.backends.mps.is_available():
    print("检测到MPS设备，使用Mac GPU加速")
    # 使用 float16 减少内存占用，避免卡死
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.float16,  # 使用float16，内存占用减半
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    model = model.to("mps")
    # 启用梯度检查点以节省显存
    model.gradient_checkpointing_enable()
    print("已启用梯度检查点，使用float16精度")
else:
    print("使用CPU或CUDA设备")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    model.gradient_checkpointing_enable()

# 优化的LoRA配置 - 平衡性能与内存
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=4,  # 保持适中的秩，平衡效果与内存
    lora_alpha=16,  # 相应调整alpha
    lora_dropout=0.15,  # 适度dropout
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # 训练核心注意力模块
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()


# 数据预处理 - 添加数据增强
def preprocess_function(examples):
    texts = []
    for i in range(len(examples['instruction'])):
        # 随机决定是否包含system指令，增加数据多样性
        if np.random.random() > 0.2:  # 80%的概率包含system指令
            messages = [
                {"role": "system", "content": examples['instruction'][i]},
                {"role": "user", "content": examples['input'][i]},
                {"role": "assistant", "content": examples['output'][i]}
            ]
        else:
            # 20%的概率不包含system指令，让模型学习在没有上下文的情况下回应
            messages = [
                {"role": "user", "content": examples['input'][i]},
                {"role": "assistant", "content": examples['output'][i]}
            ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        texts.append(text)

    tokenized = tokenizer(
        texts,
        truncation=True,
        max_length=384,  # 适度减少序列长度，保留足够的上下文
        padding=False,
        add_special_tokens=True
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized


# 加载并分割数据
dataset = load_dataset('json', data_files=dataset_path)

# 对小数据集进行训练/验证分割
if len(dataset['train']) > 100:  # 确保有足够数据分割
    dataset = dataset['train'].train_test_split(
        test_size=0.2,  # 20%作为验证集
        shuffle=True,
        seed=42
    )
else:
    # 如果数据太少，使用全部数据训练，创建一个小的虚拟验证集
    train_dataset = dataset['train']
    # 取前10条作为验证集（如果数据很少）
    if len(train_dataset) > 20:
        val_size = min(10, len(train_dataset) // 5)
        dataset = train_dataset.train_test_split(
            test_size=val_size,
            shuffle=True,
            seed=42
        )
    else:
        # 数据非常少，全部用于训练
        dataset = {'train': train_dataset, 'test': train_dataset.select(range(min(3, len(train_dataset))))}

print(f"训练集大小: {len(dataset['train'])}")
print(f"验证集大小: {len(dataset['test'])}")

tokenized_dataset = dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=dataset['train'].column_names
)


# 计算评估指标的函数
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    # 计算准确率（忽略padding token）
    mask = labels != -100
    aligned_predictions = predictions[mask]
    aligned_labels = labels[mask]

    accuracy = accuracy_score(aligned_labels, aligned_predictions)

    # 计算perplexity（需要交叉熵损失）
    loss_fct = torch.nn.CrossEntropyLoss()
    logits_tensor = torch.tensor(logits)
    labels_tensor = torch.tensor(labels)

    # 移除非标签位置
    mask = labels_tensor != -100
    active_logits = logits_tensor[mask]
    active_labels = labels_tensor[mask]

    loss = loss_fct(active_logits, active_labels)
    perplexity = torch.exp(loss)

    return {
        "accuracy": accuracy,
        "perplexity": perplexity.item(),
        "loss": loss.item()
    }


# 训练回调 - 添加内存管理
class TrainingMonitor(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and 'loss' in logs:
            print(f"Step {state.global_step}: Loss = {logs['loss']:.4f}")
        if logs and 'eval_loss' in logs:
            print(f"Step {state.global_step}: Eval Loss = {logs['eval_loss']:.4f}")
        
        # 定期清理 MPS 缓存
        if state.global_step % 10 == 0 and torch.backends.mps.is_available():
            torch.mps.empty_cache()

    def on_epoch_begin(self, args, state, control, **kwargs):
        print(f"\n🚀 开始第 {state.epoch} 轮训练")
        # 每轮开始前清理缓存
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
            print("已清理 MPS 缓存")

    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"✅ 完成第 {state.epoch} 轮训练")
        # 每轮结束后清理缓存
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
            print("已清理 MPS 缓存")


# 优化的训练参数 - 针对小数据集和内存限制
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    num_train_epochs=5,  # 增加轮数但使用早停
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=4,  # 减少累积步数，降低内存压力
    warmup_ratio=0.15,  # 更长的预热期，稳定训练
    logging_steps=5,  # 更频繁的日志
    eval_steps=20,  # 定期评估
    save_steps=100,
    learning_rate=2e-5,  # 显著降低学习率，提高数值稳定性
    fp16=False,  # 在MPS上禁用fp16训练，避免nan
    remove_unused_columns=True,
    report_to=None,
    dataloader_pin_memory=False,
    save_strategy="steps",
    logging_strategy="steps",
    eval_strategy="steps",  # 启用评估
    load_best_model_at_end=True,  # 训练结束时加载最佳模型
    metric_for_best_model="eval_loss",  # 根据验证损失选择最佳模型
    greater_is_better=False,  # 损失越小越好
    prediction_loss_only=False,  # 需要计算完整损失
    gradient_checkpointing=True,  # 启用梯度检查点
    max_grad_norm=1.0,  # 适当的梯度裁剪，防止梯度爆炸
)

# 创建 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['test'],
    data_collator=DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        pad_to_multiple_of=8  # 优化内存使用
    ),
    callbacks=[
        TrainingMonitor(),
        EarlyStoppingCallback(  # 早停回调
            early_stopping_patience=3,  # 3次评估没有改善就停止
            early_stopping_threshold=0.01  # 改善小于0.01不算改善
        )
    ],
    compute_metrics=compute_metrics  # 添加指标计算
)

# 开始训练
print("开始微调训练...")
trainer.train()

# 保存最终模型
trainer.save_model()
print(f"🎉 训练完成！模型保存在: {output_dir}")

# 保存训练统计
print("\n📊 训练统计:")
print(f"总训练步数: {trainer.state.global_step}")
print(f"训练耗时: {trainer.state.log_history[-1].get('train_runtime', 'N/A')} 秒")

# 最终评估
final_eval = trainer.evaluate()
print(f"最终验证损失: {final_eval.get('eval_loss', 'N/A')}")
print(f"最终验证困惑度: {final_eval.get('eval_perplexity', 'N/A')}")