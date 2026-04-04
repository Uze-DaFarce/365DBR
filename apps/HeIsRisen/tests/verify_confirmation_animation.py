import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_confirmation_test():
    print(f"\n=== Testing Confirmation Animation (Desktop) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")

    server_process = th.start_server(app_dir)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})

            page = context.new_page()
            th.init_global_bypasses(page)

            page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
            page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            th.wait_for_phaser_init(page)

            print("Starting game via Spacebar...")
            time.sleep(1)
            # Need to create the confirmation dialog in MainMenu before Spacebar is pressed, or trigger it via UI

            # We'll trigger it from the UI Scene's reset button since that's a stable way to open it
            print("Opening UI Settings to click Reset...")
            page.keyboard.press("Space")
            time.sleep(3)
            page.keyboard.press("Space")
            time.sleep(2)
            th.wait_for_active_scene(page, "MapScene")

            page.evaluate("""
                () => {
                    const uiScene = window.game.scene.getScene('UIScene');
                    if (uiScene && uiScene.settingsContainer) {
                         uiScene.settingsContainer.setVisible(true);
                         // Find the Reset button text to click it
                         const resetBtn = uiScene.settingsContainer.list.find(c => c.type === 'Container' && c.list.find(child => child.type === 'Text' && child.text === 'Reset Game'));
                         if (resetBtn) {
                             resetBtn.emit('pointerdown');
                         }
                    }
                }
            """)

            # mid animation frame
            time.sleep(0.05)
            page.screenshot(path=os.path.join(script_dir, "confirmation_desktop_mid.png"))
            print("Captured mid animation")

            # end animation frame
            time.sleep(0.3)
            page.screenshot(path=os.path.join(script_dir, "confirmation_desktop_end.png"))
            print("Captured end animation")

            browser.close()
    finally:
        server_process.terminate()

def run_confirmation_test_mobile():
    print(f"\n=== Testing Confirmation Animation (Mobile) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..", "m")

    server_process = th.start_server(app_dir)

    try:
        with sync_playwright() as p:
            iphone = p.devices['iPhone 12']
            browser = p.chromium.launch(headless=True)
            landscape_viewport = {'width': iphone['viewport']['height'], 'height': iphone['viewport']['width']}
            context = browser.new_context(
                viewport=landscape_viewport,
                user_agent=iphone['user_agent'],
                device_scale_factor=iphone['device_scale_factor'],
                is_mobile=iphone['is_mobile'],
                has_touch=iphone['has_touch']
            )

            page = context.new_page()
            th.init_global_bypasses(page)

            page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
            page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            th.wait_for_phaser_init(page)

            print("Starting game via Spacebar...")
            time.sleep(1)
            page.keyboard.press("Space")
            time.sleep(3)
            page.keyboard.press("Space")
            time.sleep(2)
            th.wait_for_active_scene(page, "MapScene")

            # Open confirmation dialog
            page.evaluate("""
                () => {
                    const uiScene = window.game.scene.getScene('UIScene');
                    if (uiScene && uiScene.settingsContainer) {
                         uiScene.settingsContainer.setVisible(true);
                         // Find the Reset button text to click it
                         const resetBtn = uiScene.settingsContainer.list.find(c => c.type === 'Container' && c.list.find(child => child.type === 'Text' && child.text === 'Reset Game'));
                         if (resetBtn) {
                             resetBtn.emit('pointerdown');
                         }
                    }
                }
            """)

            # mid animation frame
            time.sleep(0.05)
            page.screenshot(path=os.path.join(script_dir, "confirmation_mobile_mid.png"))
            print("Captured mid animation")

            # end animation frame
            time.sleep(0.3)
            page.screenshot(path=os.path.join(script_dir, "confirmation_mobile_end.png"))
            print("Captured end animation")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_confirmation_test()
    run_confirmation_test_mobile()
