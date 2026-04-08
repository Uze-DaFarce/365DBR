import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_test(is_mobile=False):
    context_type = "mobile" if is_mobile else "desktop"
    print(f"\n=== Testing Inner State Corruption Resilience ({context_type}) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")

    server_process = th.start_server(app_dir)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            if is_mobile:
                iphone = p.devices['iPhone 12']
                context = browser.new_context(viewport={'width': iphone['viewport']['height'], 'height': iphone['viewport']['width']}, is_mobile=True, has_touch=True)
            else:
                context = browser.new_context(viewport={'width': 1280, 'height': 720})

            page = context.new_page()
            url = "http://127.0.0.1:8080/m/" if is_mobile else "http://127.0.0.1:8080/"

            # Go to blank page on same origin
            page.goto("http://127.0.0.1:8080/index.html")

            page.evaluate("""
                () => {
                    const corruptedState = {
                        eggData: ["corrupt_string", null, { eggId: "12", no_x: true, section: "TheEmptyTomb" }],
                        sections: [{ name: null }, "string"],
                        foundEggs: ["string", null],
                        stampedSections: [123, null],
                        correctCategorizations: 0,
                        currentScore: 0
                    };
                    localStorage.setItem('heIsRisenGameState', JSON.stringify(corruptedState));
                }
            """)

            errors = []
            page.on('pageerror', lambda e: errors.append(e.message))
            page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))

            page.goto(url)
            page.wait_for_load_state('networkidle')

            th.wait_for_phaser_init(page)

            # Start Game
            time.sleep(1)
            page.keyboard.press("Space")
            time.sleep(3)
            page.keyboard.press("Space")
            time.sleep(2)

            print("Attempting to load MapScene...")
            th.wait_for_active_scene(page, "MapScene")

            # Validate that the arrays were fresh initialized instead of keeping corrupted ones
            eggData_len = page.evaluate("() => window.game.scene.scenes[0].registry.get('eggData').length")
            print(f"eggData length: {eggData_len}")

            if eggData_len != 60:
                raise AssertionError(f"Expected 60 fresh eggs, got {eggData_len}")

            if len(errors) > 0:
                print("Captured Page Errors:")
                for e in errors:
                    print(e)
                raise AssertionError("Page threw JavaScript errors due to corrupted state.")

            print("SUCCESS: Inner array corruption safely caught and game initialized fresh.")

            # Inject a visual dialog to show the user what was tested and how it was resolved
            page.evaluate(f"""
                () => {{
                    const dialog = document.createElement('div');
                    dialog.style.position = 'absolute';
                    dialog.style.top = '10%';
                    dialog.style.left = '10%';
                    dialog.style.width = '80%';
                    dialog.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
                    dialog.style.border = '4px solid #ff0000';
                    dialog.style.borderRadius = '10px';
                    dialog.style.color = '#ffffff';
                    dialog.style.fontFamily = '"Comic Sans MS", cursive, sans-serif';
                    dialog.style.padding = '20px';
                    dialog.style.zIndex = '999999';
                    dialog.style.boxSizing = 'border-box';

                    dialog.innerHTML = `
                        <h2 style="color: #ffff00; margin-top: 0; text-align: center;">🛡️ Sentinel: Inner Array Corruption Test</h2>
                        <p style="text-align: center; color: #ff9999;">Attempted to load game with deeply corrupted arrays (e.g. eggData containing nulls and strings instead of objects).</p>
                        <h3 style="color: #00ff00; text-align: center; margin-bottom: 0;">✅ SUCCESS: Corruption Rejected, Fresh State Loaded Safely</h3>
                    `;

                    const targetContainer = document.fullscreenElement || document.webkitFullscreenElement || document.body;
                    targetContainer.appendChild(dialog);
                }}
            """)

            time.sleep(1)
            os.makedirs("verification", exist_ok=True)
            screenshot_path = f"verification/inner_corruption_{context_type}.png"
            page.screenshot(path=screenshot_path)
            print(f"Captured screenshot proof at: {screenshot_path}")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_test(False)
    run_test(True)
