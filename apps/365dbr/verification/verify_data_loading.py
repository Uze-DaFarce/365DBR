from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Verify index.html (Daily Bread)
            print("Verifying index.html...")
            # Use 0202 as reference date (Feb 2nd) which has content
            page.goto("http://localhost:8000/index.html?startDate=0202")

            # Wait for content
            page.wait_for_selector(".verse-block", timeout=5000)

            verse_blocks = page.locator(".verse-block")
            count = verse_blocks.count()
            print(f"Found {count} verse blocks in index.html.")
            if count == 0:
                raise Exception("No verses found in index.html")

            first_text = verse_blocks.first.text_content()
            if not first_text or len(first_text.strip()) < 10:
                raise Exception(f"Verse text seems empty or too short: {first_text}")

            page.screenshot(path="verification/index_baseline.png")

            # 2. Verify bible.html (Browser)
            print("Verifying bible.html...")
            # 0202 covers EXO.9.1-EXO.10.29
            page.goto("http://localhost:8000/bible.html?book=EXO&chapter=9")

            # Wait for content
            page.wait_for_selector(".verse-block", timeout=5000)

            verse_blocks = page.locator(".verse-block")
            count = verse_blocks.count()
            print(f"Found {count} verse blocks in bible.html.")
            if count == 0:
                raise Exception("No verses found in bible.html")

            first_text = verse_blocks.first.text_content()
            if not first_text or len(first_text.strip()) < 10:
                raise Exception(f"Verse text seems empty or too short: {first_text}")

            page.screenshot(path="verification/bible_baseline.png")

            print("Verification successful!")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
