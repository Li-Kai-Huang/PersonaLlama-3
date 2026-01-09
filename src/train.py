from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

# 1. Llama-3 的 Alpaca 模板
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def main():
    # 2. 載入模型 (針對 3080 Ti 優化的 4-bit 版本)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/llama-3-8b-bnb-4bit",
        max_seq_length = 2048,
        load_in_4bit = True,
    )
    
    EOS_TOKEN = tokenizer.eos_token # 取得結束標記

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha = 16,
        use_gradient_checkpointing = "unsloth", 
        random_state = 3407,
    )

    # 3. 載入與格式化資料
    dataset = load_dataset("json", data_files="dataset.jsonl", split="train")

    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        # 使用 .get 確保找不到 "input" 時會補上空字串清單
        inputs       = examples.get("input", [""] * len(instructions)) 
        outputs      = examples["output"]
        texts = []
        for instruction, input_text, output in zip(instructions, inputs, outputs):
            # 確保 input_text 不是 None
            valid_input = input_text if input_text is not None else ""
            # 組合模板並加上結束符號，這是模型學會停止的關鍵
            text = alpaca_prompt.format(instruction, valid_input, output) + EOS_TOKEN
            texts.append(text)
        return { "text" : texts, }

    dataset = dataset.map(formatting_prompts_func, batched = True,)

    # 4. 訓練設定
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = 2048,
        dataset_num_proc = 2,
        args = SFTConfig(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 30, # 你的資料較少，先跑 30 步觀察
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit", # 節省顯存
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
        ),
    )

    print("--- 3080 Ti 啟動！正在微調你的 NLP 課程資料 ---")
    trainer.train()
    model.save_pretrained("nlp_final_model")

if __name__ == "__main__":
    main()