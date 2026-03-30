import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright
import test_helpers as th

def capture_cursor_visual(is_mobile=False):
    server_process = subprocess.Popen(["python3", "-m", "http.server", "8080"])
    time.sleep(2)

    screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)

    try:
        with sync_playwright() as p:
            if is_mobile:
                # Use a specific mobile device viewport, e.g. iPhone XR
                device = p.devices['iPhone XR']
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(**device)
                prefix = "mobile"
                url = "http://127.0.0.1:8080/m/"
            else:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1280, 'height': 720})
                prefix = "desktop"
                url = "http://127.0.0.1:8080/"

            page = context.new_page()
            th.init_global_bypasses(page)

            print(f"[{prefix.upper()}] Loading application...")
            page.goto(url)
            page.wait_for_load_state('networkidle')
            th.wait_for_phaser_init(page)

            # Skip to SectionHunt directly
            print(f"[{prefix.upper()}] Bypassing to SectionHunt...")
            page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('SectionHunt', { sectionName: 'old-faithful' })")
            th.wait_for_active_scene(page, "SectionHunt")

            # Wait for any intros/fade-ins
            time.sleep(3)

            # Move the mouse to the center of the screen to ensure the custom cursor tracks to it
            viewport = page.viewport_size
            center_x = viewport['width'] / 2
            center_y = viewport['height'] / 2

            print(f"[{prefix.upper()}] Moving pointer to ({center_x}, {center_y})...")
            # In Playwright, mouse.move explicitly dispatches a pointermove event, which Phaser listens to
            page.mouse.move(center_x, center_y, steps=10)

            # Wait for Phaser to render the cursor at the new position
            time.sleep(1)

            screenshot_path = os.path.join(screenshots_dir, f"{prefix}_cursor_verify.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[{prefix.upper()}] Screenshot captured: {screenshot_path}")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    capture_cursor_visual(is_mobile=False)
    capture_cursor_visual(is_mobile=True)
