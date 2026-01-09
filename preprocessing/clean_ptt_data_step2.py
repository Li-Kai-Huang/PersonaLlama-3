import json
import re

def final_polish(text):
    # 1. 移除開頭是冒號的引言行 (PTT 回文常見的引用)
    lines = text.split('\n')
    # 只保留不是以 : 開頭，且不是空行的內容
    cleaned_lines = [l for l in lines if not l.strip().startswith(':') and l.strip()]
    text = '\n'.join(cleaned_lines)
    
    # 2. 移除多餘的空白符號
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

# 處理並合併資料
final_list = []
# 讀取你目前的資料
with open("gold_mentor_data.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        item["output"] = final_polish(item["output"])
        if len(item["output"]) > 30: # 確保內容夠長
            final_list.append(item)

# 寫入最後檔案
with open("mentor_clean_v3.jsonl", "w", encoding="utf-8") as f:
    for entry in final_list:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")