import os
import json
import time
import shutil
import threading
import http.server
import socketserver
import argparse
import sys
import re
import requests
from playwright.sync_api import sync_playwright

# Use port 0 to let OS choose a free port
DATA_DIR = "data"
PRODUCTION_DATA_URL = "https://mt-sin.ai/365DBR/data"

def start_server(server_ready_event, port_container):
    """Starts a simple HTTP server to serve the React app on a random port."""
    try:
        # Change to the directory containing index.html (current directory)
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass # Suppress logs

        with socketserver.TCPServer(("", 0), QuietHandler) as httpd:
            port = httpd.server_address[1]
            port_container[0] = port
            # print(f"Serving at port {port}")
            server_ready_event.set()
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")
        server_ready_event.set() # Unblock main thread even on error

def setup_data_interception(page, base_url):
    """
    Intercepts requests to /data/ and serves:
    1. Local file if it exists (Priority)
    2. Production file if local is missing (Fallback)
    """
    def handle_route(route):
        request = route.request
        url = request.url

        # Check if it's a data request
        if "/data/" in url:
            # Extract relative path after /data/
            # Example: http://localhost:1234/data/0101/manifest.json -> 0101/manifest.json
            try:
                # Find where /data/ starts
                split_token = "/data/"
                if split_token in url:
                    rel_path = url.split(split_token)[1]

                    if ".." in rel_path:
                        route.abort('accessdenied')
                        return

                    # 1. Check Local File
                    local_path = os.path.join(DATA_DIR, rel_path.replace("/", os.sep))
                    if os.path.exists(local_path) and os.path.isfile(local_path):
                        # print(f"  [Local] Serving {rel_path}")
                        with open(local_path, "rb") as f:
                            content = f.read()
                            route.fulfill(status=200, body=content, content_type="application/json")
                            return

                    # 2. Check Production (Fallback)
                    # Only fallback if it's a JSON file (manifest or reading data)
                    if rel_path.endswith(".json"):
                        prod_url = f"{PRODUCTION_DATA_URL}/{rel_path}"
                        print(f"  [Fallback] Fetching {rel_path} from Production...")
                        try:
                            resp = requests.get(prod_url)
                            if resp.status_code == 200:
                                route.fulfill(status=200, body=resp.content, content_type="application/json")
                                return
                            else:
                                print(f"  [Error] Production fetch failed: {resp.status_code}")
                        except Exception as e:
                            print(f"  [Error] Production fetch error: {e}")

            except Exception as e:
                print(f"Interceptor Error: {e}")

        # Continue normally if not handled
        route.continue_()

    # Intercept everything under the base url that looks like data
    # Note: The React app requests relative paths like "data/...", which resolve to base_url/data/...
    page.route("**/data/**/*.json", handle_route)

def compile_readings(page, readings, base_url, limit=None):
    print("Compiling Daily Readings...")
    total = len(readings)
    if limit:
        print(f"Limiting to first {limit} days.")
        readings = readings[:limit]
        total = limit

    for i, day in enumerate(readings):
        mmdd = day['day'] # e.g. "0225"

        # Determine output path: data/0225/index.html
        day_dir = os.path.join(DATA_DIR, mmdd)
        if not os.path.exists(day_dir):
            os.makedirs(day_dir)

        output_file = os.path.join(day_dir, "index.html")

        url = f"{base_url}/index.html?startDate={mmdd}&static=true"
        print(f"[{i+1}/{total}] Processing {mmdd}...", end="\r")

        try:
            response = page.goto(url, wait_until="networkidle")
            if not response:
                raise RuntimeError(f"Failed to load {url}: No response")

            if response.status != 200:
                raise RuntimeError(f"Failed to load {url}: Status {response.status}")

            # Wait for content to load (verse blocks)
            try:
                page.wait_for_selector(".verse-block", timeout=5000)
            except Exception as e:
                raise RuntimeError(f"Timeout waiting for content on {mmdd}. (Data likely missing in both Local and Production)") from e

            # --- Data Embedding Logic ---

            # Step 1: Get Manifest
            manifest_path = os.path.join(DATA_DIR, mmdd, "manifest.json")
            manifest_content = None

            # Try Local Manifest
            if os.path.exists(manifest_path):
                 with open(manifest_path, 'r', encoding='utf-8') as f:
                     manifest_content = json.load(f)
            else:
                # Try Prod Manifest
                try:
                    r = requests.get(f"{PRODUCTION_DATA_URL}/{mmdd}/manifest.json")
                    if r.status_code == 200:
                        manifest_content = r.json()
                except:
                    pass

            full_data_payload = {}
            if manifest_content:
                full_data_payload['manifest'] = manifest_content
                full_data_payload['files'] = {}
                for fname in manifest_content.get('files', []):
                    fpath = os.path.join(DATA_DIR, mmdd, fname)
                    # Try Local File
                    if os.path.exists(fpath):
                        with open(fpath, 'r', encoding='utf-8') as f:
                            full_data_payload['files'][fname] = json.load(f)
                    else:
                        # Try Prod File
                        try:
                            r = requests.get(f"{PRODUCTION_DATA_URL}/{mmdd}/{fname}")
                            if r.status_code == 200:
                                full_data_payload['files'][fname] = r.json()
                        except:
                            pass

            # Serialize Data
            json_str = json.dumps(full_data_payload, ensure_ascii=False)

            # Inject Script into Head
            page.evaluate(f"""(data) => {{
                const script = document.createElement('script');
                script.id = 'preloaded-data';
                script.type = 'application/json';
                script.textContent = data;
                document.head.appendChild(script);
            }}""", json_str)

            # Get full HTML (with injected script + React scripts)
            # We do NOT strip scripts anymore, so interactivity works.
            content = page.content()

            # Save to data directory
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            raise RuntimeError(f"Error processing {mmdd}: {e}") from e

    print("\nDaily Readings Compilation Complete.        ")

