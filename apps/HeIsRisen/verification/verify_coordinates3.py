import asyncio
import os
from playwright.async_api import async_playwright
import urllib.request
import time

async def main():
    print("Starting visual verification (taking UI through actual sequence)...")
    # Start a background server
    os.system("python3 -m http.server 8008 --directory apps/HeIsRisen &")
    time.sleep(2)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # MOBILE FINAL
        context = await browser.new_context(viewport={'width': 844, 'height': 390})
        page = await context.new_page()
        await page.goto("http://localhost:8008/m/index.html")
        await page.wait_for_timeout(2000)

        # Tap anywhere to start
        await page.mouse.click(422, 195)
        await page.wait_for_timeout(2000)

        # Skip intro video
        await page.mouse.click(422, 195)
        await page.wait_for_timeout(2000)

        # We are at map. Jump directly to final eggzam
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
            registry.set('currentScore', 500);

            // stop all scenes
            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            window.game.scene.start('FinalEggZam');
        }""")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="apps/HeIsRisen/verification/mobile_final_eggzam_real.png")

        # MOBILE CAT
        await page.evaluate("""() => {
            const registry = window.game.registry;
            registry.set('foundEggs', 1);
            let eggData = {};
            // Set first egg uncategorized
            eggData['1'] = { categorized: false, category: 'Christian' };
            registry.set('eggData', eggData);

            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            window.game.scene.start('CategorizeScene');
        }""")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="apps/HeIsRisen/verification/mobile_cat_real.png")

        # DESKTOP
        context2 = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page2 = await context2.new_page()
        await page2.goto("http://localhost:8008/index.html")
        await page2.wait_for_timeout(2000)

        # click start
        await page2.mouse.click(640, 360)
        await page2.wait_for_timeout(2000)

        # skip video
        await page2.mouse.click(640, 360)
        await page2.wait_for_timeout(2000)

        # DESKTOP FINAL
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
            registry.set('currentScore', 500);

            // stop all scenes
            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            window.game.scene.start('FinalEggZam');
        }""")
        await page2.wait_for_timeout(2000)
        await page2.screenshot(path="apps/HeIsRisen/verification/desktop_final_eggzam_real.png")

        # DESKTOP CAT
        await page2.evaluate("""() => {
            const registry = window.game.registry;
            registry.set('foundEggs', 1);
            let eggData = {};
            // Set first egg uncategorized
            eggData['1'] = { categorized: false, category: 'Christian' };
            registry.set('eggData', eggData);

            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            window.game.scene.start('CategorizeScene');
        }""")
        await page2.wait_for_timeout(2000)
        await page2.screenshot(path="apps/HeIsRisen/verification/desktop_cat_real.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
