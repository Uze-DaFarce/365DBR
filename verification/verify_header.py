from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Test Mobile Viewport where space is critical
        page = browser.new_page(viewport={"width": 375, "height": 667})

        try:
            page.goto("http://localhost:8000/index.html")

            # Wait for content to load
            page.wait_for_selector("header")

            # Verify Calendar Button is GONE
            calendar_btn = page.locator('button[aria-label="Open Calendar"]')
            if calendar_btn.count() > 0:
                print("Error: Calendar button found!")
                expect(calendar_btn).not_to_be_attached()
            else:
                print("Verified: Calendar button is removed.")

            # Verify Date Input is GONE
            date_input = page.locator('input[type="date"]')
            if date_input.count() > 0:
                 print("Error: Date input found!")
                 expect(date_input).not_to_be_attached()
            else:
                 print("Verified: Date input is removed.")

            # Take screenshot of header to confirm layout
            header = page.locator("header")
            header.screenshot(path="verification/header_mobile.png")
            print("Screenshot saved to verification/header_mobile.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
