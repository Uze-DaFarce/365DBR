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
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for content to load
        page.wait_for_selector("header")

        # Find the Browse link
        # It has title="Switch to Bible Browser"
        browse_link = page.locator('a[title="Switch to Bible Browser"]')

        # Check if it is visible
        if browse_link.is_visible():
            print("SUCCESS: Browse link is visible on mobile.")
        else:
            print("FAILURE: Browse link is NOT visible on mobile.")

        # Check if the text "Browse" is hidden
        # The text is inside a span with class "hidden md:inline"
        text_span = browse_link.locator("span")

        # In Tailwind, 'hidden' class sets display: none
        # We can check computed style or visibility
        if text_span.is_hidden():
             print("SUCCESS: 'Browse' text is hidden on mobile.")
        else:
             print("FAILURE: 'Browse' text is visible on mobile.")

        # Take screenshot of header
        header = page.locator("header")
        header.screenshot(path="verification/mobile_header.png")

        browser.close()

if __name__ == "__main__":
    test_mobile_browse_link()
