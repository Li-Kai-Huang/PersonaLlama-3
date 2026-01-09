from unsloth import FastLanguageModel
import torch
import sys

# 1. 載入你剛訓練好的模型
# "nlp_final_model" 是你剛才 save_pretrained 儲存的資料夾名稱
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "simp_llama_model_2", 
    max_seq_length = 2048,
    load_in_4bit = True,
)
FastLanguageModel.for_inference(model) # 啟用 2 倍速推理加速

# 2. 定義跟訓練時一模一樣的模板
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

print("\n" + "="*50)
print("🦥 Unsloth 互動測試已啟動！輸入 'quit' 即可結束。")
print("="*50)

# 3. 建立互動迴圈
while True:
    user_instruction = input("\n請輸入你的問題 (Instruction): ")
    if user_instruction.lower() == 'quit':
        break
        
    user_input = input("如果有額外補充 (Input，無則按 Enter): ")

    # 將輸入包裝進模板
    inputs = tokenizer(
        [
            alpaca_prompt.format(
                user_instruction, # 指令
                user_input,       # 補充資料
                "",               # 模型回答的起點
            )
        ], return_tensors = "pt").to("cuda")

    # 讓 3080 Ti 進行矩陣運算並生成答案
    outputs = model.generate(
        **inputs, 
        max_new_tokens = 512,
        use_cache = True, # 加速解碼過程
        temperature = 0.8,         # 提高溫度，讓回覆更有隨機性與創意
        repetition_penalty = 1.2,  # 關鍵！強制模型不可以一直講重複的話
        top_p = 0.9,               # 確保用詞既有變化又不會太離譜
        do_sample = True,          # 開啟隨機取樣模式
    )
    
    # 解碼並印出結果
    result = tokenizer.batch_decode(outputs)
    # 只擷取 Response 之後的內容，並去除結束符號
    final_response = result[0].split("### Response:\n")[-1].replace(tokenizer.eos_token, "")
    
    print("\n--- 模型回答 ---")
    print(final_response)
    print("-" * 30)