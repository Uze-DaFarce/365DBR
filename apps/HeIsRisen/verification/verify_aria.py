from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu', '--disable-webgl', '--use-gl=swiftshader'])
        context = browser.new_context()
        page = context.new_page()

        # Desktop
        page.goto("http://localhost:8000/apps/HeIsRisen/index.html")
        page.wait_for_timeout(2000)

        # Check if sr-announcer is present
        announcer = page.locator('#sr-announcer')
        announcer.wait_for(state='attached')
        print(f"Desktop announcer present: {announcer.count() == 1}")

        # Take a screenshot to prove the UI still renders correctly
        page.screenshot(path="/app/apps/HeIsRisen/verification/desktop_aria.png")

        # Mobile
        context_mobile = browser.new_context(viewport={'width': 844, 'height': 390})
        page_mobile = context_mobile.new_page()
        page_mobile.goto("http://localhost:8000/apps/HeIsRisen/m/index.html")
        page_mobile.wait_for_timeout(2000)

        # Check if sr-announcer is present
        announcer_mobile = page_mobile.locator('#sr-announcer')
        announcer_mobile.wait_for(state='attached')
        print(f"Mobile announcer present: {announcer_mobile.count() == 1}")

        # Take a screenshot
        page_mobile.screenshot(path="/app/apps/HeIsRisen/verification/mobile_aria.png")

        context_mobile.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    verify_feature()
