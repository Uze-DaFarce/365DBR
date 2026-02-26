import os
import json
import time
import shutil
import threading
import http.server
import socketserver
import argparse
import sys
from playwright.sync_api import sync_playwright

# Use port 0 to let OS choose a free port
DIST_DIR = "dist"
DATA_DIR = "data"

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

def compile_readings(page, readings, base_url, limit=None):
    print("Compiling Daily Readings...")
    total = len(readings)
    if limit:
        print(f"Limiting to first {limit} days.")
        readings = readings[:limit]
        total = limit

    # Create dist/reading directory structure
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    for i, day in enumerate(readings):
        mmdd = day['day'] # e.g. "0225"

        # Check if data exists locally before compiling
        local_data_path = os.path.join(DATA_DIR, mmdd)
        if not os.path.exists(local_data_path):
            # print(f"[{i+1}/{total}] Skipping {mmdd} (No local data found)")
            print(f"[{i+1}/{total}] Skipping {mmdd}", end="\r")
            continue

        # Determine output path: dist/0225/index.html
        day_dir = os.path.join(DIST_DIR, mmdd)
        if not os.path.exists(day_dir):
            os.makedirs(day_dir)

        output_file = os.path.join(day_dir, "index.html")

        url = f"{base_url}/index.html?startDate={mmdd}"
        print(f"[{i+1}/{total}] Processing {mmdd}...", end="\r")

        try:
            response = page.goto(url, wait_until="networkidle")
            if not response:
                print(f"\nFailed to load {url}: No response")
                continue

            if response.status != 200:
                print(f"\nFailed to load {url}: Status {response.status}")
                continue

            # Wait for content to load (verse blocks)
            try:
                page.wait_for_selector(".verse-block", timeout=10000)
            except Exception as e:
                print(f"\nTimeout waiting for content on {mmdd}: {e}")
                # page.screenshot(path=f"error_{mmdd}.png")
                continue

            # Get HTML
            # Strip out script tags to ensure the page remains static and doesn't try to re-hydrate/fetch data
            # which fails in offline/file protocol scenarios and is unnecessary for crawlers.
            content = page.evaluate("""() => {
                // Remove all script tags
                document.querySelectorAll('script').forEach(el => el.remove());
                // Also remove the importmap if separate
                document.querySelectorAll('link[rel="modulepreload"]').forEach(el => el.remove());
                return document.documentElement.outerHTML;
            }""")

            # Add DOCTYPE back since evaluate returns the element
            full_html = f"<!DOCTYPE html>\n{content}"

            # Save to dist
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_html)

        except Exception as e:
            print(f"\nError processing {mmdd}: {e}")

    print("\nDaily Readings Compilation Complete.        ")

def compile_bible(page, readings, base_url):
    print("Compiling Bible Browser... (Not Implemented)")
    # Placeholder for future expansion
    pass

def main():
    parser = argparse.ArgumentParser(description="Compile the 365DBR site to static HTML.")
    parser.add_argument("--limit", type=int, help="Limit the number of days to process (for testing).")
    args = parser.parse_args()

    # 1. Prepare Dist
    print(f"Cleaning {DIST_DIR}...")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)

    # 2. Copy Assets
    print("Copying assets...")
    shutil.copytree(DATA_DIR, os.path.join(DIST_DIR, DATA_DIR))

    # Copy root HTMLs to dist root (for spa fallback)
    shutil.copy("index.html", os.path.join(DIST_DIR, "index.html"))
    shutil.copy("bible.html", os.path.join(DIST_DIR, "bible.html"))

    if os.path.exists(".htaccess"):
        shutil.copy(".htaccess", os.path.join(DIST_DIR, ".htaccess"))

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
            readings = json.load(f)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            compile_readings(page, readings, base_url, limit=args.limit)

            browser.close()

    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)

    print(f"Compilation finished! Static site generated in '{DIST_DIR}'.")

if __name__ == "__main__":
    main()
