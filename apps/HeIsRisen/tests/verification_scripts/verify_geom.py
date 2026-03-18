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

        geom = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               const z = scene.mapZones[0];
               return {
                    x: z.x, y: z.y,
                    geomRect: z.input.hitArea,
                    scaleX: z.scaleX, scaleY: z.scaleY,
                    displayWidth: z.displayWidth, displayHeight: z.displayHeight,
                    width: z.width, height: z.height,
                    hitTestAtCenter: Phaser.Geom.Rectangle.Contains(z.input.hitArea, 0, 0)
               };
            }
        """)

        print(f"Container data: {geom}")

        browser.close()

if __name__ == '__main__':
    test_click()
