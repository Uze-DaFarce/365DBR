from playwright.sync_api import sync_playwright
import os

def test_mobile_browse_link():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)

        # Create a mobile context (iPhone 12 Pro)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        # Load index.html
        page.goto("https://mt-sin.ai/365DBR/index.html")

        # Wait for content to load
        page.wait_for_selector("header")

        # Find the Browse link
        # There are two links, one for larger screens, one for mobile. Find the one visible on mobile.
        browse_link = page.locator('a[title="Switch to Bible Browser"]').filter(has_text="BROWSE").first

        # If we can't find it easily this way, let's just pick the visible one
        visible_link = None
        for i in range(page.locator('a[title="Switch to Bible Browser"]').count()):
            link = page.locator('a[title="Switch to Bible Browser"]').nth(i)
            if link.is_visible():
                visible_link = link
                break

        if visible_link:
            print("SUCCESS: Browse link is visible on mobile.")
            text_span = visible_link.locator("span")
            if text_span.count() > 0 and text_span.is_hidden():
                 print("SUCCESS: 'Browse' text is hidden on mobile.")
            else:
                 print("FAILURE: 'Browse' text is visible on mobile (or no span found).")
        else:
            print("FAILURE: Browse link is NOT visible on mobile.")

        # Take screenshot of header
        header = page.locator("header")
        header.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile_header.png"))

        browser.close()

if __name__ == "__main__":
    test_mobile_browse_link()
