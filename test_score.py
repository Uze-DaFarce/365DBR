import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/apps/HeIsRisen/index.html")
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)
        # Start game
        await page.keyboard.press("Space")
        await asyncio.sleep(2)
        await page.keyboard.press("Space")
        await asyncio.sleep(2)

        # Navigate to SectionHunt
        await page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('SectionHunt', { sectionName: 'mammoth-hot-springs' })")
        await asyncio.sleep(2)

        # Collect egg
        score_before = await page.evaluate("() => window.game.scene.getScene('SectionHunt').scoreText.text")
        print(f"Score Before: {score_before}")

        await page.evaluate("""() => {
            const scene = window.game.scene.getScene('SectionHunt');
            if (scene.eggs && scene.eggs.getChildren().length > 0) {
                const egg = scene.eggs.getChildren()[0];
                scene.collectEgg(egg);
            }
        }""")

        await asyncio.sleep(1)
        score_after = await page.evaluate("() => window.game.scene.getScene('SectionHunt').scoreText.text")
        print(f"Score After: {score_after}")
        await browser.close()

asyncio.run(run())
