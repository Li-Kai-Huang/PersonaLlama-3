import requests
import json

def scrape_dcard_safely():
    # 增加更完整的 Headers 偽裝成真實瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.dcard.tw/f/relationship'
    }
    url = "https://www.dcard.tw/service/api/v2/forums/relationship/posts?limit=10"
    
    try:
        response = requests.get(url, headers=headers)
        # 檢查 HTTP 狀態碼
        if response.status_code != 200:
            print(f"❌ 請求失敗，狀態碼：{response.status_code}")
            print("內容可能是 HTML 阻擋頁面：", response.text[:200]) # 印出前200字檢查
            return

        posts = response.json()
        print(f"✅ 成功抓取 {len(posts)} 篇文章！")
        # ... 後續處理邏輯 ...
        
    except Exception as e:
        print(f"💥 發生錯誤：{e}")

if __name__ == "__main__":
    scrape_dcard_safely()