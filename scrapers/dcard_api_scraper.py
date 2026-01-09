import cloudscraper
import json
import time
import random

def get_dcard_data_with_bypass(limit=30, batches=5):
    # 建立一個可以繞過 Cloudflare 的 scraper 物件
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    base_api = "https://www.dcard.tw/service/api/v2/forums/relationship/posts"
    all_data = []
    last_id = None

    for i in range(batches):
        print(f"📡 正在抓取第 {i+1} 批文章...")
        params = {'limit': limit}
        if last_id:
            params['before'] = last_id

        try:
            # 使用 scraper 發送請求
            res = scraper.get(base_api, params=params, timeout=10)
            
            if res.status_code != 200:
                print(f"❌ 還是被擋，狀態碼：{res.status_code}")
                if res.status_code == 403:
                    print("💡 建議：嘗試換個 IP (如手機熱點) 或是稍後再試。")
                break

            posts = res.json()
            if not posts: break

            for post in posts:
                last_id = post['id']
                title = post['title']
                
                # 關鍵字篩選：確保跟「卑微/感情」有關
                keywords = ["卑微", "工具人", "不回", "冷淡", "挽回", "對不起", "到底算什麼"]
                if any(k in title for k in keywords):
                    print(f"🎯 發現目標：{title}")
                    
                    # 抓取詳細內文
                    content_url = f"https://www.dcard.tw/service/api/v2/posts/{last_id}"
                    content_res = scraper.get(content_url)
                    if content_res.status_code == 200:
                        content = content_res.json().get('content', '')
                        all_data.append({
                            "instruction": f"關於文章『{title}』，請模仿其風格回覆：",
                            "input": "",
                            "output": content.replace("\n", " ").strip()[:400]
                        })
                    time.sleep(random.uniform(2, 4)) # 頻率要慢，Dcard 會鎖 IP

        except Exception as e:
            print(f"💥 發生錯誤：{e}")
            break

    with open("dcard_api_data_v2.jsonl", "w", encoding="utf-8") as f:
        for entry in all_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"🎉 成功！獲得 {len(all_data)} 筆資料。")

if __name__ == "__main__":
    get_dcard_data_with_bypass(limit=30, batches=10)