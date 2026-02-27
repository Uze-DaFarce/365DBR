from playwright.sync_api import sync_playwright

def verify_navigation():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Go to Bible Browser
        # We need to serve from root to access data/
        page.goto("http://localhost:3000/bible.html")

        # Wait for data to load
        try:
            page.wait_for_selector("select[aria-label='Select Book']", timeout=10000)
        except Exception:
            print("Timeout waiting for Book selector. Check console logs.")
            # print(page.content())
            return

        # Select Genesis
        page.select_option("select[aria-label='Select Book']", "GEN")

        # Wait for Chapter selector and select Ch 1
        page.wait_for_selector("select[aria-label='Select Chapter']", timeout=5000)
        page.select_option("select[aria-label='Select Chapter']", "1")

        # Wait for content - GEN 1 might not be in the mock data, let's check what's available
        # The compile_site output says 0101 was processed, which has GEN 1.
        try:
            page.wait_for_selector(".verse-block", timeout=5000)
        except:
             print("Content not loading for GEN 1. Might be missing local data.")
             # Fallback: check if we can at least navigate UI

        # Screenshot initial state
        page.screenshot(path="verification/initial_gen_1.png")
        print("Captured initial state")

        # Click Next Chapter button
        # If no content, navigation might still work (it changes state)
        next_btn = page.locator("button[aria-label='Next Chapter (Right Arrow)']")
        if next_btn.is_visible():
            next_btn.click()
            page.wait_for_timeout(1000) # Wait for state update

            # Check if selector updated
            val = page.locator("select[aria-label='Select Chapter']").input_value()
            if val == "2":
                 print("Verified Next Chapter click (Selector updated to 2)")
            else:
                 print(f"Next Chapter click failed? Value: {val}")

            page.screenshot(path="verification/next_gen_2.png")

        # Test Previous Chapter
        prev_btn = page.locator("button[aria-label='Previous Chapter (Left Arrow)']")
        if prev_btn.is_visible():
            prev_btn.click()
            page.wait_for_timeout(1000)
            val = page.locator("select[aria-label='Select Chapter']").input_value()
            if val == "1":
                 print("Verified Prev Chapter click (Selector updated to 1)")
            else:
                 print(f"Prev Chapter click failed? Value: {val}")
            page.screenshot(path="verification/prev_gen_1.png")

        # Test Keyboard Shortcut (Right Arrow)
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(1000)
        val = page.locator("select[aria-label='Select Chapter']").input_value()
        if val == "2":
             print("Verified Keyboard ArrowRight (Selector updated to 2)")

        browser.close()

if __name__ == "__main__":
    verify_navigation()
