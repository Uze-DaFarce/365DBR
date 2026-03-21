from playwright.sync_api import sync_playwright

def test_mobile_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile viewport equivalent
        context = browser.new_context(
            viewport={'width': 800, 'height': 360},
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
            has_touch=True,
            is_mobile=True
        )
        page = context.new_page()
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.goto("http://localhost:8000/m/")

        # Click the canvas directly to start
        page.wait_for_timeout(2000)
        page.locator("canvas").click(position={"x": 10, "y": 10}, force=True)

        # Click the middle to press PLAY NOW
        page.wait_for_timeout(2000)
        page.locator("canvas").click(position={"x": 400, "y": 180}, force=True)

        # Wait for map scene
        page.wait_for_timeout(8000)

        page.screenshot(path="/home/jules/verification/mobile_map_scene_test.png")
        browser.close()

if __name__ == "__main__":
    test_mobile_ui()
