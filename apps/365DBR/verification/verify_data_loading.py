import argparse
import os
import sys
import requests
from playwright.sync_api import sync_playwright, expect

# Ensure bible_common can be imported from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from bible_common import validate_safe_relative_path
except ImportError:
    print("Error: Could not import 'validate_safe_relative_path' from 'bible_common.py'.")
    print("Ensure the script is run from a location where 'bible_common.py' is in the python path.")
    sys.exit(1)

# --- Constants ---
# Assumes the script is run from the root of the 365DBR app directory
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
                # Extract the path relative to the /data/ directory
                # e.g., "http://.../data/0101/manifest.json" -> "0101/manifest.json"
                rel_path = url.split("/data/")[1]

                if not validate_safe_relative_path(rel_path):
                    print(f"  [Security] Aborting unsafe path: {rel_path}")
                    route.abort('accessdenied')
                    return

                # --- Local Data Source ---
                if source == "local":
                    local_path = os.path.join(DATA_DIR, rel_path.replace("/", os.sep))
                    if os.path.exists(local_path) and os.path.isfile(local_path):
                        print(f"  [Local] Serving {rel_path}")
                        with open(local_path, "rb") as f:
                            content = f.read()
                        route.fulfill(status=200, body=content, content_type="application/json")
                        return
                    else:
                        # If a local file is missing, we DO NOT fall back to production
                        # to ensure tests against local data are strict.
                        print(f"  [Local] Error: File not found: {local_path}")
                        route.fulfill(status=404, body=b"File not found in local data source")
                        return

                # --- Production Data Source (Default) ---
                prod_url = f"{PRODUCTION_DATA_URL}/{rel_path}"
                try:
                    print(f"  [Production] Fetching {rel_path}")
                    resp = requests.get(prod_url, timeout=10)
                    resp.raise_for_status() # Raise an exception for bad status codes
                    route.fulfill(status=resp.status_code, body=resp.content, content_type=resp.headers.get("Content-Type"))
                    return
                except requests.exceptions.RequestException as e:
                    print(f"  [Production] Error fetching {prod_url}: {e}")
                    route.abort()
                    return

            except Exception as e:
                print(f"  [Interceptor Error] {e}")
                route.abort()
                return

        # For any other request, continue normally
        route.continue_()

    # Apply the interception rule for all .json files under the /data/ path
    page.route("**/data/**/*.json", handle_route)


def run(source: str):
    """
    Launches Playwright, sets up data interception, and runs verification tests.
    """
    print(f"Running verification with data source: '{source.upper()}'")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # Set up the data interception before navigating
        setup_data_interception(page, source)

        try:
            # 1. Verify index.html (Daily Bread)
            print("\nVerifying index.html (Daily Reading)...")
            # Use 0202 as a reliable reference date with content
            page.goto("https://mt-sin.ai/365DBR/index.html?startDate=0202", timeout=60000)

            # Wait for verse content to appear
            page.wait_for_selector(".verse-block", timeout=10000)

            verse_blocks = page.locator(".verse-block")
            count = verse_blocks.count()
            print(f"Found {count} verse blocks in index.html.")
            if count == 0:
                raise Exception("No verses found in index.html")

            first_text = verse_blocks.first.text_content()
            if not first_text or len(first_text.strip()) < 10:
                raise Exception(f"Verse text seems empty or too short: {first_text}")

            page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "index_baseline.png"))
            print("index.html verification PASSED.")

            # 2. Verify bible.html (Bible Browser)
            print("\nVerifying bible.html (Bible Browser)...")
            # The reading for 0202 includes Exodus 9
            page.goto("https://mt-sin.ai/365DBR/bible.html?book=EXO&chapter=9", timeout=60000)

            # Wait for verse content to appear
            page.wait_for_selector(".verse-block", timeout=10000)

            verse_blocks = page.locator(".verse-block")
            count = verse_blocks.count()
            print(f"Found {count} verse blocks in bible.html.")
            if count == 0:
                raise Exception("No verses found in bible.html")

            first_text = verse_blocks.first.text_content()
            if not first_text or len(first_text.strip()) < 10:
                raise Exception(f"Verse text seems empty or too short: {first_text}")

            page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible_baseline.png"))
            print("bible.html verification PASSED.")

            print("\nVerification successful!")

        except Exception as e:
            print(f"\nERROR: {e}")
            page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.png"))
            # Re-raise the exception to ensure the script exits with a non-zero code
            raise e
        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run verification tests for the 365DBR app, loading data from a specified source.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="""Specify the data source for the tests:
  'production' (default): Fetches data from the live production URL.
  'local': Uses data from the local 'data/' directory."""
    )
    args = parser.parse_args()
    
    run(source=args.source)
