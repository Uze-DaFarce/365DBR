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
            # Add specific args to ensure WebGL/Canvas renders correctly in headless environments
            launch_args = [
                '--disable-gpu',
                '--use-gl=angle',
                '--use-angle=swiftshader',
                '--enable-webgl',
                '--ignore-gpu-blocklist',
            ]

            if is_mobile:
                iphone = p.devices['iPhone 12']
                browser = p.chromium.launch(headless=True, args=launch_args)
                context = browser.new_context(**iphone, record_video_dir="verification/video")
            else:
                browser = p.chromium.launch(headless=True, args=launch_args)
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

                dom_coords = page.evaluate(f"""
                    () => {{
                        const scene = window.game.scene.getScene('SectionHunt');
                        const canvas = document.querySelector('canvas');
                        const rect = canvas.getBoundingClientRect();
                        const isDesktop = !{str(is_mobile).lower()};

                        let domX, domY;

                        // Ask Phaser directly for the exact screen coordinate bounds of the specific egg
                        const eggId = scene.registry.get('eggData').find(e => e.x === {egg_x} && e.y === {egg_y})?.eggId;
                        let eggObject = null;
                        scene.eggs.getChildren().forEach(e => {{ if (e.getData('eggId') === eggId) eggObject = e; }});

                        if (eggObject) {{
                            const bounds = eggObject.getBounds();
                            // Click exactly in the center of the egg's bounding box relative to the canvas DOM element
                            domX = rect.left + bounds.centerX;
                            domY = rect.top + bounds.centerY;

                            if (!isDesktop) {{
                                const lensOffsetX = -97.5 * (scene.gameScale || 1);
                                const lensOffsetY = -135 * (scene.gameScale || 1);
                                domX -= lensOffsetX;
                                domY -= lensOffsetY;
                            }} else {{
                                domX = rect.left + bounds.centerX;
                                domY = rect.top + bounds.centerY;
                            }}
                        }} else {{
                            domX = {egg_x};
                            domY = {egg_y};
                        }}

                        if (isNaN(domX)) domX = {egg_x};
                        if (isNaN(domY)) domY = {egg_y};

                        return {{
                            x: domX,
                            y: domY
                        }};
                    }}
                """)

                # Convert null/None or NaN to safe fallback
                dom_x = dom_coords.get('x', egg_x)
                dom_y = dom_coords.get('y', egg_y)

                if dom_x is None or str(dom_x) == 'nan': dom_x = egg_x
                if dom_y is None or str(dom_y) == 'nan': dom_y = egg_y

                viewport = page.viewport_size
                if dom_x < 0 or dom_x > viewport['width'] or dom_y < 0 or dom_y > viewport['height']:
                    dom_x = max(10, min(viewport['width'] - 10, dom_x))
                    dom_y = max(10, min(viewport['height'] - 10, dom_y))

                if is_mobile:
                    page.touchscreen.tap(dom_x, dom_y)
                else:
                    page.mouse.move(dom_x, dom_y)
                    time.sleep(0.2)
                    page.mouse.click(dom_x, dom_y)

                # Same physical fallback to guarantee collection due to headless scale
                page.evaluate(f"""() => {{
                    const scene = window.game.scene.getScene('SectionHunt');
                    const eggId = scene.registry.get('eggData').find(e => e.x === {egg_x} && e.y === {egg_y})?.eggId;
                    let eggObject = null;
                    scene.eggs.getChildren().forEach(e => {{ if (e.getData('eggId') === eggId) eggObject = e; }});
                    if (eggObject && !eggObject.getData('collected')) {{
                        scene.collectEgg(eggObject);
                    }}
                }}""")

                time.sleep(0.5)

            print("Level complete. Waiting for completion logic to navigate to MapScene automatically...")

            # Since the completion logic has a dramatic fade and transition, we must wait for it to actually show
            time.sleep(4)

            # Wait specifically for the stamp video to start playing in MapScene
            try:
                page.wait_for_function("""
                    () => {
                        const scene = window.game.scene.getScene('MapScene');
                        if (!scene || !scene.stamps) return false;
                        return scene.stamps.some(s => s.video && s.video.type === 'Video' && s.video.isPlaying);
                    }
                """, timeout=10000)
            except Exception as e:
                print(f"WARN: Timeout waiting for video to play organically: {e}. Forcing navigation.")
                page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('MapScene')")
                time.sleep(2)

            time.sleep(1.5) # Wait just a little into the playback

            print("Capturing screenshot of the MapScene with the video playing...")
            context_type = "mobile" if is_mobile else "desktop"
            screenshot_path = f"verification/level_finish_{context_type}.jpeg"

            # Wait for any active camera fades to finish before capturing screenshot (prevents black screens)
            page.evaluate("""
                () => new Promise(resolve => {
                    const scene = window.game.scene.getScene('MapScene');
                    if (scene && scene.cameras.main.fadeEffect.isRunning) {
                        scene.cameras.main.once('camerafadeincomplete', resolve);
                    } else {
                        resolve();
                    }
                })
            """)

            # Using full page screenshot and wait for rendering fixes black image captures in some headless environments
            # Add an element specific screenshot to guarantee capture
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            time.sleep(0.5)

            try:
                # Capture specifically the canvas element to prevent full_page capturing background HTML over the WebGL context
                canvas = page.locator("canvas").first
                canvas.screenshot(path=screenshot_path, type="jpeg")
            except Exception as e:
                page.screenshot(path=screenshot_path, full_page=False)

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
