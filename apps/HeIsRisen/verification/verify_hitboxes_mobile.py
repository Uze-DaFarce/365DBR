from playwright.sync_api import sync_playwright
import time

def test_hitboxes():
    with sync_playwright() as p:
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

        # Test coordinates of the hitboxes
        res = m_page.evaluate("""
            () => {
               const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
               return scene.mapZones.map(z => {
                   const hit = z.getBounds();
                   return { name: z.name, x: z.x, y: z.y, bounds: hit };
               });
            }
        """)
        print("Mobile Hitboxes:")
        for r in res:
            print(r)

        m_browser.close()

if __name__ == '__main__':
    test_hitboxes()
