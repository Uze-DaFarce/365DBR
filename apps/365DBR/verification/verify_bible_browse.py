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
    print("Ensure the script is run from a location where 'bible_common.py' is in the python path.")
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
                    if os.path.exists(local_path) and os.path.isfile(local_path):
                        with open(local_path, "rb") as f:
                            content = f.read()
                        route.fulfill(status=200, body=content, content_type="application/json")
                        return
                    else:
                        route.fulfill(status=404, body=b"File not found in local data source")
                        return
                else: # production
                    prod_url = f"{PRODUCTION_DATA_URL}/{rel_path}"
                    try:
                        resp = requests.get(prod_url, timeout=10)
                        resp.raise_for_status()
                        route.fulfill(status=resp.status_code, body=resp.content, content_type=resp.headers.get("Content-Type"))
                        return
                    except requests.exceptions.RequestException as e:
                        print(f"[Production] Error fetching {prod_url}: {e}")
                        route.abort()
                        return
            except Exception as e:
                print(f"[Interceptor Error] {e}")
                route.abort()
                return

        route.continue_()

    page.route("**/data/**/*.json", handle_route)

def verify_bible_browse(source: str):
    print(f"Running Bible Browse verification with data source: '{source.upper()}'")
    with sync_playwright() as p:
        # iPhone 12 emulation for mobile testing
        iphone = p.devices['iPhone 12']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**iphone)
        page = context.new_page()

        # Set up data interception before any navigation
        setup_data_interception(page, source)

        print("Navigating to app...")
        # Standardize on port 8000
        page.goto("https://mt-sin.ai/365DBR/bible.html", timeout=60000)

        # Wait for page to indicate it's ready for browsing
        page.wait_for_selector("text=Browse Bible", state="visible")
        time.sleep(1) # Allow for any UI animations to settle

        print("App auto-opened Bible Browse dialog...")
        page.wait_for_selector("text=Old", state="visible")
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_testament.png"))

        print("Selecting Old Testament...")
        page.click("text=Old")
        page.wait_for_selector("button:has-text('PSA')") # Wait for book list
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_books.png"))

        print("Selecting Psalms...")
        page.click("button:has-text('PSA')")
        page.wait_for_selector("button:has-text('101-150')") # Wait for chapter chunks

        print("Selecting Chunk 101-150...")
        page.click("button:has-text('101-150')")
        page.wait_for_selector("button:text-is('119')") # Wait for chapter list
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_chapters.png"))

        print("Selecting Chapter 119...")
        page.click("button:text-is('119')")
        page.wait_for_selector("button:has-text('151-176')") # Wait for verse chunks

        print("Selecting Chunk 151-176...")
        page.click("button:has-text('151-176')")
        page.wait_for_selector("button:text-is('151')") # Wait for verse list
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_verses.png"))

        print("Selecting Verse 151...")
        page.click("button:text-is('151')")

        # After selecting a verse, the dialog should close and content should load
        print("Verifying dialog closed and verse content loaded...")
        page.wait_for_selector("text=Old", state="hidden")
        
        # Now check that the verse we selected is actually loaded on the page
        page.wait_for_selector(".verse-block[data-vid*='PSA.119.151']", timeout=10000)
        print("Successfully loaded verse PSA.119.151.")

        browser.close()
        print("\nBible Browse verification successful!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UI verification for the Bible Browse feature.")
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="Specify the data source: 'production' (default) or 'local'."
    )
    args = parser.parse_args()
    
    try:
        verify_bible_browse(source=args.source)
    except Exception as e:
        print(f"\nERROR: {e}")
        # Exit with a non-zero status code to indicate failure
        sys.exit(1)
