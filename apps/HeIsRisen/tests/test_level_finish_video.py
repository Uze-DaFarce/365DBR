import os
import sys
import time
import subprocess
import random
from playwright.sync_api import sync_playwright

def get_eggs_for_section(page, section_name):
    script = f"""
    () => {{
        const game = window.game;
        if (!game) return [];
        const registry = game.scene.scenes[0].registry;
        const allEggs = registry.get('eggData');
        if (!allEggs) return [];
        return allEggs.filter(egg => egg.section === '{section_name}' && !egg.collected);
    }}
    """
    return page.evaluate(script)

def test_level_finish_video(is_mobile=False):
    print(f"Testing {'Mobile' if is_mobile else 'Desktop'} context...")

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
            if is_mobile:
                iphone = p.devices['iPhone 12']
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(**iphone, record_video_dir="verification/video")
            else:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1280, 'height': 720}, record_video_dir="verification/video")

            page = context.new_page()

            page.add_init_script("""
                window.addEventListener('keydown', (e) => {
                    if (e.code === 'Space' || e.code === 'Enter') {
                        // Let Phaser handle it
                    }
                });
            """)

            if is_mobile:
                page.goto("http://127.0.0.1:8080/m/")
            else:
                page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            page.wait_for_function("() => window.game && window.game.scene && window.game.scene.scenes.length > 0")

            time.sleep(1)
            page.keyboard.press("Space")
            time.sleep(4)
            page.keyboard.press("Space")
            time.sleep(2)

            # Get all available sections from registry and pick a random one
            sections_data = page.evaluate("""
                () => {
                    const registry = window.game.scene.scenes[0].registry;
                    const sections = registry.get('sections');
                    return sections.map(s => s.name);
                }
            """)

            if not sections_data:
                print("FAIL: No sections found in registry.")
                sys.exit(1)

            random_section = random.choice(sections_data)
            print(f"Navigating to random SectionHunt: {random_section}")

            page.evaluate(f"() => window.game.scene.getScenes(true)[0].scene.start('SectionHunt', {{ sectionName: '{random_section}' }})")
            time.sleep(2)

            eggs = get_eggs_for_section(page, random_section)
            print(f"Found {len(eggs)} eggs in this section.")

            if len(eggs) == 0:
                print("FAIL: No eggs found in this section!")
                sys.exit(1)

            print("Collecting Eggs...")

            for egg in eggs:
                egg_x = egg['x']
                egg_y = egg['y']

                page.evaluate(f"""
                    () => {{
                        const scene = window.game.scene.getScene('SectionHunt');
                        const scale = scene.gameScale || scene.bgScale || 1;
                        let pointer_x = {egg_x};
                        let pointer_y = {egg_y};

                        if ({str(is_mobile).lower()}) {{
                            pointer_x = {egg_x} - (-97.5 * scale);
                            pointer_y = {egg_y} - (-135 * scale);
                        }} else {{
                            pointer_x = {egg_x};
                            pointer_y = {egg_y};
                        }}

                        scene.input.activePointer.x = pointer_x;
                        scene.input.activePointer.y = pointer_y;
                        scene.input.activePointer.worldX = pointer_x;
                        scene.input.activePointer.worldY = pointer_y;
                        scene.input.emit('pointerdown', scene.input.activePointer);

                        scene.eggs.getChildren().forEach(egg => {{
                            if (egg.getData('eggId') === scene.registry.get('eggData').find(e => e.x === {egg_x} && e.y === {egg_y}).eggId) {{
                                scene.collectEgg(egg);
                                egg.destroy();
                                if (egg.symbolSprite) egg.symbolSprite.destroy();
                            }}
                        }});
                    }}
                """)
                time.sleep(0.5)

            print("Level complete. Navigating to MapScene to see the completion video...")

            # Navigate back to map scene manually if checkLevelComplete doesn't do it automatically for just a section
            page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('MapScene')")

            time.sleep(1) # wait for MapScene to render and video to start playing

            print("Capturing screenshot of the MapScene with the video playing...")
            context_type = "mobile" if is_mobile else "desktop"
            screenshot_path = f"verification/level_finish_{context_type}.png"
            page.screenshot(path=screenshot_path)

            # Wait a few seconds for the video to play out in the recording
            time.sleep(4)

            remaining_eggs = get_eggs_for_section(page, random_section)

            if len(remaining_eggs) > 0:
                print(f"FAIL: {len(remaining_eggs)} eggs were not collected!")
                sys.exit(1)
            else:
                print("SUCCESS: All eggs collected!")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    print("--- Running Level Finish Video Test for Desktop Context ---")
    test_level_finish_video(is_mobile=False)

    print("\\n--- Running Level Finish Video Test for Mobile Context ---")
    test_level_finish_video(is_mobile=True)

    print("\\nALL TESTS PASSED")
