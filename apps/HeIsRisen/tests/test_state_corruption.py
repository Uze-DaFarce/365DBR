import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_state_corruption_test(is_mobile=False):
    context_type = "mobile" if is_mobile else "desktop"
    print(f"\n=== Testing State Corruption Resilience ({context_type.capitalize()}) ===")

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

            # Pre-populate localStorage with corrupted data to simulate tampering
            url = "http://127.0.0.1:8080/m/" if is_mobile else "http://127.0.0.1:8080/"

            # Go to a blank page on the same origin first to set local storage
            page.goto("http://127.0.0.1:8080/index.html")

            page.evaluate("""
                () => {
                    localStorage.setItem('highScore', '-Infinity'); // Edge case negative infinity
                    localStorage.setItem('musicVolume', 'NaN'); // Not a number
                    localStorage.setItem('musicVolume_backup', '0.8'); // Valid backup
                    localStorage.setItem('ambientVolume', '{}'); // Stringified object
                    localStorage.setItem('ambientVolume_backup', 'not_a_number'); // Invalid backup
                    localStorage.setItem('sfxVolume', ' '); // Empty/whitespace string
                    // No sfxVolume_backup set

                    // Tamper with the main game state
                    const corruptedState = {
                        eggData: "not an array",
                        sections: { wrong: "type" },
                        foundEggs: "should be array",
                        stampedSections: 12345,
                        correctCategorizations: "NaN",
                        currentScore: "HACKED"
                    };
                    localStorage.setItem('heIsRisenGameState', JSON.stringify(corruptedState));
                }
            """)

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

            # Verify high score was handled gracefully (should be 0)
            high_score = page.evaluate("() => window.game.scene.scenes[0].registry.get('highScore')")
            print(f"High Score after corrupted load: {high_score}")
            if high_score != 0:
                raise AssertionError(f"High score failed to fallback to 0. Got {high_score}")

            # Verify volumes were handled gracefully (should be bounded between 0 and 1, or default 0.5)
            music_vol = page.evaluate("() => window.game.scene.scenes[0].registry.get('musicVolume')")
            ambient_vol = page.evaluate("() => window.game.scene.scenes[0].registry.get('ambientVolume')")
            sfx_vol = page.evaluate("() => window.game.scene.scenes[0].registry.get('sfxVolume')")

            print(f"Volumes after corrupted load -> Music: {music_vol}, Ambient: {ambient_vol}, SFX: {sfx_vol}")

            if music_vol > 1.0 or music_vol < 0.0:
                raise AssertionError(f"Music volume not bounded safely: {music_vol}")
            if ambient_vol > 1.0 or ambient_vol < 0.0:
                raise AssertionError(f"Ambient volume not bounded safely: {ambient_vol}")
            if sfx_vol > 1.0 or sfx_vol < 0.0:
                raise AssertionError(f"SFX volume not bounded safely: {sfx_vol}")

            # Expect music to fallback to valid backup (0.8)
            # Expect ambient to fallback to 0.5 because backup is invalid
            # Expect sfx to fallback to 0.5 because backup is missing
            if music_vol != 0.8 or ambient_vol != 0.5 or sfx_vol != 0.5:
                 raise AssertionError(f"Volumes should fallback properly, but got Music:{music_vol}, Ambient:{ambient_vol}, SFX:{sfx_vol}")

            current_score = page.evaluate("() => window.game.scene.scenes[0].registry.get('currentScore')")
            print(f"Current Score after corrupted load: {current_score}")
            if current_score != 0 or type(current_score) != int:
                raise AssertionError(f"Current score failed to fallback to 0 or is invalid. Got {current_score} ({type(current_score)})")

            correct_cat = page.evaluate("() => window.game.scene.scenes[0].registry.get('correctCategorizations')")
            print(f"Correct Categorizations after corrupted load: {correct_cat}")
            if correct_cat != 0 or type(correct_cat) != int:
                raise AssertionError(f"Correct Categorizations failed to fallback to 0 or is invalid. Got {correct_cat} ({type(correct_cat)})")

            found_eggs = page.evaluate("() => window.game.scene.scenes[0].registry.get('foundEggs')")
            if not isinstance(found_eggs, list):
                raise AssertionError(f"foundEggs is not a list. Got {type(found_eggs)}")

            stamped_sections = page.evaluate("() => window.game.scene.scenes[0].registry.get('stampedSections')")
            if not isinstance(stamped_sections, list):
                raise AssertionError(f"stampedSections is not a list. Got {type(stamped_sections)}")

            egg_data = page.evaluate("() => window.game.scene.scenes[0].registry.get('eggData')")
            if not isinstance(egg_data, list):
                raise AssertionError(f"eggData is not a list. Got {type(egg_data)}")

            sections = page.evaluate("() => window.game.scene.scenes[0].registry.get('sections')")
            if not isinstance(sections, list):
                raise AssertionError(f"sections is not a list. Got {type(sections)}")

            print("SUCCESS: State corruption was safely rejected and game defaulted to stable values (or valid backups).")

            # Capture visual proof
            os.makedirs("verification", exist_ok=True)
            screenshot_path = f"verification/state_corruption_{context_type}.png"
            page.screenshot(path=screenshot_path)
            print(f"Captured screenshot proof at: {screenshot_path}")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_state_corruption_test(is_mobile=False)
    run_state_corruption_test(is_mobile=True)
