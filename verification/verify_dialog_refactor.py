from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("http://localhost:3000/bible.html")
        page.wait_for_timeout(2000)

        # 1. Click "Browse Bible"
        page.get_by_text("Browse Bible").click()
        page.wait_for_timeout(1000)

        # 2. Select Testament (Old Testament)
        page.get_by_role("button", name="Old Testament").first.click()
        page.wait_for_timeout(1000)

        # 3. Select Book (GEN)
        page.get_by_role("button", name="GEN Genesis").click()
        page.wait_for_timeout(1000)

        # Verify Refactor: Check if "GENESIS" is in the header, and screenshot full spread chapter view
        page.screenshot(path="verification/dialog_refactor_chapter.png")
        print("Took dialog_refactor_chapter.png")

        # Select a book with many chapters/verses like Psalms to see chunking
        page.get_by_text("Back").first.click() # Go back to Book view
        page.wait_for_timeout(500)

        page.get_by_role("button", name="PSA Psalms").click()
        page.wait_for_timeout(1000)
        page.screenshot(path="verification/dialog_refactor_psalms.png")
        print("Took dialog_refactor_psalms.png")

        browser.close()

if __name__ == "__main__":
    run()
