from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a clean context with no local storage or URL params
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:3000/bible.html")
        page.wait_for_timeout(2000)

        # 1. Dialog should open automatically due to my previous fix
        page.screenshot(path="verification/dialog_cover.png")
        print("Took dialog_cover.png")

        # 2. Select Testament (Old Testament)
        page.get_by_role("button", name="Old Testament").first.click()
        page.wait_for_timeout(1000)

        # 3. Select Book (Psalms)
        page.get_by_role("button", name="PSA Psalms").click()
        page.wait_for_timeout(1000)

        # Snapshot Chapters
        page.screenshot(path="verification/dialog_chapters.png")
        print("Took dialog_chapters.png")

        # 4. Select Chapter (119 - which has 176 verses)
        # Chunks are 70 long: 1-70, 71-140
        page.get_by_text("71-140").click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="119", exact=True).click()
        page.wait_for_timeout(1000)

        # Snapshot Verses
        page.screenshot(path="verification/dialog_verses.png")
        print("Took dialog_verses.png")

        # 5. Click Verse 176
        # Need to go to third chunk: 141-176
        page.get_by_text("141-176").click()
        page.wait_for_timeout(500)

        page.screenshot(path="verification/dialog_verses_176.png")
        print("Took dialog_verses_176.png")

        browser.close()

if __name__ == "__main__":
    run()
