import argparse
import os
import sys
import asyncio
import requests
from playwright.async_api import async_playwright

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

async def setup_data_interception(page, source):
    """
    Intercepts network requests to the /data/ directory and serves them
    from the specified source (local or production).
    """
    async def handle_route(route):
        request = route.request
        url = request.url

        if "/data/" in url:
            try:
                rel_path = url.split("/data/")[1]
                if not validate_safe_relative_path(rel_path):
                    await route.abort('accessdenied')
                    return

                if source == "local":
                    local_path = os.path.join(DATA_DIR, rel_path.replace("/", os.sep))
                    if os.path.exists(local_path):
                        with open(local_path, "rb") as f:
                            content = f.read()
                        await route.fulfill(status=200, body=content, content_type="application/json")
                    else:
                        await route.fulfill(status=404, body=b"File not found in local data")
                else: # production
                    prod_url = f"{PRODUCTION_DATA_URL}/{rel_path}"
                    try:
                        # NOTE: Using synchronous 'requests' here for simplicity.
                        # For heavy-duty async, a library like 'httpx' would be better.
                        resp = requests.get(prod_url, timeout=10)
                        resp.raise_for_status()
                        await route.fulfill(status=resp.status_code, body=resp.content, content_type=resp.headers.get("Content-Type"))
                    except requests.exceptions.RequestException as e:
                        print(f"[Production] Error fetching {prod_url}: {e}")
                        await route.abort()

            except Exception as e:
                print(f"[Interceptor Error] {e}")
                await route.abort()
            return

        await route.continue_()

    await page.route("**/data/**/*.json", handle_route)

async def run(source: str):
    print(f"Running Scroll Test with data source: '{source.upper()}'")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 800, 'height': 800})
        page = await context.new_page()

        # Setup data interception before navigating
        await setup_data_interception(page, source)

        try:
            # Navigate to a day with known psalm-to-proverb transition
            print("Navigating to page with startDate=0307...")
            await page.goto("https://mt-sin.ai/365DBR/index.html?startDate=0307", wait_until="networkidle")
            await page.wait_for_selector(".verse-block")
            print("Page loaded.")

            # Jump to the Psalms section
            await page.click("button[title='Jump to Psalms']")
            await page.wait_for_timeout(1000) # Allow for scroll animation

            print("Walking through end of Psalms to Proverbs (0307)...")
            for i in range(16):
                await page.keyboard.press("ArrowDown")
                await page.wait_for_timeout(400) # Wait for UI to update

                # Get the ID of the currently focused verse block
                active_verse_id = await page.evaluate('''() => {
                    const activeEl = document.querySelector('.verse-block > div > div.bg-stone-900, .verse-block > div > div.bg-emerald-100, .verse-block > div > div.bg-rose-100');
                    return activeEl ? activeEl.closest('.verse-block').id : null;
                }''')
                print(f"Step {i+1}: Active verse is '{active_verse_id}'")
                if not active_verse_id:
                    raise AssertionError("Failed to find an active verse during scroll test.")

            print("\nScroll test completed successfully.")

        except Exception as e:
            await page.screenshot(path="tests/scroll_test_error.png"))
            print(f"\nERROR: {e}")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test verse scrolling behavior.")
    parser.add_argument(
        "--source",
        type=str,
        choices=['local', 'production'],
        default='production',
        help="Specify the data source: 'production' (default) or 'local'."
    )
    args = parser.parse_args()

    try:
        asyncio.run(run(source=args.source))
    except Exception as e:
        sys.exit(1)
