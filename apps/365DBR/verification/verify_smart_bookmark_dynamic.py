import argparse
import os
import sys
import time
import datetime
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

def run(source: str):
    print(f"Running Smart Bookmark verification with data source: '{source.upper()}'")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Set up data interception before any navigation
        setup_data_interception(page, source)

        # --- Test Setup ---
        now = datetime.datetime.now()
        today_mmdd = f"{now.month:02d}{now.day:02d}"
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_mmdd = f"{tomorrow.month:02d}{tomorrow.day:02d}"
        future = now + datetime.timedelta(days=2)
        future_mmdd = f"{future.month:02d}{future.day:02d}"
        initial_state = f'{{"date":"{today_mmdd}","focal":"lsv","compare":"kjv","verseId":"INIT.1.1"}}'

        # Must navigate first before setting localStorage
        print("Navigating to index.html and setting initial state...")
        page.goto("https://mt-sin.ai/365DBR/index.html", timeout=60000)

        # Set storage to simulate a previous session
        page.evaluate(f"localStorage.setItem('biblical_reading_state', '{initial_state}')")

        try:
            # 1. Navigate to TOMORROW (Allowed Future Date)
            print(f"\nNavigating to Tomorrow ({tomorrow_mmdd})...")
            page.goto(f"https://mt-sin.ai/365DBR/index.html?startDate={tomorrow_mmdd}", timeout=60000)

            saved_state = page.evaluate("localStorage.getItem('biblical_reading_state')")
            print(f"State after navigating to Tomorrow: {saved_state}")

            if f'"date":"{tomorrow_mmdd}"' in saved_state:
                print("PASS: Date was correctly updated for Tomorrow.")
            else:
                raise AssertionError(f"FAIL: Date was not updated for Tomorrow. Expected {tomorrow_mmdd}.")

            # 2. Navigate to DAY AFTER TOMORROW (Blocked Future Date)
            print(f"\nNavigating to Day After Tomorrow ({future_mmdd})...")
            page.goto(f"https://mt-sin.ai/365DBR/index.html?startDate={future_mmdd}", timeout=60000)

            saved_state_2 = page.evaluate("localStorage.getItem('biblical_reading_state')")
            print(f"State after navigating to Future+2: {saved_state_2}")

            if f'"date":"{tomorrow_mmdd}"' in saved_state_2:
                print("PASS: Date was not updated for a future date, preserving the last valid date.")
            elif f'"date":"{future_mmdd}"' in saved_state_2:
                raise AssertionError("FAIL: Date was updated for a future date, which should be blocked.")
            else:
                raise AssertionError(f"FAIL: State has an unexpected value: {saved_state_2}")

            page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "smart_bookmark_dynamic_test.png"))
            print("\nSmart Bookmark verification successful!")

        except Exception as e:
            page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "smart_bookmark_error.png"))
            print(f"\nERROR: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify the smart bookmark logic for future dates.")
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="Specify the data source: 'production' (default) or 'local'."
    )
    args = parser.parse_args()

    try:
        run(source=args.source)
    except Exception as e:
        # The error is already printed, just exit with a failure code
        sys.exit(1)
