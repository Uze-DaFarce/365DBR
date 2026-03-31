import os
import sys

# Add pytest pipx env to PYTHONPATH so we can import playwright
sys.path.append('/home/jules/.local/share/pipx/venvs/pytest/lib/python3.12/site-packages')

from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # We don't record video to commit per AGENTS.md, but we take a screenshot to verify
        page = browser.new_page()

        # Start a local HTTP server in the background to serve the files
        import subprocess
        import time
        server_process = subprocess.Popen(["python3", "-m", "http.server", "8080"])
        time.sleep(2) # wait for server to start

        try:
            # Navigate to the local server
            page.on('console', lambda msg: print(f'BROWSER CONSOLE: {msg.text}'))
            page.goto("http://localhost:8080/apps/HeIsRisen/index.html")
            page.wait_for_load_state("networkidle")

            # Start game and skip to EggZamRoom directly
            print("Navigating to EggZamRoom...")
            page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('EggZamRoom')")
            page.wait_for_timeout(2000)

            # Setup fake data in EggZamRoom so we can test categorization
            print("Injecting fake data...")
            page.evaluate("""() => {
                const scene = window.game.scene.getScene('EggZamRoom');
                scene.registry.set('foundEggs', [
                    { eggId: 1, symbolData: { category: 'Christian', name: 'Test1', explanation: 'exp1', scripture: 'John 1:1' }, categorized: false },
                    { eggId: 2, symbolData: { category: 'Pagan', name: 'Test2', explanation: 'exp2', scripture: 'John 1:2' }, categorized: false }
                ]);
                scene.registry.set('currentScore', 100);
                scene.registry.set('correctCategorizations', 0);
                scene.scene.restart();
            }""")

            page.wait_for_timeout(2000)

            # Categorize first egg correctly
            print("Categorizing first egg...")
            page.evaluate("""() => {
                const scene = window.game.scene.getScene('EggZamRoom');
                const isChristian = scene.currentEgg.symbolData.category === 'Christian';
                if (isChristian) {
                    scene.actionButtons[1].emit('pointerdown'); // EggCellent
                } else {
                    scene.actionButtons[0].emit('pointerdown'); // Stinky
                }
            }""")

            page.wait_for_timeout(4000) # Wait for animation/video

            # Close popup safely
            print("Closing popup...")
            page.evaluate("""() => {
                const scene = window.game.scene.getScene('EggZamRoom');
                if (scene.explanationText && scene.explanationText.list) {
                    scene.explanationText.list.forEach(el => {
                        if (el.type === 'Container') { // The close button
                            el.emit('pointerdown');
                        }
                    });
                }
            }""")

            page.wait_for_timeout(2000)

            # Categorize second egg incorrectly
            print("Categorizing second egg incorrectly...")
            page.evaluate("""() => {
                const scene = window.game.scene.getScene('EggZamRoom');
                if (!scene.currentEgg) return;
                const isChristian = scene.currentEgg.symbolData.category === 'Christian';
                if (isChristian) {
                    scene.actionButtons[0].emit('pointerdown'); // Stinky (wrong)
                } else {
                    scene.actionButtons[1].emit('pointerdown'); // EggCellent (wrong)
                }
            }""")

            page.wait_for_timeout(4000)

            # Close popup again safely
            print("Closing second popup...")
            page.evaluate("""() => {
                const scene = window.game.scene.getScene('EggZamRoom');
                if (scene.explanationText && scene.explanationText.list) {
                    scene.explanationText.list.forEach(el => {
                        if (el.type === 'Container') { // The close button
                            el.emit('pointerdown');
                        }
                    });
                }
            }""")

            page.wait_for_timeout(2000)

            # Both should now be categorized. Score should be 100 + 5 (1 correct) = 105.
            # Total categorized = 2. It should show the Final EggZam screen now!
            page.screenshot(path="apps/HeIsRisen/tests/verification_eggzam_desktop.png")
            print("Screenshot saved to apps/HeIsRisen/tests/verification_eggzam_desktop.png")

        finally:
            server_process.terminate()
            browser.close()

if __name__ == "__main__":
    run_test()
