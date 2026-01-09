from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset


# 1. 舔狗專用 Alpaca 模板
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def main():
    # 2. 載入模型 (4-bit 節省顯存)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/llama-3-8b-bnb-4bit",
        max_seq_length = 2048,
        load_in_4bit = True,
    )
    
    EOS_TOKEN = tokenizer.eos_token 

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha = 16,
        use_gradient_checkpointing = "unsloth", 
        random_state = 3407,
    )

    # 3. 載入與格式化「舔狗」資料集
    dataset = load_dataset("json", data_files="mixed_personality_v3_final.jsonl", split="train")

    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        inputs       = examples.get("input", [""] * len(instructions)) 
        outputs      = examples["output"]
        texts = []
        for instruction, input_text, output in zip(instructions, inputs, outputs):
            valid_input = input_text if input_text is not None else ""
            text = alpaca_prompt.format(instruction, valid_input, output) + EOS_TOKEN
            texts.append(text)
        return { "text" : texts, }

    dataset = dataset.map(formatting_prompts_func, batched = True,)

    # 4. 針對性格微調的訓練參數
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = 2048,
        args = SFTConfig(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = -1, # 使用 num_train_epochs
            num_train_epochs = 3,       # 增加 Epoch 讓卑微的人格更穩固
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "cosine",
            save_steps = 100,               # 每 100 步存一個中間檔
            seed = 3407,
            output_dir = "outputs_v2_3epochs", # 區分輸出目錄
        ),
    )

    print("--- 3080 Ti 已就緒：正在植入舔狗人格 ---")
    trainer.train()
    model.save_pretrained("mixed_personality_v4_final") # 儲存為另一個模型目錄

if __name__ == "__main__":
    main()