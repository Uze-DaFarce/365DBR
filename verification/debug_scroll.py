from playwright.sync_api import sync_playwright

def test_scroll():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        page.goto("http://localhost:3000/bible.html")
        page.wait_for_selector("text=Select a book to begin")

        # Test scroll by clicking OT -> GEN -> 1 -> 5
        # 1. Click OT (the button has the text "Old")
        page.click("text=\"Old\"")

        # 2. Click GEN
        page.click("button:has-text('GEN')")

        # 3. Click Chapter 1
        page.click("button:has-text('1')")

        # 4. Click Verse 5
        page.click("button:has-text('5')")

        # 5. Wait for scroll
        page.wait_for_timeout(2000)

        # Log scroll position using JS
        scroll_y = page.evaluate("window.scrollY")
        print(f"Scroll Y Position: {scroll_y}")

        # The scroll position should be significantly greater than 0 if we scrolled down to verse 5.
        if scroll_y > 100:
            print("SUCCESS! Scrolled successfully!")
        else:
            print("FAILED! Did not scroll!")

        page.screenshot(path="verification/bible_scroll.png")
        browser.close()

if __name__ == "__main__":
    test_scroll()
