import requests
from bs4 import BeautifulSoup
import time
import json
import re

def get_ptt_real_simp_data(target_pages=20):
    base_url = "https://www.ptt.cc"
    current_url = "/bbs/Boy-Girl/index.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    cookies = {'over18': '1'}
    
    simp_dataset = []
    # 只要是求助、心情、分享，通通不放過
    target_tags = ["[求助]", "[心情]", "[分享]"]
    # 內文關鍵字：只要內文出現這些詞，這篇就很可能是「舔狗/卑微」主題
    body_keywords = ["工具人", "卑微", "暗戀", "訊息", "已讀", "不回", "宵夜", "接送"]

    for i in range(target_pages):
        print(f"正在掃描看板第 {i+1} 頁...")
        try:
            res = requests.get(base_url + current_url, headers=headers, cookies=cookies, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            articles = soup.select('div.r-ent')
            
            for art in articles:
                title_tag = art.select_one('div.title a')
                if not title_tag: continue
                title = title_tag.text
                
                # 只要標題符合標籤，就點進去
                if any(tag in title for tag in target_tags):
                    art_url = base_url + title_tag['href']
                    art_res = requests.get(art_url, headers=headers, cookies=cookies, timeout=10)
                    art_soup = BeautifulSoup(art_res.text, 'html.parser')
                    content = art_soup.select_one('#main-content').text
                    
                    # 檢查內文是否包含卑微關鍵字
                    if any(word in content for word in body_keywords):
                        print(f"找到潛在目標: {title}")
                        # 抓取「」內的文字，或者是 A: B 這種格式
                        # 使用正規表達式抓取括號內容
                        quotes = re.findall(r'[「『](.*?)[」』]', content)
                        for q in quotes:
                            if 5 < len(q) < 100: # 過濾太短或太長的亂碼
                                simp_dataset.append({
                                    "instruction": f"在情境『{title}』中，有一段卑微的對話：",
                                    "input": "",
                                    "output": q.strip()
                                })
                    time.sleep(0.5)

            prev_btn = soup.select('div.btn-group-paging a')[1]
            current_url = prev_btn['href']
            
        except Exception as e:
            print(f"錯誤: {e}")
            continue

    with open("real_ptt_data_v2.jsonl", "w", encoding="utf-8") as f:
        for entry in simp_dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"🎉 抓取結束！共獲得 {len(simp_dataset)} 筆語料。")

if __name__ == "__main__":
    get_ptt_real_simp_data(30) # 掃多一點，掃 30 頁