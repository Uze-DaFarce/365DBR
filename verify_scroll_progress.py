from playwright.sync_api import sync_playwright
import time
import re

def verify_scroll_progress():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        try:
            page.goto("http://localhost:8000/index.html")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            print("Make sure python3 -m http.server 8000 is running.")
            return

        page.wait_for_load_state("networkidle")

        # Check if progress bar exists
        progress_bar = page.locator("#scroll-progress")
        assert progress_bar.count() == 1, "Progress bar element not found"
        print("Progress bar element found.")

        # Initial check
        page.wait_for_timeout(100)
        initial_style = progress_bar.get_attribute("style") or ""
        print(f"Initial style: '{initial_style}'")

        # Scroll down
        print("Scrolling down...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(500) # Wait for throttle

        mid_style = progress_bar.get_attribute("style")
        print(f"Mid scroll style: '{mid_style}'")

        if not mid_style or "transform" not in mid_style:
             print("FAIL: Transform style not set on progress bar after scroll.")
             browser.close()
             exit(1)

        # Extract scaleX value
        # Style format might be "transform: scaleX(0.50123);"
        match = re.search(r"scaleX\(([\d\.]+)\)", mid_style)
        if not match:
             print("FAIL: scaleX value not found in style.")
             browser.close()
             exit(1)

        scale_val = float(match.group(1))
        print(f"Mid scale value: {scale_val}")

        if not (0.1 < scale_val < 0.9):
             print(f"FAIL: Expected scale between 0.1 and 0.9, got {scale_val}")
             browser.close()
             exit(1)

        # Scroll to bottom
        print("Scrolling to bottom...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)

        end_style = progress_bar.get_attribute("style")
        print(f"End scroll style: '{end_style}'")

        match_end = re.search(r"scaleX\(([\d\.]+)\)", end_style)
        if not match_end:
             print("FAIL: End scaleX value not found.")
             browser.close()
             exit(1)

        scale_val_end = float(match_end.group(1))
        print(f"End scale value: {scale_val_end}")

        if scale_val_end < 0.9:
             print(f"FAIL: Expected end scale > 0.9, got {scale_val_end}")
             browser.close()
             exit(1)

        print("SUCCESS: Scroll progress bar works as expected (optimized).")
        browser.close()

if __name__ == "__main__":
    verify_scroll_progress()
