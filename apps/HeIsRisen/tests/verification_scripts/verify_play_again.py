from playwright.sync_api import sync_playwright
import time
import os

def test_play_again():
    print("Testing PLAY AGAIN button on Desktop and Mobile...")
    with sync_playwright() as p:
        # Desktop
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
        page.screenshot(path="verification/desktop_play_again.png")
        print("Saved desktop_play_again.png")
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
        time.sleep(2)
        m_page.mouse.click(200, 400)
        time.sleep(2)
        m_page.mouse.click(200, 400)
        time.sleep(2)

        m_page.evaluate("""
            // Fake foundEggs to match TOTAL_EGGS (60)
            const fakeFoundEggs = Array.from({length: 60}, (_, i) => ({
                eggId: 'fake'+i, categorized: true
            }));
            // Add one real uncategorized egg to sort
            fakeFoundEggs[0] = {eggId: 'e1', categorized: false, symbolData: { name: 'Cross', category: 'Christian' }};
            window.game.scene.scenes[0].registry.set('foundEggs', fakeFoundEggs);
            window.game.scene.start('EggZamRoom');
        """)

        time.sleep(3)
        # Click left bottle (rough coordinates for mobile)
        m_page.mouse.click(200, 600)
        time.sleep(2)
        # Dismiss modal
        m_page.mouse.click(360, 400)
        time.sleep(2)

        m_page.screenshot(path="verification/mobile_play_again.png")
        print("Saved mobile_play_again.png")
        m_browser.close()

if __name__ == '__main__':
    test_play_again()
