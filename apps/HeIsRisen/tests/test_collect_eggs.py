import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def get_eggs_for_section(page, section_name):
    # Retrieve egg data from the Phaser registry
    # In Phaser 3, registry is usually accessible via game.scene.scenes[0].registry
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

def test_collect_eggs_in_level(is_mobile=False):
    print(f"Testing {'Mobile' if is_mobile else 'Desktop'} context...")

    # Ensure http-server runs from the HeIsRisen directory even if executed from monorepo root
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
            if is_mobile:
                iphone = p.devices['iPhone 12']
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(**iphone)
            else:
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

            if is_mobile:
                page.goto("http://127.0.0.1:8080/m/")
            else:
                page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            # Wait for Phaser to initialize
            page.wait_for_function("() => window.game && window.game.scene && window.game.scene.scenes.length > 0")

            # 1. Start the game (Main Menu)
            print("1. Starting Main Menu")
            time.sleep(1) # wait for intro video setup

            # Press Space to simulate global tap and pass through "Tap to start"
            page.keyboard.press("Space")

            # Wait for Play Now button (Wait 3s in the intro logic + tween)
            time.sleep(4)

            # Press Space again to trigger "Play Now"
            page.keyboard.press("Space")

            # Wait for MapScene to load
            print("2. Waiting for Map Scene")
            time.sleep(2)

            # 2. Go to a specific section (e.g. "grand-prismatic")
            # In MapScene, we can just start the SectionHunt scene directly via console to ensure reliability
            # or click the map. Direct scene start is more robust for testing the actual egg logic.
            print("3. Navigating to SectionHunt: grand-prismatic")
            page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('SectionHunt', { sectionName: 'grand-prismatic' })")
            time.sleep(2) # wait for SectionHunt to load

            # 3. Retrieve Eggs
            print("4. Retrieving Eggs in grand-prismatic")
            eggs = get_eggs_for_section(page, "grand-prismatic")
            print(f"Found {len(eggs)} eggs in this section.")

            if len(eggs) == 0:
                print("FAIL: No eggs found in this section!")
                sys.exit(1)

            # 4. Programmatically "tap" each egg using the lens logic
            print("5. Collecting Eggs...")

            for egg in eggs:
                egg_x = egg['x']
                egg_y = egg['y']

                print(f"Attempting to collect egg at ({egg_x}, {egg_y})")

                # We need to simulate a pointerdown event.
                # In m/main.js, the egg collection checks the distance from the *lens visual center*,
                # which is offset from the pointer.
                # const lensOffsetX = -97.5 * scale;
                # const lensOffsetY = -135 * scale;
                # lensX = pointer.x + lensOffsetX
                # lensY = pointer.y + lensOffsetY
                # So to make lensX = egg_x, pointer.x must be egg_x - lensOffsetX

                # Fetch scale from scene
                scale = page.evaluate("() => { const scene = window.game.scene.getScene('SectionHunt'); return scene.gameScale || scene.bgScale || 1; }")

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
                                domX = rect.left + bounds.centerX;
                                domY = rect.top + bounds.centerY;

                                if (!isDesktop) {{
                                    const lensOffsetX = -97.5 * (scene.gameScale || 1);
                                    const lensOffsetY = -135 * (scene.gameScale || 1);
                                    domX -= lensOffsetX;
                                    domY -= lensOffsetY;
                                    }} else {{
                                        // The ONLY reason `bounds.centerX` isn't registering correctly via Playwright's physical mouse
                                        // is because the `magnifyingGlass.setPosition(pointer.x - 15, pointer.y - 30)` logic
                                        // in Desktop intercepts it or modifies the global pointer visually.
                                        // WAIT. We discovered earlier that forcing `input.activePointer.x = pointer_x` and emitting worked.
                                        // This means `pointer_x` must be EXACTLY `egg_x`.
                                        // So what is the exact physical DOM pixel that maps to `egg.x`?
                                        // In RESIZE mode where canvas spans 1280x720, `pointer_x` literally maps 1:1 with `clientX` inside the canvas.
                                        // Let's try direct translation without offsets or bounds logic.
                                        domX = rect.left + {egg_x};
                                        domY = rect.top + {egg_y};
                                    }}
                            }} else {{
                                domX = 0;
                                domY = 0;
                            }}

                        return {{
                            x: domX,
                            y: domY
                        }};
                    }}
                """)

                dom_x = dom_coords['x']
                dom_y = dom_coords['y']

                viewport = page.viewport_size
                if dom_x < 0 or dom_x > viewport['width'] or dom_y < 0 or dom_y > viewport['height']:
                    # Cap boundaries instead of failing for minor edge bleeds
                    dom_x = max(10, min(viewport['width'] - 10, dom_x))
                    dom_y = max(10, min(viewport['height'] - 10, dom_y))
                    print(f"WARN: Capped Physical DOM pointer interaction to ({dom_x}, {dom_y})")

                # Move the mouse so the magnifying glass follows and visually frames it, then click.
                # In Playwright, `tap` implicitly dispatches pointerdown, pointerup.
                if is_mobile:
                    page.touchscreen.tap(dom_x, dom_y)
                else:
                    page.mouse.move(dom_x, dom_y)
                    time.sleep(0.2) # Briefly pause like a kid aiming the magnifying glass
                    page.mouse.click(dom_x, dom_y)

                time.sleep(0.5) # Wait for collection tween/logic

            # 5. Verify the "Great Job Detective" message appears
            print("6. Verifying level complete...")

            # Wait a moment for the checkLevelComplete logic
            time.sleep(1)

            # Verify no more eggs are left uncollected in this section
            remaining_eggs = get_eggs_for_section(page, "grand-prismatic")

            if len(remaining_eggs) > 0:
                print(f"FAIL: {len(remaining_eggs)} eggs were not collected!")
                sys.exit(1)
            else:
                print("SUCCESS: All eggs collected!")

            # Optional: Check if the text "Great Job Detective" exists in the scene
            text_exists = page.evaluate("""
                () => {
                    const scene = window.game.scene.getScene('SectionHunt');
                    return scene.children.list.some(child => child.type === 'Text' && child.text && child.text.includes('Great Job Detective'));
                }
            """)

            if text_exists:
                print("SUCCESS: 'Great Job Detective' message found!")
            else:
                print("FAIL: Completion message not found!")
                sys.exit(1)

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    print("--- Running Test for Desktop Context ---")
    test_collect_eggs_in_level(is_mobile=False)

    print("\\n--- Running Test for Mobile Context ---")
    test_collect_eggs_in_level(is_mobile=True)

    print("\\nALL TESTS PASSED")
