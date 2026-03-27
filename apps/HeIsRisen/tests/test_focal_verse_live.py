import os
import sys
import subprocess
import time
from playwright.sync_api import sync_playwright

import test_helpers as th

def run_focal_verse_test(is_mobile=False):
    print(f"\\n=== Testing Focal Verse Integration against LIVE 365DBR ({'Mobile' if is_mobile else 'Desktop'}) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..", "..", "..")

    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

    try:
        with sync_playwright() as p:
            if is_mobile:
                iphone = p.devices['iPhone 12']
                browser = p.chromium.launch(headless=True)
                landscape_viewport = {'width': iphone['viewport']['height'], 'height': iphone['viewport']['width']}
                context = browser.new_context(
                    viewport=landscape_viewport,
                    user_agent=iphone['user_agent'],
                    device_scale_factor=iphone['device_scale_factor'],
                    is_mobile=iphone['is_mobile'],
                    has_touch=iphone['has_touch'],
                    record_video_dir=os.path.join(script_dir, "verification_videos")
                )
            else:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    record_video_dir=os.path.join(script_dir, "verification_videos")
                )

            page = context.new_page()
            app_path = "m/index.html" if is_mobile else "index.html"
            page.goto(f"http://127.0.0.1:8080/apps/HeIsRisen/{app_path}")

            page.wait_for_selector('canvas', state='visible', timeout=10000)
            time.sleep(2)

            print("Entering game naturally...")
            if is_mobile:
                page.mouse.click(195, 600)
            else:
                page.mouse.click(640, 500)
            time.sleep(2)

            page.mouse.click(10, 10)
            time.sleep(2)

            if is_mobile:
                page.mouse.click(350, 150)
            else:
                page.mouse.click(500, 300)
            time.sleep(3)

            # Use Playwright UI clicking logic instead of unreliable evaluating injection!
            # Since HeIsRisen has a predictable layout for level 1:
            print("Clicking randomly around screen to collect egg...")
            for x in range(100, 1200, 50):
                for y in range(100, 700, 50):
                    page.mouse.click(x, y)
                    time.sleep(0.01)

            time.sleep(2)

            # Click bottom left to categorize
            print("Categorizing Egg...")
            if is_mobile:
                page.mouse.click(100, 350)
            else:
                page.mouse.click(300, 600)
            time.sleep(2)

            # Click scripture link in the popup!
            print("Clicking scripture link...")
            if is_mobile:
                page.mouse.click(422, 345) # Mobile scripture link roughly bottom middle
            else:
                page.mouse.click(640, 576) # Desktop scripture link roughly bottom middle

            print("Waiting 10 seconds for LIVE 365DBR iframe to load and scroll...")
            time.sleep(10)

            iframe_count = page.locator("iframe").count()
            if iframe_count == 0:
                 # Backup fallback logic just in case the UI click missed
                 print("UI click missed, falling back to finding the exact node via eval...")
                 page.evaluate("""() => {
                    const game = window.game;
                    if (!game) return;
                    const mainScene = game.scene.getScene('MainScene');
                    if (mainScene && mainScene.explanationText) {
                        const list = mainScene.explanationText.list;
                        const verseTextObj = list.find(obj => obj.type === 'Text' && obj.style.color === '#0000ee');
                        if (verseTextObj) {
                            verseTextObj.emit('pointerdown', { stopPropagation: () => {} }, verseTextObj.x, verseTextObj.y, { stopPropagation: () => {} });
                        }
                    }
                 }""")
                 time.sleep(10)

            iframe_count = page.locator("iframe").count()
            assert iframe_count > 0, "Iframe was not appended to the DOM!"
            print(f"Found {iframe_count} iframes on page.")

            os.makedirs(os.path.join(script_dir, "verification_screenshots"), exist_ok=True)
            screenshot_name = f"focal_verse_live_{'mobile' if is_mobile else 'desktop'}.png"
            screenshot_path = os.path.join(script_dir, "verification_screenshots", screenshot_name)
            page.screenshot(path=screenshot_path)
            print(f"Saved screenshot to {screenshot_path}")

            context.close()
            browser.close()

    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_focal_verse_test(is_mobile=False)
    run_focal_verse_test(is_mobile=True)
