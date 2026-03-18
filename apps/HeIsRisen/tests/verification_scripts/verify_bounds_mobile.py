from playwright.sync_api import sync_playwright
import time

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Enable hasTouch
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

        # Test coordinates of the hitboxes
        res = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               return scene.mapZones.map(z => {
                   return {
                       name: z.name,
                       hitAreaCenter: { x: z.x, y: z.y }
                   }
               });
            }
        """)
        for r in res:
            print(f"Tapping {r['name']} at X:{r['hitAreaCenter']['x']}, Y:{r['hitAreaCenter']['y']}")
            page.touchscreen.tap(r['hitAreaCenter']['x'], r['hitAreaCenter']['y'])
            time.sleep(0.5)
            active = page.evaluate("window.game.scene.scenes.find(s => s.scene.isActive()).scene.key")
            if active == "SectionHunt":
                print(f"SUCCESS: {r['name']} clicked")
                page.evaluate("""window.game.scene.scenes.find(s => s.scene.isActive()).scene.start('MapScene')""")
                time.sleep(1)
            else:
                print(f"FAILED: {r['name']} did not transition")

        browser.close()

if __name__ == '__main__':
    test_click()
