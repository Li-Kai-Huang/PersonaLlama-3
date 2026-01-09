from unsloth import FastLanguageModel
import torch

# 💡 根據你剛才的截圖，選擇你練得最滿意的資料夾
model_path = "mixed_personality_v4_final" 

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_path,
    max_seq_length = 2048,
    load_in_4bit = True,
)

# 💡 推送到雲端 (這會自動處理大型檔案分片)
repo_id = "Li-Kai-Huang/Llama-3-8B-Multi-Persona-Ray"

print("--- 正在推送權重至 Hugging Face Hub ---")
model.push_to_hub(repo_id)
tokenizer.push_to_hub(repo_id)
print("✅ 推送完成！")