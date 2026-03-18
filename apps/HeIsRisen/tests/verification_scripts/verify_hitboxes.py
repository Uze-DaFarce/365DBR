from playwright.sync_api import sync_playwright
import time

def test_hitboxes():
    with sync_playwright() as p:
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

        # Test coordinates of the hitboxes
        res = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               return scene.mapZones.map(z => {
                   const hit = z.getBounds();
                   return { name: z.name, x: z.x, y: z.y, bounds: hit };
               });
            }
        """)
        print("Desktop Hitboxes:")
        for r in res:
            print(r)

        browser.close()

if __name__ == '__main__':
    test_hitboxes()
