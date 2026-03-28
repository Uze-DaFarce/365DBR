import sys
import os
import subprocess
import time
from playwright.sync_api import sync_playwright

def get_base_url():
    """Retrieve the dynamically assigned ngrok URL or use localhost."""
    url = os.environ.get("VERCEL_URL", "")
    if url:
        if not url.startswith("http"):
            url = f"https://{url}"
        return url
    return "http://127.0.0.1:8080"

# Kill existing servers
subprocess.run("kill $(lsof -t -i :8080) 2>/dev/null || true", shell=True)

# Start simple web server
server_process = subprocess.Popen(
    [sys.executable, "-m", "http.server", "8080"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

try:
    with sync_playwright() as p:
        print("Playwright starting...")
        browser = p.chromium.launch(headless=True)
        # Force landscape orientation
        context = browser.new_context(viewport={"width": 667, "height": 375}, is_mobile=True, user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
        page = context.new_page()

        base_url = get_base_url()
        url = f"{base_url}/apps/HeIsRisen/m/index.html"
        print(f"Navigating to: {url}")

        page.goto(url)
        print("Page loaded, waiting for game initialization...")

        # Wait for the game canvas and registry to initialize
        page.wait_for_selector("canvas", state="visible", timeout=15000)
        print("Canvas found. Injecting test data...")

        # Inject game state: Give 1 uncategorized egg so we can jump straight to EggZamRoom
        page.evaluate("""
            () => {
                if (window.game && window.game.registry) {
                    window.game.registry.set('musicVolume', 0);
                    window.game.registry.set('sfxVolume', 0);
                    window.game.registry.set('ambientMusicVolume', 0);
                    window.game.registry.set('foundEggs', [{
                        eggId: '10',
                        x: 100, y: 100,
                        found: true,
                        categorized: false,
                        symbolData: {
                            id: 10,
                            filename: 'Symbol 10010',
                            category: 'Pagan',
                            explanation: 'Test Explanation.'
                        }
                    }]);
                    window.game.registry.set('currentScore', 0);

                    // Stop current scene and start EggZamRoom
                    const activeScenes = window.game.scene.scenes.filter(s => s.sys.settings.active);
                    activeScenes.forEach(s => window.game.scene.stop(s.sys.config.key));
                    window.game.scene.start('EggZamRoom');
                }
            }
        """)

        print("Navigated to EggZamRoom. Waiting 500ms to capture starting UI state...")
        # We wait 500ms because there is now a 500ms tween for the egg alpha
        time.sleep(1)

        # Take screenshot of the room without any interactions
        screenshot_path = "apps/HeIsRisen/tests/mobile_eggzam_room_landscape_start.png"
        page.screenshot(path=screenshot_path)
        print(f"Start-state landscape screenshot saved to {screenshot_path}")

        browser.close()

finally:
    # Cleanup server
    print("Stopping server...")
    server_process.terminate()
    server_process.wait()
