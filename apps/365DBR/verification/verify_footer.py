import os
from playwright.sync_api import sync_playwright

def verify_footer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mt-sin.ai/365DBR/index.html?startDate=0222")

        # Wait for data to load
        page.wait_for_selector("text=Literal Standard Version", timeout=10000)

        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Take screenshot of footer
        footer = page.locator("footer")
        footer.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "footer_verification.png"))

        browser.close()

if __name__ == "__main__":
    verify_footer()
