import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def capture_ui():
    print("Starting server for capture...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")

    server_process = subprocess.Popen(
        ["npx", "http-server", "-p", "8080", "-c-1"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2) # wait for server to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            # Global keydown listener to bypass user gesture requirement for AudioContext
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

            # Wait for Phaser
            page.wait_for_function("() => window.game && window.game.scene && window.game.scene.scenes.length > 0")
            time.sleep(1)

            # 1. Skip intro "Click anywhere to start"
            page.keyboard.press("Space")

            # Wait for Play button
            time.sleep(4)

            # 2. Click "Play Now"
            page.keyboard.press("Space")

            # Wait for MapScene to load and render completely
            print("Waiting for MapScene rendering...")
            time.sleep(3)

            # Take screenshot of MapScene
            screenshot_path = os.path.join(app_dir, "verification", "map_scene_desktop.png")
            page.screenshot(path=screenshot_path)
            print(f"Saved desktop screenshot to {screenshot_path}")

            # Navigate to EggZamRoom directly via console to test it too
            page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('EggZamRoom')")
            time.sleep(3)

            # Take screenshot of EggZamRoom
            screenshot_path_egg = os.path.join(app_dir, "verification", "eggzam_room_desktop.png")
            page.screenshot(path=screenshot_path_egg)
            print(f"Saved desktop screenshot to {screenshot_path_egg}")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    capture_ui()
