import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_game_state_validation_test(is_mobile=False):
    context_type = "mobile" if is_mobile else "desktop"
    print(f"\n=== Testing Game State Validation ({context_type.capitalize()}) ===")

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

            page = context.new_page()
            th.init_global_bypasses(page)

            url = "http://127.0.0.1:8080/m/" if is_mobile else "http://127.0.0.1:8080/"

            # Go to a blank page on the same origin first to set local storage
            page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
            page.goto("http://127.0.0.1:8080/index.html")

            page.evaluate("""
                () => {
                    localStorage.setItem('highScore', '100');
                    localStorage.setItem('musicVolume', '0.8');
                    localStorage.setItem('ambientVolume', '0.2');
                    localStorage.setItem('sfxVolume', '0.7');
                }
            """)

            page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
            page.goto(url)
            page.wait_for_load_state('networkidle')

            th.wait_for_phaser_init(page)

            # Start Game to activate Audio Context
            time.sleep(1)
            page.keyboard.press("Space")
            time.sleep(3) # Wait for start screen tween
            page.keyboard.press("Space")
            time.sleep(2) # Wait for MapScene

            th.wait_for_active_scene(page, "MapScene")

            # Verify high score was loaded correctly
            high_score = page.evaluate("() => window.game.scene.scenes[0].registry.get('highScore')")
            print(f"High Score after valid load: {high_score}")
            if high_score != 100:
                raise AssertionError(f"High score failed to load correctly. Got {high_score}")

            # Verify volumes were loaded correctly
            music_vol = page.evaluate("() => window.game.scene.scenes[0].registry.get('musicVolume')")
            ambient_vol = page.evaluate("() => window.game.scene.scenes[0].registry.get('ambientVolume')")
            sfx_vol = page.evaluate("() => window.game.scene.scenes[0].registry.get('sfxVolume')")

            print(f"Volumes after valid load -> Music: {music_vol}, Ambient: {ambient_vol}, SFX: {sfx_vol}")

            if music_vol != 0.8:
                raise AssertionError(f"Music volume not loaded correctly: {music_vol}")
            if ambient_vol != 0.2:
                raise AssertionError(f"Ambient volume not loaded correctly: {ambient_vol}")
            if sfx_vol != 0.7:
                raise AssertionError(f"SFX volume not loaded correctly: {sfx_vol}")

            print("SUCCESS: Valid game state was correctly loaded.")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_game_state_validation_test(is_mobile=False)
    run_game_state_validation_test(is_mobile=True)
