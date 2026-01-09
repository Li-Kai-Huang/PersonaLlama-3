import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_threads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 模擬真實手機瀏覽器，Threads 對行動版更友好
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        
        # 搜尋關鍵字：工具人 (你可以換成其他詞)
        search_url = "https://www.threads.net/search?q=%E5%B7%A5%E5%85%B7%E4%BA%BA"
        print(f"正在前往 Threads 搜尋: 工具人...")
        await page.goto(search_url)
        await page.wait_for_timeout(5000)

        results = []
        # 模擬捲動 10 次抓取更多內容
        for i in range(10):
            print(f"捲動第 {i+1} 次...")
            # 抓取包含貼文內容的 span 或 div
            posts = await page.query_selector_all('span')
            for post in posts:
                text = await post.inner_text()
                if len(text) > 5 and any(k in text for k in ["我", "她", "他", "不回", "已讀"]):
                    results.append({
                        "instruction": "請模仿 Threads 上的卑微語氣回覆：",
                        "input": "",
                        "output": text.replace("\n", " ").strip()
                    })
            
            await page.evaluate("window.scrollBy(0, 1500)")
            await page.wait_for_timeout(2000)

        # 去重處理
        unique_results = {res['output']: res for res in results}.values()

        with open("threads_simp_data.jsonl", "w", encoding="utf-8") as f:
            for entry in unique_results:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"🎉 抓取成功！共獲得 {len(unique_results)} 筆 Threads 語料。")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_threads())