def validate_args(args):
    """
    Validates command line arguments to prevent injection or misuse.
    """
    if args.day:
        if not re.match(r'^(\d{4}|\d{4}-\d{4})$', args.day):
             raise ValueError(f"[Input Error] Invalid day format: '{args.day}'. Expected MMDD or MMDD-MMDD.")

    if args.month:
        if not re.match(r'^(\d{2}|\d{2}-\d{2})$', args.month):
             raise ValueError(f"[Input Error] Invalid month format: '{args.month}'. Expected MM or MM-MM.")

def main():
    parser = argparse.ArgumentParser(description="Compile the 365DBR site to static HTML.")
    parser.add_argument("--day", help="Compile specific day (e.g., 0201) or range (0201-0210)")
    parser.add_argument("--month", help="Compile specific month (e.g., 02) or range (02-03)")
    parser.add_argument("--all", action="store_true", help="Compile all days")
    parser.add_argument("--limit", type=int, help="Limit the number of days to process (for testing).")
    args = parser.parse_args()

    try:
        validate_args(args)
    except ValueError as e:
        print(e)
        return

    # 3. Start Server
    server_ready = threading.Event()
    port_container = [0]
    server_thread = threading.Thread(target=start_server, args=(server_ready, port_container), daemon=True)
    server_thread.start()

    server_ready.wait()
    port = port_container[0]
    if port == 0:
        print("Failed to start server.")
        return

    base_url = f"http://localhost:{port}"

    # 4. Run Playwright
    try:
        with open("data/readings.json", "r") as f:
            all_readings = json.load(f)

        # Filter Readings
        targets = []
        if args.day:
            if '-' in args.day:
                start, end = args.day.split('-')
                targets = [r for r in all_readings if r['day'] >= start and r['day'] <= end]
            else:
                targets = [r for r in all_readings if r['day'] == args.day]
        elif args.month:
            if '-' in args.month:
                start_m, end_m = args.month.split('-')
                s_int = int(start_m)
                e_int = int(end_m)
                def is_in_month_range(day_str, s, e):
                    m = int(day_str[:2])
                    if s <= e: return s <= m <= e
                    else: return m >= s or m <= e
                targets = [r for r in all_readings if is_in_month_range(r['day'], s_int, e_int)]
            else:
                targets = [r for r in all_readings if r['day'].startswith(args.month)]
        elif args.all:
            targets = all_readings
        elif args.limit:
            targets = all_readings
        else:
            print("Please specify --day, --month, --all, or --limit")
            sys.exit(0)

        if not targets:
            print("No readings found matching criteria.")
            sys.exit(0)

        print(f"Found {len(targets)} days to process.")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Setup Data Interception
            setup_data_interception(page, base_url)

            compile_readings(page, targets, base_url, limit=args.limit)

            browser.close()

    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)

    print(f"Compilation finished! Output in '{DATA_DIR}/<day>/index.html'.")

if __name__ == "__main__":
    main()
