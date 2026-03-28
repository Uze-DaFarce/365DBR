from playwright.sync_api import sync_playwright
import time
import os

def run_cuj(page):
    print("Navigating to local server...")
    page.goto("http://localhost:8080/apps/HeIsRisen/index.html")
    page.wait_for_timeout(2000)

    print("Starting game...")
    # Wait for the game to load
    page.wait_for_function("() => window.game && window.game.scene.getScenes(true).length > 0")

    # Click to start the intro
    page.mouse.click(640, 360)
    page.wait_for_timeout(1000)

    # Click PLAY NOW
    page.mouse.click(640, 580)
    page.wait_for_timeout(2000)

    # We are in MapScene. Go to EggZamRoom.
    print("Navigating to EggZamRoom via console...")
    page.evaluate("() => window.game.scene.getScenes(true)[0].scene.start('EggZamRoom')")
    page.wait_for_timeout(2000)

    # Setup some test data in EggZamRoom so we can categorize
    print("Setting up test egg data...")
    page.evaluate("""() => {
        const scene = window.game.scene.getScene('EggZamRoom');
        scene.registry.set('foundEggs', [
            {
                eggId: 1,
                symbolData: {
                    name: 'Test Christian Symbol',
                    category: 'Christian',
                    explanation: 'This is a test explanation for a Christian symbol.',
                    scripture: 'John 3:16',
                    filename: 'assets/map/new-map.png' // Use an existing asset so it loads
                },
                categorized: false
            }
        ]);
        scene.displayRandomEggInfo(0, 0, 1);
    }""")
    page.wait_for_timeout(1000)

    # Click the Egg-cellent button
    # stinkyBtn = 640 - 120 = 520, eggCellentBtn = 640 + 120 = 760
    # centerBottomY = 720 - 100 = 620
    print("Clicking Egg-cellent button to categorize the egg...")
    page.mouse.click(760, 620)

    print("Waiting for animation to complete...")
    page.wait_for_timeout(4000)

    print("Taking screenshot of the explanation popup...")
    os.makedirs("/home/jules/verification/screenshots", exist_ok=True)
    page.screenshot(path="/home/jules/verification/screenshots/verification_eggzam_desktop.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
            print("Verification complete.")
