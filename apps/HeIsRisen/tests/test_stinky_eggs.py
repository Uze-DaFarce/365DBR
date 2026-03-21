import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_stinky_egg_test(is_mobile=False):
    context_type = "mobile" if is_mobile else "desktop"
    print(f"\n=== Testing Stinky Eggs & Audio ({context_type.capitalize()}) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")
    verification_dir = os.path.join(script_dir, "..", "..", "..", "verification")
    os.makedirs(verification_dir, exist_ok=True)

    server_process = th.start_server(app_dir)
    time.sleep(2) # Give server time to boot

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

            if is_mobile:
                page.goto("http://127.0.0.1:8080/m/")
            else:
                page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            th.wait_for_phaser_init(page)

            # Start Game to get past the initial user interaction block for AudioContext
            page.locator('canvas').first.click(force=True)

            # Use evaluate to just skip to mapscene after preloader finishes
            time.sleep(5) # Just wait

            # Start MapScene directly
            page.evaluate("window.game.scene.scenes[0].scene.start('MapScene')")
            time.sleep(2)

            # Inject state to bypass menu and go straight to the EggZamRoom with a Pagan egg ready to be categorized
            page.evaluate("""
                () => {
                    const registry = window.game.registry;
                    registry.set('foundEggs', [{
                        eggId: 'egg1',
                        categorized: false,
                        symbolData: { category: 'Pagan' }
                    }]);
                    registry.set('currentScore', 0);
                    registry.set('highScore', 0);
                    registry.set('sfxVolume', 0.5);
                    registry.set('ambientVolume', 0.5);
                    registry.set('correctCategorizations', 0);

                    // Stop other scenes and start EggZamRoom
                    window.game.scene.scenes.forEach(s => {
                        if (s.scene.isActive()) s.scene.stop();
                    });
                    window.game.scene.start('EggZamRoom');
                }
            """)

            time.sleep(2) # Wait for scene to build



            # Trigger the Stinky Egg categorization via code
            page.evaluate("""
                () => {
                    const eggZamScene = window.game.scene.getScene('EggZamRoom');
                    if (eggZamScene && eggZamScene.rightBottleZone) {
                        eggZamScene.rightBottleZone.emit('pointerdown');
                    }
                }
            """)

            # Take a screenshot right as it starts
            time.sleep(0.5)
            screenshot_path = os.path.join(verification_dir, f"stinky_egg_gas_{context_type}.png")
            page.screenshot(path=screenshot_path)
            print(f"Captured green gas screenshot: {screenshot_path}")

            time.sleep(1.5)

            browser.close()
    finally:
        server_process.terminate()

def test_stinky_eggs_desktop():
    run_stinky_egg_test(is_mobile=False)

def test_stinky_eggs_mobile():
    run_stinky_egg_test(is_mobile=True)

if __name__ == "__main__":
    test_stinky_eggs_desktop()
    test_stinky_eggs_mobile()
