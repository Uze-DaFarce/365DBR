from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a clean context with no local storage or URL params
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:3000/bible.html")
        page.wait_for_timeout(2000)

        # Expect the dialogue to be visible automatically
        # Let's take a screenshot to verify it opened
        page.screenshot(path="verification/dialog_auto_open.png")
        print("Took dialog_auto_open.png")

        # Verify text is on screen to prove it's the dialogue
        assert page.get_by_text("Testament", exact=False).first.is_visible(), "Testament dialogue not visible!"

        browser.close()

if __name__ == "__main__":
    run()
