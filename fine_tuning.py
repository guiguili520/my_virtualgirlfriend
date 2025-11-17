from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer,
    DataCollatorForLanguageModeling, TrainerCallback
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch

# 配置参数
model_path = "./Qwen2.5-7B-Instruct"
output_dir = "./qwen-ai-girlfriend-lora"
dataset_path = "./train_data/dataset/girlfriend_chat_dataset_20251113_052759.json"

print("加载模型和tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# 针对 MPS 优化模型加载
if torch.backends.mps.is_available():
    print("检测到MPS设备，使用Mac GPU加速")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    # 手动移动到MPS设备
    model = model.to("mps")
else:
    print("使用CPU或CUDA设备")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

# LoRA 配置
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()


# 数据预处理
def preprocess_function(examples):
    texts = []
    for i in range(len(examples['instruction'])):
        messages = [
            {"role": "system", "content": examples['instruction'][i]},
            {"role": "user", "content": examples['input'][i]},
            {"role": "assistant", "content": examples['output'][i]}
        ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        texts.append(text)

    tokenized = tokenizer(texts, truncation=True, max_length=512, padding=False)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized


# 加载数据
dataset = load_dataset('json', data_files=dataset_path)
tokenized_dataset = dataset.map(
    preprocess_function, 
    batched=True,
    remove_columns=dataset['train'].column_names  # 移除原始列，只保留tokenized数据
)


# 训练回调
class TrainingMonitor(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and 'loss' in logs:
            print(f"Step {state.global_step}: Loss = {logs['loss']:.4f}")

    def on_epoch_begin(self, args, state, control, **kwargs):
        print(f"\n🚀 开始第 {state.epoch} 轮训练")

    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"✅ 完成第 {state.epoch} 轮训练")


# 优化的训练参数
training_args = TrainingArguments(
    output_dir=output_dir,
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
    learning_rate=2e-4,
    fp16=True,
    remove_unused_columns=True,
    report_to=None,
    dataloader_pin_memory=False,  # 禁用 MPS 不支持的 pin_memory
    save_strategy="steps",
    logging_strategy="steps",
    eval_strategy="no",  # 如果没有验证集，禁用评估
)

# 创建 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    callbacks=[TrainingMonitor()]
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