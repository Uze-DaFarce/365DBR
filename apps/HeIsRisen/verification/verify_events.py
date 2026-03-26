from playwright.sync_api import sync_playwright
import time

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(has_touch=True, is_mobile=True, viewport={'width': 640, 'height': 360})
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

        # Inject an event listener to intercept pointer events
        page.evaluate("""
            () => {
               window.clickedTargets = [];
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               scene.input.on('gameobjectdown', (pointer, gameObject) => {
                   window.clickedTargets.push(gameObject.name || gameObject.type);
               });
            }
        """)

        # Mammoth Hot Springs center
        print("Tapping exact center of Mammoth Hot Springs (146, 55)")
        page.touchscreen.tap(146, 55)
        time.sleep(1)

        res = page.evaluate("window.clickedTargets")
        print(f"Captured targets from center tap: {res}")

        browser.close()

if __name__ == '__main__':
    test_click()
