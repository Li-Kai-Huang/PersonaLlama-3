from unsloth import FastLanguageModel

# 載入你剛練好的模型
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "mixed_personality_v4_final", # 指向你 save_pretrained 的路徑
    load_in_4bit = True,
)
FastLanguageModel.for_inference(model)

def ask_llama(user_input, explicit_tag=None):
    # 如果沒給標籤，就讓 Llama-3 自己猜
    tag = f"[{explicit_tag}] " if explicit_tag else ""
    prompt = f"### Instruction:\n{user_input}\n\n### Response:\n"
    inputs = tokenizer([prompt], return_tensors = "pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens = 512, temperature = 0.7)
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)[0].split("### Response:\n")[-1]

# --- 報告用的測試案例 ---
print("🧪 案例 1：NLP 專業問題（不加標籤）")
print(ask_llama("請解釋為什麼 Transformer 比 RNN 適合處理長文本？"))

print("\n🧪 案例 2：感情求助（不加標籤）")
print(ask_llama("我的曖昧對象突然不回我了，我該傳什麼給她？"))