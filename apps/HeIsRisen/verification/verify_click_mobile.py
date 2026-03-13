from playwright.sync_api import sync_playwright
import time

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8080/m/")

        # Bypass intro
        page.evaluate("""
            window.localStorage.setItem('musicVolume', '0.0');
            window.localStorage.setItem('ambientVolume', '0.0');
            window.localStorage.setItem('sfxVolume', '0.0');
        """)
        page.reload()
        page.wait_for_selector("canvas", timeout=10000)
        time.sleep(1)
        # Click past "Tap anywhere to start"
        page.mouse.click(200, 400)
        time.sleep(1)
        # Click past "PLAY NOW"
        page.mouse.click(200, 400)
        time.sleep(2)

        # Force map scene
        page.evaluate("""window.game.scene.scenes[0].scene.start('MapScene')""")
        time.sleep(2)

        # Mammoth Hot Springs coordinates
        page.mouse.click(293, 110)
        time.sleep(1)

        scene = page.evaluate("window.game.scene.scenes.find(s => s.scene.isActive()).scene.key")
        print(f"Active scene after click (mobile): {scene}")

        browser.close()

if __name__ == '__main__':
    test_click()
