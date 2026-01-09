import gradio as gr
from unsloth import FastLanguageModel
import torch
import re

# 1. 載入你練好的模型 (請確認路徑正確)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "mixed_personality_v4_final", # 指向你合併後的模型路徑
    load_in_4bit = True,
)
'''
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "Li-Kai-Huang/Llama-3-8B-Multi-Persona-Ray", 
    load_in_4bit = True,
)
'''
FastLanguageModel.for_inference(model)

# 2. 定義預測函式
def predict(message, history, persona, auto_detect):
    # 隱含意圖辨識：如果開啟自動判斷且使用者沒手動選
    current_persona = persona
    if auto_detect:
        # 資工系最愛的簡易意圖識別：關鍵字過濾器
        academic_keywords = ["RNN", "Transformer", "梯度", "Loss", "微調", "LLM", "NLP", "權重"]
        emotional_keywords = ["曖昧", "冷淡", "女朋友", "吵架", "分手", "AA", "感情", "已讀"]
        
        if any(k in message for k in academic_keywords):
            current_persona = "人格:NLP助教"
        elif any(k in message for k in emotional_keywords):
            current_persona = "人格:感情導師"
        else:
            current_persona = "人格:舔狗" # 預設為舔狗 (或是原模型人格)

    # 💡 確保 Prompt 格式與訓練時完全一致（包含換行）
    prompt = f"### Instruction:\n[{current_persona}] {message}\n\n### Response:\n"
    
    inputs = tokenizer([prompt], return_tensors = "pt").to("cuda")
    
    # 💡 加入推論優化參數
    outputs = model.generate(
        **inputs, 
        max_new_tokens = 512,
        temperature = 0.5,        # 降低隨機性，讓回答更穩定
        repetition_penalty = 1.2, # 💡 強制防止它重複輸出標籤或指令
        pad_token_id = tokenizer.eos_token_id
    )
    
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    
    # 💡 只截取 Response 之後的純文字，並移除可能噴出的下一段 Instruction
    final_output = response.split("### Response:\n")[-1].split("### Instruction:")[0].strip()
    # 移除模型自己愛噴的 [系統] 或 [人格:XXX] 等前綴
    final_output = re.sub(r"\[人格:.*?\]", "", final_output)
    final_output = re.sub(r"\[系統.*?\]", "", final_output)
    return final_output

# 3. 構建 Gradio 介面
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"# 🤖 Ray 的 多人格測試平台")
    gr.Markdown(f"### 硬體：RTX 3080 Ti | 框架：Unsloth LoRA")
    
    with gr.Row():
        with gr.Column(scale=1):
            persona_radio = gr.Radio(
                ["人格:NLP助教", "人格:感情導師", "人格:感情維護員"], 
                label="選擇人格模式", 
                value="人格:NLP助教"
            )
            auto_cb = gr.Checkbox(label="啟動隱含意圖辨識 (Auto-Detect)", value=False)
            gr.Markdown("---")
            gr.Markdown("💡 **提示：** 助教適合問技術問題；導師適合問人生大事。")
            
        with gr.Column(scale=4):
            chatbot = gr.ChatInterface(
                fn=predict, 
                additional_inputs=[persona_radio, auto_cb],
                fill_height=True
            )

if __name__ == "__main__":
    demo.launch()