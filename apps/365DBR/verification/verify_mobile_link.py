import argparse
import os
import sys
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

def test_mobile_browse_link(source: str):
    print(f"Running Mobile Link verification with data source: '{source.upper()}'")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a standard iPhone viewport
        context = browser.new_context(**p.devices['iPhone 12 Pro'])
        page = context.new_page()

        # Set up data interception
        setup_data_interception(page, source)

        try:
            print("Navigating to index.html...")
            page.goto("http://localhost:8000/index.html", wait_until="networkidle")

            # Wait for the main verse content to load to ensure the app is in a stable state
            page.wait_for_selector(".verse-block", timeout=15000)

            # Find the link to the Bible Browser
            browse_link = page.locator('a[title="Switch to Bible Browser"]')

            # On mobile, the link icon should be visible
            if browse_link.is_visible():
                print("PASS: Browse link icon is visible on mobile.")
            else:
                raise AssertionError("FAIL: Browse link icon is NOT visible on mobile.")

            # The text label "Browse" should be hidden on mobile
            text_span = browse_link.locator("span")
            if text_span.is_hidden():
                print("PASS: 'Browse' text label is hidden on mobile.")
            else:
                raise AssertionError("FAIL: 'Browse' text label is visible on mobile.")

            # Take a screenshot of the header for visual verification
            header = page.locator("header")
            header.screenshot(path="verification/mobile_header.png")
            print("Screenshot saved to verification/mobile_header.png")
            
            print("\nMobile Link verification successful!")

        except Exception as e:
            page.screenshot(path="verification/mobile_link_error.png")
            print(f"\nERROR: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify the Bible Browse link visibility on mobile.")
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="Specify the data source: 'production' (default) or 'local'."
    )
    args = parser.parse_args()

    try:
        test_mobile_browse_link(source=args.source)
    except Exception as e:
        sys.exit(1)
