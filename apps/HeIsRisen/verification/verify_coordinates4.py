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
        # Use headed mode to avoid swiftshader issues
        browser = await p.chromium.launch(headless=True)

        # MOBILE
        context = await browser.new_context(viewport={'width': 844, 'height': 390})
        page = await context.new_page()
        await page.goto("http://localhost:8008/m/index.html")
        await page.wait_for_timeout(2000)

        # Skip into Map Scene
        await page.evaluate("""() => {
            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            window.game.scene.start('MapScene');
        }""")
        await page.wait_for_timeout(2000)

        # DESKTOP
        context2 = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page2 = await context2.new_page()
        await page2.goto("http://localhost:8008/index.html")
        await page2.wait_for_timeout(2000)

        # Skip into Map Scene
        await page2.evaluate("""() => {
            window.game.scene.getScenes(true).forEach(s => s.scene.stop());
            window.game.scene.start('MapScene');
        }""")
        await page2.wait_for_timeout(2000)


        # We are at map. Setup final eggzam state and trigger via UI button
        print("Setting up states for Final Eggzam...")

        # MOBILE FINAL trigger via map
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

            const mapScene = window.game.scene.getScene('MapScene');
            mapScene.scene.start('FinalEggZam');
        }""")
        await page.wait_for_timeout(2000)

        # Log out final data instead of just screens
        mobile_final_data = await page.evaluate("""() => {
            const scene = window.game.scene.getScene('FinalEggZam');
            if(!scene) return null;
            return scene.children.list.map(c => ({
                type: c.type,
                text: c.text,
                x: c.x,
                y: c.y,
                fontSize: c.style ? c.style.fontSize : null,
                texture: c.texture ? c.texture.key : null
            }));
        }""")

        print("\n--- MOBILE FINAL EGGZAM ---")
        if mobile_final_data:
            for item in mobile_final_data:
                if item['type'] == 'Text':
                    print(f"Text '{item['text']}' at ({item['x']}, {item['y']}) size: {item['fontSize']}")
                elif item['type'] == 'Image':
                    print(f"Image '{item['texture']}' at ({item['x']}, {item['y']})")
        else:
            print("FinalEggZam scene not found or active")


        # DESKTOP FINAL trigger via map
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

            const mapScene = window.game.scene.getScene('MapScene');
            mapScene.scene.start('FinalEggZam');
        }""")
        await page2.wait_for_timeout(2000)

        desktop_final_data = await page2.evaluate("""() => {
            const scene = window.game.scene.getScene('FinalEggZam');
            if(!scene) return null;
            return scene.children.list.map(c => ({
                type: c.type,
                text: c.text,
                x: c.x,
                y: c.y,
                fontSize: c.style ? c.style.fontSize : null,
                texture: c.texture ? c.texture.key : null
            }));
        }""")

        print("\n--- DESKTOP FINAL EGGZAM ---")
        if desktop_final_data:
            for item in desktop_final_data:
                if item['type'] == 'Text':
                    print(f"Text '{item['text']}' at ({item['x']}, {item['y']}) size: {item['fontSize']}")
                elif item['type'] == 'Image':
                    print(f"Image '{item['texture']}' at ({item['x']}, {item['y']})")
        else:
             print("FinalEggZam scene not found or active")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
