from playwright.sync_api import sync_playwright
import time
import os

def test_play_again_fix():
    print("Testing PLAY AGAIN button on Desktop (Checking if it's hidden when not complete)...")
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
        time.sleep(2)
        page.mouse.click(640, 360)
        time.sleep(2)
        page.mouse.click(640, 360)
        time.sleep(2)

        page.evaluate("""
            const eggData = [
                { eggId: 'e1', symbolData: { name: 'Cross', category: 'Christian' }, categorized: false }
            ];
            window.game.scene.scenes[0].registry.set('eggData', eggData);
            window.game.scene.scenes[0].registry.set('foundEggs', [{eggId: 'e1', categorized: false, symbolData: { name: 'Cross', category: 'Christian' }}]);
            window.game.scene.start('EggZamRoom');
        """)

        time.sleep(3)
        # Click left bottle to categorize the single egg
        page.mouse.click(360, 500)
        time.sleep(2)
        # Click the modal to dismiss explanation
        page.mouse.click(640, 360)
        time.sleep(2)

        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/desktop_play_again_fix.png")
        print("Saved desktop_play_again_fix.png")
        browser.close()

if __name__ == '__main__':
    test_play_again_fix()
