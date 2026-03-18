from playwright.sync_api import sync_playwright
import time
import sys
import os

def verify_stamp():
    print("Starting frontend verification for Level-Complete Stamp and Volumes...")
    with sync_playwright() as p:
        # ---- 1. Test Desktop View ----
        print("Testing Desktop View...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:8080/")
        page.evaluate("""
            window.localStorage.setItem('musicVolume', '0.2');
            window.localStorage.setItem('ambientVolume', '0.2');
            window.localStorage.setItem('sfxVolume', '0.2');
        """)
        page.reload()

        page.wait_for_selector("canvas", timeout=10000)
        time.sleep(2)
        page.mouse.click(640, 360)
        time.sleep(2)
        page.mouse.click(640, 360)
        time.sleep(2)

        # Inject completed state
        page.evaluate("""
            const mapScene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
            if (mapScene) {
                const eggDataArray = mapScene.registry.get('eggData');
                if (eggDataArray) {
                    const gpEggs = eggDataArray.filter(e => e.section === 'grand-prismatic');
                    // Format explicitly using the format foundEggs expects to trigger completion
                    const formattedGpEggs = gpEggs.map(e => ({ eggId: e.eggId }));
                    window.game.scene.scenes[0].registry.set('foundEggs', formattedGpEggs);
                    mapScene.scene.restart();
                }
            }
        """)

        print("Waiting for MapScene restart...")
        time.sleep(3)

        # Assertion: Check if stamps array has length > 0
        stamps_count = page.evaluate("""
            const mapScene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
            mapScene.stamps ? mapScene.stamps.length : 0;
        """)
        print(f"Desktop Stamp Overlays Found: {stamps_count}")
        if stamps_count == 0:
            print("ERROR: Desktop level-complete stamp was NOT rendered!")
            sys.exit(1)

        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/desktop_stamp.png")
        print("Saved desktop_stamp.png")

        browser.close()

        # ---- 2. Test Mobile View ----
        print("Testing Mobile View...")
        mobile_browser = p.chromium.launch(headless=True)
        mobile_context = mobile_browser.new_context()
        mobile_page = mobile_context.new_page()

        mobile_page.goto("http://localhost:8080/m/")
        mobile_page.evaluate("""
            window.localStorage.setItem('musicVolume', '0.3');
            window.localStorage.setItem('ambientVolume', '0.3');
            window.localStorage.setItem('sfxVolume', '0.3');
        """)
        mobile_page.reload()

        mobile_page.wait_for_selector("canvas", timeout=10000)
        time.sleep(2)
        mobile_page.mouse.click(200, 400)
        time.sleep(2)
        mobile_page.mouse.click(200, 400)
        time.sleep(2)

        mobile_page.evaluate("""
            const mapSceneM = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
            if (mapSceneM) {
                const eggDataArray = mapSceneM.registry.get('eggData');
                if (eggDataArray) {
                    const gpEggs = eggDataArray.filter(e => e.section === 'grand-prismatic');
                    const formattedGpEggs = gpEggs.map(e => ({ eggId: e.eggId }));
                    window.game.scene.scenes[0].registry.set('foundEggs', formattedGpEggs);
                    mapSceneM.scene.restart();
                }
            }
        """)

        time.sleep(3)

        m_stamps_count = mobile_page.evaluate("""
            const mapSceneM = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
            mapSceneM.stamps ? mapSceneM.stamps.length : 0;
        """)
        print(f"Mobile Stamp Overlays Found: {m_stamps_count}")
        if m_stamps_count == 0:
            print("ERROR: Mobile level-complete stamp was NOT rendered!")
            sys.exit(1)

        mobile_page.screenshot(path="verification/mobile_stamp.png")
        print("Saved mobile_stamp.png")

        mobile_browser.close()
        print("Verification Successful! Both platforms rendered stamps.")

if __name__ == '__main__':
    verify_stamp()
