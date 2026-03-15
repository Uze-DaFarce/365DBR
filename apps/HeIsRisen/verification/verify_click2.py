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

        # Test coordinates of yellowstone history: 983, 363
        page.mouse.click(983, 363)
        time.sleep(1)

        scene = page.evaluate("window.game.scene.scenes.find(s => s.scene.isActive()).scene.key")
        print(f"Active scene after click 2: {scene}")

        browser.close()

if __name__ == '__main__':
    test_click()
