import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def verify_feature():
    print("Starting verification script...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "..", "apps", "HeIsRisen")

    server_process = subprocess.Popen(
        ["npx", "http-server", "-p", "8080", "-c-1"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2) # wait for server to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Record video
            context = browser.new_context(viewport={'width': 1280, 'height': 720}, record_video_dir="verification/video")
            page = context.new_page()

            # Global keydown listener
            page.add_init_script("""
                window.addEventListener('keydown', (e) => {
                    if (e.code === 'Space' || e.code === 'Enter') {
                    }
                });
            """)

            print("Navigating to desktop app...")
            page.goto("http://127.0.0.1:8080/")
            page.wait_for_load_state('networkidle')

            page.wait_for_function("() => window.game && window.game.scene && window.game.scene.scenes.length > 0")

            time.sleep(1)
            page.keyboard.press("Space")
            time.sleep(4)
            page.keyboard.press("Space")
            time.sleep(2)

            print("Navigating to SectionHunt...")
            page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('SectionHunt', { sectionName: 'grand-prismatic' })")
            time.sleep(2)

            eggs = page.evaluate("""
            () => {
                const game = window.game;
                if (!game) return [];
                const registry = game.scene.scenes[0].registry;
                const allEggs = registry.get('eggData');
                if (!allEggs) return [];
                return allEggs.filter(egg => egg.section === 'grand-prismatic' && !egg.collected);
            }
            """)

            print(f"Collecting {len(eggs)} eggs...")
            for egg in eggs:
                egg_x = egg['x']
                egg_y = egg['y']

                page.evaluate(f"""
                    () => {{
                        const scene = window.game.scene.getScene('SectionHunt');
                        const pointer_x = {egg_x};
                        const pointer_y = {egg_y};

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

            # Wait for level complete video to play
            print("Level complete. Waiting for webm to play and capturing screenshot...")
            time.sleep(3)

            # The level complete video should be visible in MapScene now
            page.screenshot(path="verification/verification.png")
            time.sleep(2)

            context.close()
            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    verify_feature()
