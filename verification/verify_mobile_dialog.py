import subprocess
import time
from playwright.sync_api import sync_playwright

def test_mobile_dialog():
    server_process = subprocess.Popen(["python3", "-m", "http.server", "3000"])
    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 375, 'height': 667},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            )
            page = context.new_page()

            page.goto("http://localhost:3000/bible.html")
            page.wait_for_selector("text=Select a book to begin")

            # Take screenshot of the testament selection
            page.wait_for_timeout(1000)
            page.screenshot(path="verification/mobile_dialog_testament_new.png")

            # Click OT
            page.click("text=\"Old\"")
            page.wait_for_timeout(1000)
            page.screenshot(path="verification/mobile_dialog_books_new.png")

            # Try to click Genesis to see chapters
            page.click("button:has-text('GEN')")
            page.wait_for_timeout(1000)
            page.screenshot(path="verification/mobile_dialog_chapters_new.png")

            # Scroll down to verify scroll works
            page.evaluate("document.querySelector('.overflow-y-auto').scrollTop = 1000")
            page.wait_for_timeout(500)
            page.screenshot(path="verification/mobile_dialog_chapters_scrolled.png")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    test_mobile_dialog()
