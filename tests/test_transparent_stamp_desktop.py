from playwright.sync_api import sync_playwright
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(
        headless=True,
        args=['--disable-gpu', '--disable-webgl', '--use-gl=swiftshader']
    )
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        record_video_dir="tests/video",
        record_video_size={'width': 1280, 'height': 720}
    )
    page = context.new_page()

    # Pre-inject local storage data so a section is marked as complete but NOT YET STAMPED
    script = """
    const state = {
        eggData: [
            {eggId: 1, section: 'genesis', x: 500, y: 500, symbol: {filename: 'assets/symbols/christian/lily.png'}, collected: true}
        ],
        sections: [{name: 'genesis', eggs: [1]}],
        foundEggs: [
            {eggId: 1, symbolData: {filename: 'assets/symbols/christian/lily.png'}, categorized: true}
        ],
        stampedSections: [], // Empty so it plays the animation
        correctCategorizations: 1,
        currentScore: 100
    };
    localStorage.setItem('heIsRisenGameState', JSON.stringify(state));
    """

    page.goto("http://127.0.0.1:8080/apps/HeIsRisen/index.html")
    page.evaluate(script)
    page.reload()

    print("Game loaded, waiting for Main Menu...")
    page.wait_for_timeout(2000)
    page.mouse.click(640, 360)

    print("Waiting for Play button...")
    page.wait_for_timeout(1000)
    page.mouse.click(640, 580)

    print("Map Scene loading...")
    page.wait_for_timeout(4000)

    os.makedirs("tests/verification", exist_ok=True)
    screenshot_path = "tests/verification/stamp_animation_desktop_fixed.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

    page.wait_for_timeout(2000)

    context.close()
    browser.close()
    return screenshot_path

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
