import json
import re

def clean_ptt_content(text):
    # 1. 移除標題、作者、時間等 Header
    text = re.sub(r"作者.*看板.*標題.*時間.*\n", "", text)
    # 2. 移除引言內容 (※ 引述《...》之銘言)
    text = re.sub(r"※ 引述《.*》之銘言[\s\S]*?\n", "", text)
    # 3. 移除簽名檔與廣告 (-- 之後的內容)
    text = text.split("--")[0]
    # 4. 移除手機發文資訊
    text = re.sub(r"Sent from JPTT on my .*", "", text)
    text = re.sub(r"-----\n", "", text)
    # 5. 清理多餘換行
    text = text.strip()
    return text

cleaned_data = []
with open("ptt_mentor_data_real.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        # 提取靈魂內容
        original_output = item["output"]
        clean_output = clean_ptt_content(original_output)
        
        # 過濾掉太短的無意義回覆
        if len(clean_output) > 50:
            item["output"] = clean_output
            # 讓指令更具備導師感
            item["instruction"] = "[人格:感情導師] 你是一位洞察力敏銳的感情專家。請分析以下情境，並以理性且溫柔的語氣給予深度建議。"
            cleaned_data.append(item)

with open("gold_mentor_data.jsonl", "w", encoding="utf-8") as f:
    for entry in cleaned_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"🎉 清洗完成！保留了 {len(cleaned_data)} 筆高品質語料。")