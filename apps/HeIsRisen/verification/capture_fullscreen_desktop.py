import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def capture_ui():
    print("Starting server for fullscreen capture...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")

    server_process = subprocess.Popen(
        ["npx", "http-server", "-p", "8080", "-c-1"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--start-fullscreen'])
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            page.add_init_script("""
                window.addEventListener('keydown', (e) => {
                    if (e.code === 'Space' || e.code === 'Enter') {
                        // Let Phaser handle it via its own listener
                    }
                });
            """)

            print("Navigating to app...")
            page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            page.wait_for_function("() => window.game && window.game.scene && window.game.scene.scenes.length > 0")
            time.sleep(1)

            print("Simulating pointerdown to trigger requestFullscreen()...")
            page.mouse.click(960, 540)
            time.sleep(4)
            page.mouse.click(960, 1080 * 0.8)

            print("Waiting for MapScene rendering in fullscreen context...")
            time.sleep(4)

            # Save the screenshot directly to the directory so it's committed
            screenshot_path = os.path.join(app_dir, "verification", "map_scene_fullscreen.png")
            page.screenshot(path=screenshot_path)
            print(f"Saved fullscreen screenshot to {screenshot_path}")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    capture_ui()
