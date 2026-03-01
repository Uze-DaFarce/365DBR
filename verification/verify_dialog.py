from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the page
        page.goto("http://localhost:3000/bible.html")
        page.wait_for_timeout(2000) # Wait for initial data load

        # 1. Click "Browse Bible"
        page.get_by_text("Browse Bible").click()
        page.wait_for_timeout(1000)
        page.screenshot(path="verification/dialog_step1.png")
        print("Took dialog_step1.png")

        # 2. Select Testament (Old Testament)
        # Using a more specific selector because there might be multiple "Old Testament" texts on mobile vs desktop.
        page.get_by_role("button", name="Old Testament").first.click()
        page.wait_for_timeout(1000)
        page.screenshot(path="verification/dialog_step2.png")
        print("Took dialog_step2.png")

        # 3. Select Book (GEN)
        page.get_by_role("button", name="GEN Genesis").click()
        page.wait_for_timeout(1000)
        page.screenshot(path="verification/dialog_step3.png")
        print("Took dialog_step3.png")

        # 4. Select Chapter (1)
        page.get_by_role("button", name="1", exact=True).click()
        page.wait_for_timeout(1000)
        page.screenshot(path="verification/dialog_step4.png")
        print("Took dialog_step4.png")

        # 5. Select Verse (1) - Should close dialog
        page.get_by_role("button", name="1", exact=True).click()
        page.wait_for_timeout(1000)
        page.screenshot(path="verification/dialog_step5.png")
        print("Took dialog_step5.png")

        browser.close()

if __name__ == "__main__":
    run()
