import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 0307 (The one that wasn't failing according to user) - PRO 6.31, 6.32
        context = await browser.new_context(viewport={'width': 800, 'height': 800})
        page = await context.new_page()

        await page.goto("https://mt-sin.ai/365DBR/index.html?startDate=0307")
        await page.wait_for_selector(".verse-block")

        await page.click("button[title='Jump to Psalms']")
        await page.wait_for_timeout(1000)

        print("Walking through end of Psalms to Proverbs (0307)...")
        for i in range(16):
            await page.keyboard.press("ArrowDown")
            await page.wait_for_timeout(400) # Faster keystrokes during reading

            logs = await page.evaluate('''() => {
                const activeEl = document.querySelector('.verse-block > div > div.bg-stone-900, .verse-block > div > div.bg-emerald-100, .verse-block > div > div.bg-rose-100').closest('.verse-block');
                return `Active: ${activeEl.id}`;
            }''')
            print(f"Step {i} {logs}")

        await browser.close()

asyncio.run(run())
