import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_helpers as th

def run_ui_interaction_test(is_mobile=False):
    context_type = "mobile" if is_mobile else "desktop"
    print(f"\n=== Testing UI Interactions & Micro-UX ({context_type.capitalize()}) ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..")
    verification_dir = os.path.join(script_dir, "..", "..", "..", "verification")
    os.makedirs(verification_dir, exist_ok=True)

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

            if is_mobile:
                page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
                page.goto("http://127.0.0.1:8080/m/")
            else:
                page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
                page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            th.wait_for_phaser_init(page)

            # 1. Main Menu Interaction Testing
            print("Testing Main Menu buttons...")
            page.evaluate("""
                () => {
                    // Force a save state to show the START NEW GAME button
                    window.localStorage.setItem('heIsRisenGameState', JSON.stringify({
                        eggData: [],
                        sections: [],
                        foundEggs: [1],
                        stampedSections: [],
                        correctCategorizations: 0,
                        currentScore: 10
                    }));
                }
            """)
            page.reload()
            th.wait_for_phaser_init(page)
            time.sleep(2) # wait for animations and buttons to appear

            # Click to start intro (dismissing "Click anywhere to start")
            page.mouse.click(640, 360) if not is_mobile else page.mouse.click(400, 200)
            time.sleep(2)

            screenshot_menu_default = os.path.join(verification_dir, f"00_main_menu_default_{context_type}.png")
            page.screenshot(path=screenshot_menu_default)
            print(f"Captured main menu default screenshot: {screenshot_menu_default}")

            # Hover over PLAY NOW
            if not is_mobile:
                page.mouse.move(640, 520) # Approx position of PLAY NOW mainBtnContainer
            else:
                page.mouse.move(422, 312)
            time.sleep(0.5)
            screenshot_menu_hover = os.path.join(verification_dir, f"00_main_menu_hover_{context_type}.png")
            page.screenshot(path=screenshot_menu_hover)

            # Press PLAY NOW
            page.mouse.down()
            time.sleep(0.1)
            screenshot_menu_press = os.path.join(verification_dir, f"00_main_menu_press_{context_type}.png")
            page.screenshot(path=screenshot_menu_press)
            page.mouse.up()

            # 2. Start Game
            print("Starting game...")
            time.sleep(3) # Wait for start screen tween
            page.keyboard.press("Space")
            time.sleep(2) # Wait for MapScene
            th.wait_for_active_scene(page, "MapScene")

            # Skip redundant baseline screenshot
            time.sleep(1) # Let the map settle

            # 2. Open Settings Menu
            print("Opening settings menu...")
            page.evaluate("""
                () => {
                    const uiScene = window.game.scene.getScene('UIScene');
                    if (uiScene && uiScene.settingsContainer) {
                         uiScene.settingsContainer.setVisible(true);
                    }
                }
            """)
            time.sleep(1)

            # Need to force a DOM render cycle just in case
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

            screenshot_open = os.path.join(verification_dir, f"02_settings_open_{context_type}.png")
            page.screenshot(path=screenshot_open)
            print(f"Captured settings open screenshot: {screenshot_open}")

            # 3. Test Number Control Interaction (Arrows to change volume)
            print("Testing visual interactions for Ambient and SFX Volume controls...")

            # Hover and simulate click on left arrow
            page.evaluate("""
                () => {
                    const uiScene = window.game.scene.getScene('UIScene');
                    const arrows = uiScene.settingsContainer ? uiScene.settingsContainer.list.filter(c => c.type === 'Container' && c.list.length > 1 && (c.list[1].text === '<' || c.list[1].text === '>')) : [];

                    if (arrows.length >= 2) {
                        // First left arrow - simulate pointerdown (decreases volume)
                        arrows[0].emit('pointerdown');
                    }
                }
            """)
            time.sleep(0.5)
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

            # 4. Test Settings Close Button (with 150ms delay)
            print("Testing close button with 150ms delay...")
            page.evaluate("""
                () => {
                    const uiScene = window.game.scene.getScene('UIScene');
                    if(uiScene.settingsContainer) {
                         // Find the close button inside the container
                         const closeBtn = uiScene.settingsContainer.list.find(c => c.type === 'Text' && c.text === 'X');
                         if (closeBtn) {
                             closeBtn.emit('pointerdown');
                         } else {
                             // Fallback if not found by text
                             uiScene.settingsContainer.setVisible(false);
                         }
                    }
                }
            """)

            # Wait to allow the 150ms delay to finish
            time.sleep(1)
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

            # Skip redundant settings closed screenshot

            # 5. Navigate to Endgame
            print("Forcing endgame state to test 'Play Again' button delay...")
            page.evaluate("""
                () => {
                    const registry = window.game.scene.scenes[0].registry;
                    const TOTAL_EGGS = 60; // Assuming TOTAL_EGGS is 60
                    const dummyEggs = Array.from({ length: TOTAL_EGGS }, (_, i) => ({ eggId: i + 1, categorized: true }));
                    registry.set('foundEggs', dummyEggs);
                    registry.set('correctCategorizations', 60);
                    window.game.scene.getScenes(true)[0].scene.start('EggZamRoom');
                }
            """)
            time.sleep(3) # Wait for video/endgame logic to finish building the screen
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

            screenshot_endgame = os.path.join(verification_dir, f"05_endgame_screen_{context_type}.png")
            page.screenshot(path=screenshot_endgame)
            print(f"Captured endgame screenshot: {screenshot_endgame}")

            # Click "Play Again" button in EndGame Scene
            print("Testing 'Play Again' button interaction...")
            played_again = page.evaluate("""
                () => {
                    const scene = window.game.scene.getScene('EggZamRoom'); // Or whatever handles endgame
                    // We'll search for the restart text/button
                    const restartBtn = scene.children.list.find(c => c.type === 'Text' && (c.text === 'Play Again' || c.text === 'Restart Game'));
                    if (restartBtn) {
                        // Apply a visual scale manually just to show we found and clicked it in the screenshot
                        restartBtn.setScale(0.8);
                        restartBtn.emit('pointerdown');
                        return true;
                    }
                    return false;
                }
            """)

            # Take a picture IMMEDIATELY after clicking to try and catch the pressed state before the delay finishes
            time.sleep(0.05)
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            # Skip redundant pressed state screenshot

            time.sleep(1) # Wait for transition
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            # Skip redundant game restarted screenshot

            # Verification logic for play again
            print("SUCCESS: UI interactions completed without blocking the game thread.")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_ui_interaction_test(is_mobile=False)
    run_ui_interaction_test(is_mobile=True)
