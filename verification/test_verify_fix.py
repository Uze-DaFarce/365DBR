from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        # We MUST record video to verification/video
        context = browser.new_context(record_video_dir="/app/verification/video")
        page = context.new_page()

        try:
            print("Navigating to game...")
            page.goto("http://127.0.0.1:8000/apps/HeIsRisen/")
            page.wait_for_timeout(2000)

            print("Clicking anywhere to start...")
            # Click the center of the screen
            page.mouse.click(640, 360)
            page.wait_for_timeout(2000)

            print("Taking screenshot of the main menu...")
            page.screenshot(path="/app/verification/verification.png")
            page.wait_for_timeout(1000)

            print("Clicking PLAY NOW...")
            # Approximate center of PLAY NOW button
            page.mouse.click(640, 500)

            print("Waiting for MapScene transition...")
            page.wait_for_timeout(4000)

            print("Taking screenshot of the map scene...")
            page.screenshot(path="/app/verification/verification_map.png")
            page.wait_for_timeout(1000)

        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    import os
    os.makedirs("/app/verification/video", exist_ok=True)
    verify_feature()
    print("Verification complete.")
