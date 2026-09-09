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
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from bible_common import validate_safe_path, validate_safe_relative_path

DATA_DIR = "data"
PRODUCTION_DATA_URL = "https://mt-sin.ai/365DBR/data"
BASE_SITE_URL = "https://mt-sin.ai"
SITEMAP_PATH = "../../sitemap.xml"

def start_server(server_ready_event, port_container):
    try:
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
        with socketserver.TCPServer(("", 0), QuietHandler) as httpd:
            port = httpd.server_address[1]
            port_container[0] = port
            server_ready_event.set()
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")
        server_ready_event.set()

def setup_data_interception(page, base_url):
    def handle_route(route):
        url = route.request.url
        split_token = "/data/"
        
        if split_token in url:
            try:
                rel_path = url.split(split_token)[1]
                if not validate_safe_relative_path(rel_path):
                    print(f"  [Blocked] Unsafe path requested: {rel_path}")
                    route.abort('accessdenied')
                    return

                local_path = os.path.join(DATA_DIR, rel_path.replace("/", os.sep))
                if os.path.exists(local_path) and os.path.isfile(local_path):
                    print(f"  [Served Local] {rel_path}")
                    with open(local_path, "rb") as f:
                        route.fulfill(status=200, body=f.read(), content_type="application/json")
                        return

                if rel_path.endswith(".json"):
                    prod_url = f"{PRODUCTION_DATA_URL}/{rel_path}"
                    print(f"  [Fallback Prod] {prod_url}")
                    try:
                        resp = requests.get(prod_url, timeout=5)
                        if resp.status_code == 200:
                            route.fulfill(status=200, body=resp.content, content_type="application/json")
                            return
                    except Exception as e:
                        print(f"  [Fallback Error] {prod_url}: {e}")

            except Exception as e:
                print(f"Interceptor Error: {e}")

        route.continue_()
    page.route("**/data/**/*.json", handle_route)

def compile_readings(browser, readings, base_url, limit=None):
    print("Compiling Daily Readings...")
    total = len(readings)
    if limit:
        readings = readings[:limit]
        total = limit

    page = browser.new_page()
    
    # 🔴 DIAGNOSTIC LISTENERS 🔴
    page.on("console", lambda msg: print(f"  [React Console]: {msg.text}"))
    page.on("pageerror", lambda err: print(f"  [JS CRASH!]: {err}"))
    
    setup_data_interception(page, base_url)

    for i, day in enumerate(readings):
        if i > 0 and i % 60 == 0:
            page.close()
            page = browser.new_page()
            page.on("console", lambda msg: print(f"  [React Console]: {msg.text}"))
            page.on("pageerror", lambda err: print(f"  [JS CRASH!]: {err}"))
            setup_data_interception(page, base_url)

        mmdd = day['day']
        day_dir = os.path.join(DATA_DIR, mmdd)
        os.makedirs(day_dir, exist_ok=True)
        output_file = os.path.join(day_dir, "index.html")

        url = f"{base_url}/index.html?startDate={mmdd}&static=true"
        print(f"\n[{i+1}/{total}] Processing {mmdd}...")

        try:
            response = page.goto(url, wait_until="networkidle", timeout=15000)
            if not response or response.status != 200:
                raise RuntimeError(f"Status {response.status if response else 'None'}")

            page.wait_for_selector(".verse-block", timeout=6000)

            manifest_path = os.path.join(DATA_DIR, mmdd, "manifest.json")
            manifest_content = None

            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_content = json.load(f)
            else:
                try:
                    r = requests.get(f"{PRODUCTION_DATA_URL}/{mmdd}/manifest.json", timeout=5)
                    if r.status_code == 200: manifest_content = r.json()
                except: pass

            full_data_payload = {}
            if manifest_content:
                full_data_payload['manifest'] = manifest_content
                full_data_payload['files'] = {}
                for fname in manifest_content.get('files', []):
                    fpath = os.path.join(DATA_DIR, mmdd, fname)
                    if os.path.exists(fpath):
                        with open(fpath, 'r', encoding='utf-8') as f:
                            full_data_payload['files'][fname] = json.load(f)
                    else:
                        try:
                            r = requests.get(f"{PRODUCTION_DATA_URL}/{mmdd}/{fname}", timeout=5)
                            if r.status_code == 200: full_data_payload['files'][fname] = r.json()
                        except: pass

            json_str = json.dumps(full_data_payload, ensure_ascii=False)

            page.evaluate(f"""(data) => {{
                let script = document.getElementById('preloaded-data');
                if (!script) {{
                    script = document.createElement('script');
                    script.id = 'preloaded-data';
                    script.type = 'application/json';
                    document.head.appendChild(script);
                }}
                script.textContent = data;
            }}""", json_str)

            canonical_url = f"{BASE_SITE_URL}/365DBR/data/{mmdd}/index.html"
            page.evaluate(f"""(canonUrl) => {{
                document.querySelectorAll('a[href*="bible.html"]').forEach(link => link.remove());
                let link = document.querySelector('link[rel="canonical"]');
                if (!link) {{
                    link = document.createElement('link');
                    link.setAttribute('rel', 'canonical');
                    document.head.appendChild(link);
                }}
                link.setAttribute('href', canonUrl);
            }}""", canonical_url)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(page.content())

        except Exception as e:
            print(f"  [Error]: {e}")
            continue

    page.close()
    print("\nDaily Readings Compilation Complete.")

