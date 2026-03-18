from playwright.sync_api import sync_playwright
import time

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
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

        # Test coordinates of the hitboxes
        res = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               const z = scene.mapZones[0];
               const bounds = z.getBounds();
               return {
                    name: z.name,
                    x: z.x,
                    y: z.y,
                    containerBounds: bounds,
                    hitArea: z.input.hitArea,
                    hitAreaCenter: { x: z.input.hitArea.x + z.input.hitArea.width/2, y: z.input.hitArea.y + z.input.hitArea.height/2 }
               };
            }
        """)
        print("Hitbox geometry:", res)

        browser.close()

if __name__ == '__main__':
    test_click()
