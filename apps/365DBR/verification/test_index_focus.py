import time
from playwright.sync_api import sync_playwright

def test_focus(page):
    # Load index.html locally with http server against production data fallback
    page.goto("http://localhost:3000/index.html")

    # Wait for loading to finish (indicated by the presence of a verse group)
    page.wait_for_selector('.verse-block', timeout=10000)

    # Take a screenshot before interaction
    page.screenshot(path="verification/index_before.png")

    # Click the NT pill (which has aria-label="Jump to New Testament" and role="button")
    nt_button = page.locator('button[aria-label="Jump to New Testament"]')
    nt_button.click()

    # Wait a bit for smooth scroll and any transitions
    time.sleep(1)

    # Take a screenshot after interaction
    page.screenshot(path="verification/index_after_pill.png")

    # Click the Next Day button
    next_day_btn = page.locator('button[aria-label="Next Day (Shortcut: Right Arrow)"]')
    next_day_btn.click()

    # Wait a bit
    time.sleep(1)

    # Take another screenshot
    page.screenshot(path="verification/index_after_next_day.png")

    # Open Compare Translation dropdown
    compare_btn = page.locator('button[title="Select Translation for Middle Slot"]')
    compare_btn.click()
    time.sleep(0.5)

    # Click WEB
    web_btn = page.locator('button[aria-label="Select translation web"]')
    web_btn.click()
    time.sleep(0.5)

    page.screenshot(path="verification/index_after_dropdown.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-web-security"])
        page = browser.new_page()
        try:
            test_focus(page)
            print("Successfully executed focus verification script.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
