from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Get absolute path to index.html
        cwd = os.getcwd()
        file_path = f"file://{cwd}/index.html"
        print(f"Loading: {file_path}")

        page.goto(file_path)

        # 1. Verify Title
        title = page.title()
        print(f"Page Title: {title}")
        assert "Christian Business Services" in title

        # 2. Verify Ministry Section
        ministry_section = page.locator("#ministry")
        assert ministry_section.is_visible()

        # Screenshot Ministry Section
        ministry_section.scroll_into_view_if_needed()
        page.screenshot(path="verification/ministry_section.png")
        print("Screenshot of Ministry Section saved.")

        # 3. Verify Footer Social Links
        footer = page.locator("footer")
        footer.scroll_into_view_if_needed()

        # Check for "Follow Us" text
        assert page.get_by_text("Follow Us").is_visible()

        # Screenshot Footer
        page.screenshot(path="verification/footer_section.png")
        print("Screenshot of Footer saved.")

        browser.close()

if __name__ == "__main__":
    run()
