import time
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def run_test():
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../apps/HeIsRisen/tests'))
    import test_helpers as th

    server_process = th.start_server('apps/HeIsRisen')
    url = "http://127.0.0.1:8080/m/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # intercept video request and delay it
        page.route("**/*.mp4", lambda route: (time.sleep(5), route.continue_()))

        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Mute audio output
        page.evaluate("() => { window.localStorage.setItem('musicVolume', '0.0'); window.localStorage.setItem('ambientVolume', '0.0'); window.localStorage.setItem('sfxVolume', '0.0'); }")

        th.wait_for_phaser_init(page)
        time.sleep(1)

        # Use keyboard to start game since mobile might have invisible container logic
        page.keyboard.press("Space")
        time.sleep(3) # Wait for start screen tween
        page.keyboard.press("Space")
        time.sleep(2) # Wait for MapScene

        th.wait_for_active_scene(page, "MapScene")

        # Force unlocking tomb section and simulate transitioning to it
        page.evaluate("""() => {
            const scene = window.game.scene.scenes.find(s => s.scene.key === 'MapScene');
            scene.scene.start('SectionHunt', { sectionName: 'tomb' });
        }""")
        time.sleep(1)

        # Verify SectionHunt is active
        th.wait_for_active_scene(page, "SectionHunt")

        # Move mouse to show magnifying glass
        page.mouse.move(300, 300)
        page.mouse.down()
        page.mouse.move(301, 301) # ensure input event registers
        time.sleep(1) # still delaying video here

        # Take screenshot of the fallback texture in the lens
        page.screenshot(path="verification/mobile_slow_video_lens.png")
        print("Captured mobile_slow_video_lens.png successfully!")

        browser.close()

    server_process.terminate()

if __name__ == "__main__":
    run_test()
