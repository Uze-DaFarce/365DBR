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

def verify_footer(source: str):
    print(f"Running Footer verification with data source: '{source.upper()}'")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set up data interception
        setup_data_interception(page, source)

        try:
            # Navigate to a day with known content
            page.goto("https://mt-sin.ai/365DBR/index.html?startDate=0222", timeout=60000)

            # Wait for text that indicates data has loaded. This text is in the footer itself.
            page.wait_for_selector("text=Literal Standard Version", timeout=15000)

            # Scroll to the bottom to ensure the footer is fully visible
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Take a screenshot of the footer for verification
            footer = page.locator("footer")
            footer.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "footer_verification.png"))
            print("Footer screenshot saved.")

            print("\nFooter verification successful!")

        except Exception as e:
            page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "footer_error.png"))
            print(f"\nERROR: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify the content and layout of the footer.")
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="Specify the data source: 'production' (default) or 'local'."
    )
    args = parser.parse_args()

    try:
        verify_footer(source=args.source)
    except Exception as e:
        sys.exit(1)
