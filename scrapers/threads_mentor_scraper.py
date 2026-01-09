import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_threads_robust():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 模擬更真實的瀏覽器
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🚀 正在進入 Threads 搜尋『感情』相關討論...")
        await page.goto("https://www.threads.net/search?q=%E6%84%9F%E6%83%85%E5%BB%BA%E8%AD%B0")
        
        # 增加初始等待時間，讓頁面完全渲染
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(5000)

        mentor_dataset = []
        seen_text = set() # 避免重複抓取

        for i in range(10): # 捲動 10 次
            print(f"📄 捲動並掃描中 (第 {i+1} 次)...")
            
            # 💡 暴力解：抓取所有 div 標籤中的文字
            elements = await page.query_selector_all('div')
            for el in elements:
                text = await el.inner_text()
                text = text.strip()
                
                # 篩選邏輯：
                # 1. 長度大於 50 個字 (通常是心得或建議)
                # 2. 包含關鍵字
                # 3. 沒抓過
                if len(text) > 50 and any(k in text for k in ["建議", "我覺得", "因為", "分手", "另一半"]):
                    if text not in seen_text:
                        # 清洗文字：移除過多換行
                        clean_text = text.replace("\n", " ")
                        mentor_dataset.append({
                            "instruction": "[人格:感情導師] 請針對以下情感內容進行分析並給出建議。",
                            "input": f"文章內容：{clean_text[:100]}...",
                            "output": clean_text
                        })
                        seen_text.add(text)
            
            # 捲動並隨機等待
            await page.evaluate("window.scrollBy(0, 1500)")
            await page.wait_for_timeout(3000)

        # 儲存
        with open("threads_mentor_robust.jsonl", "w", encoding="utf-8") as f:
            for entry in mentor_dataset:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"🎉 成功！獲得 {len(mentor_dataset)} 筆真實語料。")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_threads_robust())