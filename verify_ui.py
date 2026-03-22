from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-gpu', '--disable-webgl', '--use-gl=swiftshader']
        )
        context = browser.new_context(record_video_dir="/home/jules/verification/video")
        page = context.new_page()

        try:
            # Test mobile app reset functionality
            print("Navigating to mobile app...")
            page.goto("http://127.0.0.1:8081/HeIsRisen/m/index.html")
            page.wait_for_timeout(3000)

            # Click "Tap to Start"
            page.mouse.click(200, 200)
            page.wait_for_timeout(2000)

            print("Testing Start New Game modal...")
            # Locate START NEW GAME button text
            start_btn = page.locator("text='START NEW GAME'")
            if start_btn.count() > 0:
                # We need to click the container, getting exact center of the text
                box = start_btn.bounding_box()
                if box:
                    print(f"Clicking START NEW GAME at {box['x'] + box['width']/2}, {box['y'] + box['height']/2}")
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    page.wait_for_timeout(1000)

            # Take screenshot of the custom confirm modal
            print("Taking screenshot of the modal...")
            page.screenshot(path="/home/jules/verification/mobile_confirm_modal.png")
            page.wait_for_timeout(500)

            # Locate the YES button inside the modal and click it
            yes_btn = page.locator("text='YES'")
            if yes_btn.count() > 0:
                box = yes_btn.bounding_box()
                if box:
                    print("Clicking YES to reset game")
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    page.wait_for_timeout(2000)

            # Navigate to desktop app
            print("Navigating to desktop app...")
            page.goto("http://127.0.0.1:8081/HeIsRisen/index.html")
            page.wait_for_timeout(3000)

            # Click Tap to Start
            page.mouse.click(640, 360)
            page.wait_for_timeout(2000)

            start_btn = page.locator("text='START NEW GAME'")
            if start_btn.count() > 0:
                box = start_btn.bounding_box()
                if box:
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    page.wait_for_timeout(1000)

            print("Taking screenshot of the desktop modal...")
            page.screenshot(path="/home/jules/verification/desktop_confirm_modal.png")
            page.wait_for_timeout(1000)

        finally:
            context.close()
            browser.close()
            print("Done")

if __name__ == "__main__":
    verify_feature()