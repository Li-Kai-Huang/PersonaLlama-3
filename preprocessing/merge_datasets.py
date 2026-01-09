import json
import random
import re

def clean_content(text):
    """
    資工系專用的資料清洗邏輯：移除 PTT 特有雜訊
    """
    # 1. 移除 PTT 標頭資訊 (作者、看板、標題、時間)
    text = re.sub(r"作者.*看板.*標題.*時間.*\n", "", text)
    
    # 2. 移除開頭是冒號的引言行 (如 : 各位戀愛大神...)
    lines = text.split('\n')
    cleaned_lines = [l for l in lines if not l.strip().startswith(':') and l.strip()]
    text = '\n'.join(cleaned_lines)
    
    # 3. 移除 PTT 特有的發信站、廣告簽名檔
    text = text.split('※ 發信站:')[0]
    text = text.split('--')[0]
    
    # 4. 處理多餘的空行與空白
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def tag_and_merge_pro(files_config, output_file):
    combined_data = []
    
    for file_path, tag, weight in files_config:
        print(f"📡 正在處理: {file_path} (標籤: {tag}, 權重倍率: {weight})")
        
        with open(file_path, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
            
            for _ in range(weight): 
                for line in raw_lines:
                    try:
                        item = json.loads(line)
                        
                        # 💡 核心修正：移除 instruction 中已存在的舊標籤，再統一加上新標籤
                        instr = item['instruction']
                        instr = re.sub(r"\[人格:.*?\]", "", instr).strip()
                        new_instr = f"[{tag}] {instr}"
                        
                        # 執行清洗
                        cleaned_output = clean_content(item["output"])
                        
                        if len(cleaned_output) > 15: # 門檻稍降，保留精華短句
                            combined_data.append({
                                "instruction": new_instr,
                                "input": item.get("input", ""),
                                "output": cleaned_output
                            })
                    except Exception as e:
                        print(f"跳過錯誤行: {e}")

    # 💡 關鍵：打亂順序以防止 Catastrophic Forgetting
    random.shuffle(combined_data)

    with open(output_file, "w", encoding="utf-8") as f:
        for entry in combined_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"✅ 合併完成！總計 {len(combined_data)} 筆，儲存至 {output_file}")

if __name__ == "__main__":
    # 配置：(檔案路徑, 標籤, 權重倍率)
    files_to_merge = [
        ("dataset.jsonl", "人格:NLP助教", 10),     # 放大 10 倍，強化專業知識
        ("mentor_clean_v3.jsonl", "人格:感情導師", 1), # 保持原樣
        ("real_ptt_data_v2.jsonl", "人格:舔狗", 1)   # 保持原樣
    ]
    tag_and_merge_pro(files_to_merge, "mixed_personality_v3_final.jsonl")