from playwright.sync_api import sync_playwright
import time

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
        # JS runs on load, so it should be near 0%
        page.wait_for_timeout(100)
        initial_style = progress_bar.get_attribute("style") or ""
        print(f"Initial style: '{initial_style}'")

        # Scroll down
        print("Scrolling down...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(500) # Wait for throttle and CSS transition

        mid_style = progress_bar.get_attribute("style")
        print(f"Mid scroll style: '{mid_style}'")

        if not mid_style or "width" not in mid_style:
             print("FAIL: Width style not set on progress bar after scroll.")
             browser.close()
             exit(1)

        # Extract width value
        # Style format might be "width: 50.123%;"
        width_str = mid_style.split("width:")[1].split("%")[0].strip()
        width_val = float(width_str)
        print(f"Mid width value: {width_val}%")

        if not (10 < width_val < 90):
             print(f"FAIL: Expected width between 10% and 90%, got {width_val}%")
             browser.close()
             exit(1)

        # Scroll to bottom
        print("Scrolling to bottom...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)
        # Scroll again in case lazy loaded images expanded the height
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(500)

        end_style = progress_bar.get_attribute("style")
        print(f"End scroll style: '{end_style}'")
        width_str_end = end_style.split("width:")[1].split("%")[0].strip()
        width_val_end = float(width_str_end)
        print(f"End width value: {width_val_end}%")

        if width_val_end < 90:
             print(f"FAIL: Expected end width > 90%, got {width_val_end}%")
             browser.close()
             exit(1)

        print("SUCCESS: Scroll progress bar works as expected.")
        browser.close()

if __name__ == "__main__":
    verify_scroll_progress()
