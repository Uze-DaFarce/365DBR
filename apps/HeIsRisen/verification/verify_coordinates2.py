import asyncio
import os
from playwright.async_api import async_playwright
import urllib.request
import time

async def main():
    print("Starting visual verification...")
    # Start a background server
    os.system("python3 -m http.server 8008 --directory apps/HeIsRisen &")
    time.sleep(2)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # MOBILE FINAL
        context = await browser.new_context(viewport={'width': 844, 'height': 390})
        page = await context.new_page()
        await page.goto("http://localhost:8008/m/index.html")
        await page.wait_for_function("window.game && window.game.scene && window.game.scene.scenes.length > 0")

        await page.evaluate("""() => {
            const registry = window.game.registry;
            let foundEggs = [];
            let eggData = {};
            for(let i=1; i<=60; i++) {
               foundEggs.push({ eggId: i, x: 0, y: 0, section: 'a' });
               eggData[i.toString()] = { categorized: true, category: 'Christian' };
            }
            registry.set('foundEggs', foundEggs);
            registry.set('eggData', eggData);
            registry.set('correctCategorizations', 60);

            // stop all scenes
            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            // start FinalEggZam directly
            window.game.scene.start('FinalEggZam');
        }""")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="apps/HeIsRisen/verification/mobile_final_eggzam_real.png")

        # DESKTOP FINAL
        context2 = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page2 = await context2.new_page()
        await page2.goto("http://localhost:8008/index.html")
        await page2.wait_for_function("window.game && window.game.scene && window.game.scene.scenes.length > 0")

        await page2.evaluate("""() => {
            const registry = window.game.registry;
            let foundEggs = [];
            let eggData = {};
            for(let i=1; i<=60; i++) {
               foundEggs.push({ eggId: i, x: 0, y: 0, section: 'a' });
               eggData[i.toString()] = { categorized: true, category: 'Christian' };
            }
            registry.set('foundEggs', foundEggs);
            registry.set('eggData', eggData);
            registry.set('correctCategorizations', 60);

            // stop all scenes
            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            // start FinalEggZam directly
            window.game.scene.start('FinalEggZam');
        }""")
        await page2.wait_for_timeout(2000)
        await page2.screenshot(path="apps/HeIsRisen/verification/desktop_final_eggzam_real.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
