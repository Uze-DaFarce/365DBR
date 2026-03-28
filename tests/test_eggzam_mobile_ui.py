import sys
import os
from playwright.sync_api import sync_playwright

def verify_mobile_eggzam():
    print("Starting Playwright verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile viewport emulation
        context = browser.new_context(
            viewport={'width': 414, 'height': 896}, # iPhone XR dimensions
            is_mobile=True,
            record_video_dir="tests/verification/videos"
        )

        page = context.new_page()

        try:
            # Load local file path using absolute path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            repo_root = os.path.dirname(current_dir)

            # The game serves from the root
            import threading
            import http.server
            import socketserver

            PORT = 8080
            Handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", PORT), Handler)
            thread = threading.Thread(target=httpd.serve_forever)
            thread.daemon = True
            thread.start()

            print(f"Server started on port {PORT}")

            # Navigate to the mobile version
            page.goto(f"http://127.0.0.1:{PORT}/apps/HeIsRisen/m/index.html")

            print("Waiting for game to load...")
            # Wait for phaser canvas to be ready
            page.wait_for_selector("canvas")
            page.wait_for_timeout(3000)

            # We need to bypass the menu and jump straight to the EggZamRoom scene
            # We can do this by injecting some JS to force the scene start
            print("Forcing EggZamRoom scene...")
            page.evaluate("""
                () => {
                    const game = window.game; // Assuming game is exposed globally
                    if (game && game.scene) {
                        // Populate registry with dummy data so the scene doesn't crash
                        game.registry.set('foundEggs', [{
                            eggId: '1',
                            categorized: false,
                            symbolData: { category: 'Christian', name: 'Test Symbol', explanation: 'Test explanation', scripture: 'John 1:1' }
                        }]);

                        game.scene.start('EggZamRoom');
                    }
                }
            """)

            page.wait_for_timeout(3000)

            # Take screenshot of the mobile layout
            screenshot_path = "tests/verification/screenshots/eggzam_mobile_ui.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

            # Wait for video
            page.wait_for_timeout(1000)

        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            context.close()
            browser.close()
            httpd.shutdown()

if __name__ == "__main__":
    verify_mobile_eggzam()
