from curl_cffi import requests # 換成這個
from bs4 import BeautifulSoup
import json
import time
import random

def get_ptt_mentor_data_v2(pages=10):
    base_url = "https://www.ptt.cc"
    current_url = "/bbs/Boy-Girl/index.html"
    
    # 建立一個模擬 Chrome 120 的 Session
    session = requests.Session()
    
    mentor_data = []

    for i in range(pages):
        print(f"📡 正在模擬瀏覽器分析 PTT 第 {i+1} 頁...")
        try:
            # 使用 impersonate="chrome120" 繞過 TLS 檢測
            res = session.get(base_url + current_url, impersonate="chrome120", cookies={'over18': '1'}, timeout=10)
            
            if res.status_code != 200:
                print(f"❌ 頁面請求失敗: {res.status_code}")
                break
                
            soup = BeautifulSoup(res.text, 'html.parser')
            articles = soup.select('div.r-ent')
            
            for art in articles:
                title_tag = art.select_one('div.title a')
                # 只抓「Re:」開頭的文章，這些才是導師的回覆內容
                if title_tag and "Re:" in title_tag.text:
                    url = base_url + title_tag['href']
                    
                    # 進入文章內容
                    art_res = session.get(url, impersonate="chrome120", cookies={'over18': '1'}, timeout=10)
                    art_soup = BeautifulSoup(art_res.text, 'html.parser')
                    
                    # 抓取內文
                    main_content = art_soup.select_one('#main-content')
                    if not main_content: continue
                    
                    # 清洗內容：移除掉推文與轉信站資訊
                    full_text = main_content.text
                    clean_text = full_text.split('※ 發信站:')[0]
                    
                    if len(clean_text) > 150: # 夠長才有教育意義
                        print(f"✅ 抓取到導師文：{title_tag.text[:15]}...")
                        mentor_data.append({
                            "instruction": "[人格:感情導師] 你是一位洞察力敏銳的感情專家，請分析並回覆以下困境。",
                            "input": f"個案情境：{title_tag.text.replace('Re: ', '')}",
                            "output": clean_text.strip()
                        })
                    
                    # 隨機延遲，防止被 PTT 標記 IP
                    time.sleep(random.uniform(1, 3))

            # 抓取上一頁連結
            btns = soup.select('div.btn-group-paging a')
            current_url = btns[1]['href'] # index 1 是「上頁」

        except Exception as e:
            print(f"💥 發生連線異常: {e}")
            time.sleep(5)
            continue

    # 儲存
    with open("ptt_mentor_data_real.jsonl", "w", encoding="utf-8") as f:
        for entry in mentor_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"🎉 任務完成！共獲得 {len(mentor_data)} 筆高品質感情導師語料。")

if __name__ == "__main__":
    get_ptt_mentor_data_v2(15)