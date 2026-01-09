from unsloth import FastLanguageModel
import torch

# 1. 載入剛訓練好的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "nlp_final_model", # 指向你剛才儲存的資料夾
    max_seq_length = 2048,
    load_in_4bit = True,
)
FastLanguageModel.for_inference(model) # 啟用 2 倍速推理模式

# 2. 定義測試問題
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

# 測試你的課程資料：鏈式法則
inputs = tokenizer(
    [
        alpaca_prompt.format(
            "什麼是語言模型的鏈式法則？", # 指令
            "", # 輸入 (空)
            "", # 模型回答的起點
        )
    ], return_tensors = "pt").to("cuda")

# 3. 讓 3080 Ti 生成答案
outputs = model.generate(**inputs, max_new_tokens = 128)
result = tokenizer.batch_decode(outputs)

# 4. 印出結果
print(result[0].split("### Response:\n")[-1].replace("<|end_of_text|>", ""))