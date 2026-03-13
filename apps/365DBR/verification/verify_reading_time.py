import os
from playwright.sync_api import sync_playwright
import re

def verify_reading_time():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mt-sin.ai/365DBR/index.html?startDate=0222")

        # Wait for data to load
        page.wait_for_selector(".verse-block", timeout=20000)

        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Verify reading time text
        footer = page.locator("footer")
        text_content = footer.text_content()
        print(f"Footer content: {text_content}")

        match = re.search(r"\d+ min read", text_content)
        if match:
            print(f"PASS: Found reading time: '{match.group(0)}'")
        else:
            print("FAIL: Reading time not found in footer.")
            exit(1)

        # Take screenshot
        footer.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "reading_time.png"))
        print("Screenshot saved to verification/reading_time.png")

        browser.close()

if __name__ == "__main__":
    verify_reading_time()
