from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile context
        context_mobile = browser.new_context(
            is_mobile=True,
            has_touch=True,
            viewport={'width': 844, 'height': 390}
        )
        page_mobile = context_mobile.new_page()

        print("Testing Mobile Audio Fix...")
        page_mobile.goto("http://127.0.0.1:8080/apps/HeIsRisen/m/")
        page_mobile.wait_for_timeout(4000)

        # Click to start - mobile intro is 1280x720 scaled to 844x390, just click center
        page_mobile.mouse.click(422, 195)
        page_mobile.wait_for_timeout(4000)

        # Click Play Now
        page_mobile.mouse.click(422, 195)
        page_mobile.wait_for_timeout(4000)

        page_mobile.evaluate("""
            if(window.game && window.game.scene) {
                const mapScene = window.game.scene.getScene('MapScene');
                if(mapScene) {
                    mapScene.scene.start('SectionHunt', { sectionName: 'old-faithful' });
                }
            }
        """)
        page_mobile.wait_for_timeout(3000)

        # Take screenshot of the video section
        page_mobile.screenshot(path="/app/apps/HeIsRisen/verification/08_mobile_video_audio_fix.png")
        context_mobile.close()

        # Desktop context
        context_desktop = browser.new_context(viewport={'width': 1280, 'height': 720})
        page_desktop = context_desktop.new_page()

        print("Testing Desktop Audio Fix...")
        page_desktop.goto("http://127.0.0.1:8080/apps/HeIsRisen/")
        page_desktop.wait_for_timeout(4000)

        # Press Spacebar to start
        page_desktop.keyboard.press("Space")
        page_desktop.wait_for_timeout(4000)

        page_desktop.evaluate("""
            const startBtn = document.getElementById('start-btn');
            if(startBtn) startBtn.click();
        """)
        page_desktop.wait_for_timeout(4000)

        # Force a video section
        page_desktop.evaluate("""
            if(window.game && window.game.scene) {
                const mapScene = window.game.scene.getScene('MapScene');
                if(mapScene) {
                    mapScene.scene.start('SectionHunt', { sectionName: 'old-faithful' });
                }
            }
        """)
        page_desktop.wait_for_timeout(3000)

        page_desktop.screenshot(path="/app/apps/HeIsRisen/verification/08_desktop_video_audio_fix.png")
        context_desktop.close()

        browser.close()

if __name__ == "__main__":
    verify_feature()
