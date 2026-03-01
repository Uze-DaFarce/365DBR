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

        # Snapshot Cover
        page.screenshot(path="verification/dialog_cover.png")
        print("Took dialog_cover.png")

        # 2. Select Testament (Old Testament)
        page.get_by_role("button", name="Old Testament").first.click()
        page.wait_for_timeout(1000)

        page.screenshot(path="verification/dialog_book.png")
        print("Took dialog_book.png")

        browser.close()

if __name__ == "__main__":
    run()