def update_sitemap(all_readings, sitemap_path=SITEMAP_PATH):
    print(f"Updating {sitemap_path}...")
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    core_urls = [
        {"loc": f"{BASE_SITE_URL}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{BASE_SITE_URL}/HeIsRisen/index.html", "priority": "0.9", "changefreq": "monthly"},
        {"loc": f"{BASE_SITE_URL}/m/index.html", "priority": "0.7", "changefreq": "weekly"},
    ]
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    for item in core_urls:
        xml_lines.append(f"  <url>\n    <loc>{item['loc']}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{item['changefreq']}</changefreq>\n    <priority>{item['priority']}</priority>\n  </url>")

    for r in all_readings:
        xml_lines.append(f"  <url>\n    <loc>{BASE_SITE_URL}/365DBR/data/{r['day']}/index.html</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>")
    
    xml_lines.append("</urlset>")
    with open(sitemap_path, "w", encoding="utf-8") as f: f.write("\n".join(xml_lines) + "\n")

def validate_args(args):
    if args.day and not re.match(r'^(\d{4}|\d{4}-\d{4})$', args.day): raise ValueError("Invalid day format.")
    if args.month and not re.match(r'^(\d{2}|\d{2}-\d{2})$', args.month): raise ValueError("Invalid month format.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day"); parser.add_argument("--month"); parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int); parser.add_argument("--sitemap-only", action="store_true")
    args = parser.parse_args()

    try: validate_args(args)
    except ValueError as e: return print(e)

    with open(os.path.join(DATA_DIR, "readings.json"), "r", encoding="utf-8") as f:
        all_readings = json.load(f)

    if args.sitemap_only: return update_sitemap(all_readings)

    server_ready = threading.Event()
    port_container = [0]
    threading.Thread(target=start_server, args=(server_ready, port_container), daemon=True).start()
    server_ready.wait()
    if port_container[0] == 0: return print("Failed to start server.")

    base_url = f"http://localhost:{port_container[0]}"
    targets = all_readings
    if args.day:
        if '-' in args.day: targets = [r for r in all_readings if args.day.split('-')[0] <= r['day'] <= args.day.split('-')[1]]
        else: targets = [r for r in all_readings if r['day'] == args.day]

    with sync_playwright() as p:
        # 🔴 RUNNING HEADFUL SO YOU CAN SEE THE ERROR 🔴
        browser = p.chromium.launch(headless=False)
        compile_readings(browser, targets, base_url, limit=args.limit)
        browser.close()

    update_sitemap(all_readings)

if __name__ == "__main__":
    main()