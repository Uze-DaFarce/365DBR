import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_missing_network_data_test(is_mobile=False):
    context_type = "mobile" if is_mobile else "desktop"
    print(f"\n=== Testing Missing Network Data Resilience ({context_type.capitalize()}) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")

    server_process = th.start_server(app_dir)

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
                    has_touch=iphone['has_touch']
                )
            else:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1280, 'height': 720})

            # Block the network request for symbols.json
            context.route("**/symbols.json", lambda route: route.abort("internetdisconnected"))

            page = context.new_page()
            th.init_global_bypasses(page)

            url = "http://127.0.0.1:8080/m/" if is_mobile else "http://127.0.0.1:8080/"

            print("Loading page and blocking symbols.json...")
            page.goto(url)
            page.wait_for_load_state('networkidle')

            # Wait for Phaser to initialize or fail gracefully
            time.sleep(2)

            try:
                # Try to interact to see if it crashed
                page.keyboard.press("Space")
                time.sleep(3)
                page.keyboard.press("Space")
                time.sleep(2)

                # Check if we made it to the map scene, or if the game handles the missing data
                # It might get stuck on loading, or might load but with empty symbols
                scenes = page.evaluate("() => { try { return window.game.scene.scenes.map(s => ({key: s.sys.config.key, active: s.sys.isActive()})); } catch(e) { return null; } }")

                print(f"Current scenes state: {scenes}")

                # Check if eggData is in registry
                has_egg_data = page.evaluate("() => { try { return window.game.scene.scenes[0].registry.has('eggData'); } catch(e) { return false; } }")
                print(f"Has eggData in registry: {has_egg_data}")

                if has_egg_data:
                    egg_data = page.evaluate("() => window.game.scene.scenes[0].registry.get('eggData')")
                    # Check if symbol is handled gracefully when missing
                    symbol_handled = all(egg.get('symbol') is None for egg in egg_data)
                    print(f"Are all symbols safely None/null? {symbol_handled}")
                    if not symbol_handled:
                        print("WARNING: Some symbols are not None despite blocking symbols.json")

                # Capture visual proof
                os.makedirs("verification", exist_ok=True)
                screenshot_path = f"verification/missing_network_data_{context_type}.png"
                page.screenshot(path=screenshot_path)
                print(f"Captured screenshot proof at: {screenshot_path}")

            except Exception as e:
                print(f"Game crashed or failed to load properly due to missing data: {e}")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_missing_network_data_test(is_mobile=False)
    run_missing_network_data_test(is_mobile=True)
