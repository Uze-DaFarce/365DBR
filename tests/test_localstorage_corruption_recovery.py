from playwright.sync_api import sync_playwright, expect
import os
import subprocess
import time

def test_localstorage_corruption(page, url_path, screenshot_name):
    print(f"Testing {url_path} with corrupted localStorage...")

    # 1. Load the page initially to set up origin for localStorage
    page.goto(url_path)
    page.wait_for_load_state("networkidle")

    # 2. Inject corrupted data into localStorage
    # Arrays, objects, and strings with spaces to test the strict parsing
    page.evaluate("""
        localStorage.setItem('highScore', '[9999]');
        localStorage.setItem('heIsRisenGameState', JSON.stringify({
            eggData: [],
            sections: [],
            foundEggs: [],
            stampedSections: [],
            correctCategorizations: "  ",
            currentScore: {}
        }));
        localStorage.setItem('musicVolume', '0.5abc');
    """)

    # 3. Reload the page so the app boots with the corrupted data
    page.reload()

    # 4. Wait for the MainMenu scene to become active
    # We bypass the start screen by clicking it if needed, or wait for the scene
    try:
        # Many phaser games require an initial click to start audio/context
        page.mouse.click(10, 10)
    except Exception:
        pass

    # Wait for the main menu play button or the scene to be active.
    # We can check the Phaser registry to see if it recovered gracefully to 0.
    page.wait_for_function("window.game && window.game.scene.isActive('MainMenu')", timeout=15000)

    # 5. Verify the registry values recovered to safe defaults instead of NaN or objects
    recovered_score = page.evaluate("window.game.registry.get('currentScore')")
    recovered_highscore = page.evaluate("window.game.registry.get('highScore')")

    print(f"Recovered Score: {recovered_score}")
    print(f"Recovered HighScore: {recovered_highscore}")

    assert recovered_score == 0, f"Expected currentScore 0, got {recovered_score}"
    assert recovered_highscore == 0, f"Expected highScore 0, got {recovered_highscore}"

    # 6. Take a screenshot proving the game booted successfully despite the corruption
    screenshot_path = os.path.abspath(screenshot_name)
    page.screenshot(path=screenshot_path)
    print(f"Saved visual verification to: {screenshot_path}")

def run_tests():
    server_process = None
    try:
        # Start local server at the repo root
        print("Starting local HTTP server...")
        server_process = subprocess.Popen(["python3", "-m", "http.server", "8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2) # Give it time to start

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Desktop
            desktop_context = browser.new_context(viewport={"width": 1280, "height": 720})
            desktop_page = desktop_context.new_page()
            desktop_page.on('console', lambda msg: print(f'DESKTOP BROWSER: {msg.text}'))
            test_localstorage_corruption(desktop_page, "http://127.0.0.1:8080/apps/HeIsRisen/", "desktop_recovery.png")
            desktop_context.close()

            # Mobile
            mobile_context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            mobile_page = mobile_context.new_page()
            mobile_page.on('console', lambda msg: print(f'MOBILE BROWSER: {msg.text}'))
            test_localstorage_corruption(mobile_page, "http://127.0.0.1:8080/apps/HeIsRisen/m/", "mobile_recovery.png")
            mobile_context.close()

            browser.close()

    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
            # Failsafe kill
            os.system("kill $(lsof -t -i :8080) 2>/dev/null || true")
            print("Server stopped.")

if __name__ == "__main__":
    run_tests()
