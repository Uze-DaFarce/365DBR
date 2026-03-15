from playwright.sync_api import sync_playwright
import time

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        device = p.devices['iPhone 12']
        device['viewport'] = {'width': 844, 'height': 390} # landscape
        context = browser.new_context(
            **device
        )
        page = context.new_page()
        page.goto("http://localhost:8080/m/")

        page.evaluate("""
            window.localStorage.setItem('musicVolume', '0.0');
            window.localStorage.setItem('ambientVolume', '0.0');
            window.localStorage.setItem('sfxVolume', '0.0');
        """)
        page.reload()
        page.wait_for_selector("canvas", timeout=10000)
        time.sleep(1)
        page.mouse.click(200, 400)
        time.sleep(1)
        page.mouse.click(200, 400)
        time.sleep(2)

        page.evaluate("""window.game.scene.scenes[0].scene.start('MapScene')""")
        time.sleep(2)

        page.evaluate("""
            () => {
               window.clickedTargets = [];
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');

               scene.input.on('pointerdown', (pointer, currentlyOver) => {
                   window.currentlyOverList = currentlyOver.map(go => go.name || go.type);
                   window.clickCoords = {x: pointer.x, y: pointer.y};
               });
            }
        """)

        # Offset exactly out of bounds
        pos = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               const z = scene.mapZones[0];
               return {x: z.x, y: z.y};
            }
        """)

        print(f"Tapping EXACT bounds {pos['x']}, {pos['y']}")
        # IMPORTANT: Tapping uses viewport coords
        page.touchscreen.tap(pos['x'], pos['y'])
        time.sleep(1)

        res = page.evaluate("window.currentlyOverList")
        coords = page.evaluate("window.clickCoords")
        print(f"Interactive objects directly under tap at {coords}: {res}")

        browser.close()

if __name__ == '__main__':
    test_click()
