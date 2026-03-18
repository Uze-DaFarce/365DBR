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

        cam = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               return {
                    width: scene.cameras.main.width,
                    height: scene.cameras.main.height,
                    zoom: scene.cameras.main.zoom,
                    x: scene.cameras.main.scrollX,
                    y: scene.cameras.main.scrollY
               };
            }
        """)

        print(f"Camera: {cam}")

        browser.close()

if __name__ == '__main__':
    test_click()
