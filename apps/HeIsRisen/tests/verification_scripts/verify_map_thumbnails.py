from playwright.sync_api import sync_playwright
import time
import os

def test_map_thumbnails():
    print("Testing map thumbnails visibility on Desktop and Mobile...")
    with sync_playwright() as p:
        os.makedirs("verification", exist_ok=True)
        # Desktop
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8080/")

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
        page.mouse.click(640, 360)
        time.sleep(1)
        # Click past "PLAY NOW"
        page.mouse.click(640, 360)
        time.sleep(2)

        # Force map scene
        page.evaluate("""window.game.scene.scenes[0].scene.start('MapScene')""")
        time.sleep(2)

        page.screenshot(path="verification/desktop_map_scene.png")
        print("Saved desktop_map_scene.png")
        browser.close()

        # Mobile
        m_browser = p.chromium.launch(headless=True)
        m_page = m_browser.new_page()
        m_page.goto("http://localhost:8080/m/")

        m_page.evaluate("""
            window.localStorage.setItem('musicVolume', '0.0');
            window.localStorage.setItem('ambientVolume', '0.0');
            window.localStorage.setItem('sfxVolume', '0.0');
        """)
        m_page.reload()
        m_page.wait_for_selector("canvas", timeout=10000)
        time.sleep(1)
        m_page.mouse.click(200, 400)
        time.sleep(1)
        m_page.mouse.click(200, 400)
        time.sleep(2)

        m_page.evaluate("""window.game.scene.scenes[0].scene.start('MapScene')""")
        time.sleep(2)

        m_page.screenshot(path="verification/mobile_map_scene.png")
        print("Saved mobile_map_scene.png")
        m_browser.close()

if __name__ == '__main__':
    test_map_thumbnails()
