import argparse
import os
import sys
import time
import requests
from playwright.sync_api import sync_playwright

# Ensure bible_common can be imported from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from bible_common import validate_safe_relative_path
except ImportError:
    print("Error: Could not import 'validate_safe_relative_path' from 'bible_common.py'.")
    sys.exit(1)

# --- Constants ---
DATA_DIR = "data"
PRODUCTION_DATA_URL = "https://mt-sin.ai/365DBR/data"

def setup_data_interception(page, source):
    """
    Intercepts network requests to the /data/ directory and serves them
    from the specified source (local or production).
    """
    def handle_route(route):
        request = route.request
        url = request.url

        if "/data/" in url:
            try:
                rel_path = url.split("/data/")[1]
                if not validate_safe_relative_path(rel_path):
                    route.abort('accessdenied')
                    return

                if source == "local":
                    local_path = os.path.join(DATA_DIR, rel_path.replace("/", os.sep))
                    if os.path.exists(local_path):
                        with open(local_path, "rb") as f:
                            content = f.read()
                        route.fulfill(status=200, body=content, content_type="application/json")
                    else:
                        route.fulfill(status=404, body=b"File not found in local data")
                else: # production
                    prod_url = f"{PRODUCTION_DATA_URL}/{rel_path}"
                    try:
                        resp = requests.get(prod_url, timeout=10)
                        resp.raise_for_status()
                        route.fulfill(status=resp.status_code, body=resp.content, content_type=resp.headers.get("Content-Type"))
                    except requests.exceptions.RequestException as e:
                        print(f"[Production] Error fetching {prod_url}: {e}")
                        route.abort()
            except Exception as e:
                print(f"[Interceptor Error] {e}")
                route.abort()
            return

        route.continue_()

    page.route("**/data/**/*.json", handle_route)

def run_focus_test(source: str):
    print(f"Running Index Focus verification with data source: '{source.upper()}'")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set up data interception
        setup_data_interception(page, source)

        try:
            print("Navigating to index.html...")
            page.goto("http://localhost:8000/index.html", wait_until="networkidle")

            # Wait for data to load
            print("Waiting for verse content to load...")
            page.wait_for_selector('.verse-block', timeout=15000)
            page.screenshot(path="verification/index_before.png")
            print("Initial content loaded.")

            # Click the NT pill to jump to the New Testament section
            print("Clicking NT jump link...")
            nt_button = page.locator('button[aria-label="Jump to New Testament"]')
            nt_button.click()
            time.sleep(1) # Allow for scroll animation
            page.screenshot(path="verification/index_after_pill.png")
            print("Jumped to NT section.")

            # Click the Next Day button
            print("Clicking Next Day button...")
            next_day_btn = page.locator('button[aria-label="Next Day (Shortcut: Right Arrow)"]')
            next_day_btn.click()
            page.wait_for_selector('.verse-block', timeout=15000) # Wait for new day's content
            page.screenshot(path="verification/index_after_next_day.png")
            print("Loaded next day's content.")

            # Change a translation to verify dropdown interaction
            print("Changing translation via dropdown...")
            compare_btn = page.locator('button[title="Select Translation for Middle Slot"]')
            compare_btn.click()
            time.sleep(0.5)
            web_btn = page.locator('button[aria-label="Select translation web"]')
            web_btn.click()
            time.sleep(0.5)
            page.screenshot(path="verification/index_after_dropdown.png")
            print("Translation changed.")

            print("\nSuccessfully executed focus verification script.")

        except Exception as e:
            page.screenshot(path="verification/focus_test_error.png")
            print(f"\nERROR: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UI interaction tests on the index page.")
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="Specify the data source: 'production' (default) or 'local'."
    )
    args = parser.parse_args()

    try:
        run_focus_test(source=args.source)
    except Exception as e:
        sys.exit(1)
