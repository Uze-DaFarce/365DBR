from playwright.sync_api import sync_playwright
import time

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8080/")

        page.evaluate("""
            window.localStorage.setItem('musicVolume', '0.0');
            window.localStorage.setItem('ambientVolume', '0.0');
            window.localStorage.setItem('sfxVolume', '0.0');
        """)
        page.reload()
        page.wait_for_selector("canvas", timeout=10000)
        time.sleep(1)
        page.mouse.click(640, 360)
        time.sleep(1)
        page.mouse.click(640, 360)
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
        # bounds are: {'name': 'mammoth-hot-springs', 'x': 293.125, 'y': 110.625, 'geomX': 0, 'geomY': 0, 'geomW': 179, 'geomH': 104}
        print("Clicking exact center of Mammoth Hot Springs (293, 110)")
        page.mouse.click(293, 110)
        time.sleep(1)

        res = page.evaluate("window.clickedTargets")
        print(f"Captured targets from center tap: {res}")

        browser.close()

if __name__ == '__main__':
    test_click()
