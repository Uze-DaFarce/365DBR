from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Intercept console logs
        page.on("console", lambda msg: print(f"BROWSER: {msg.text}"))

        page.goto("http://localhost:3000/bible.html")
        page.wait_for_timeout(2000)

        # 1. Select Testament (Old Testament)
        page.get_by_role("button", name="Old Testament").first.click()
        page.wait_for_timeout(500)

        # 3. Select Book (Genesis)
        page.get_by_role("button", name="GEN Genesis").click()
        page.wait_for_timeout(500)

        # 4. Select Chapter (1)
        # Chunks are 70 long: 1-70
        #page.get_by_text("1-50").click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="1", exact=True).click()
        page.wait_for_timeout(500)

        # 5. Click Verse 2
        page.get_by_role("button", name="2", exact=True).click()
        page.wait_for_timeout(2000)

        browser.close()

if __name__ == "__main__":
    run()
