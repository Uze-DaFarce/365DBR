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

        bounds = page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               const z = scene.mapZones[0]; // Mammoth

               // generate hits with CURRENT implementation
               const hits = [];
               for(let dx = -300; dx <= 300; dx+=10) {
                   for(let dy = -300; dy <= 300; dy+=10) {
                        const px = z.x + dx;
                        const py = z.y + dy;
                        if(scene.sys.input.manager.hitTest({x: px, y: py}, [z], scene.cameras.main)[0] === z) {
                            hits.push({dx, dy});
                        }
                   }
               }

               return {
                    zX: z.x,
                    zY: z.y,
                    hitCount: hits.length,
                    minDx: hits.length > 0 ? Math.min(...hits.map(h => h.dx)) : null,
                    maxDx: hits.length > 0 ? Math.max(...hits.map(h => h.dx)) : null,
                    minDy: hits.length > 0 ? Math.min(...hits.map(h => h.dy)) : null,
                    maxDy: hits.length > 0 ? Math.max(...hits.map(h => h.dy)) : null,
               };
            }
        """)

        print(f"Container data (after removed params): {bounds}")
        browser.close()

if __name__ == '__main__':
    test_click()
