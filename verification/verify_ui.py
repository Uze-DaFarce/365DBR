import time
from playwright.sync_api import sync_playwright
import subprocess
import os

def run_test():
    # Start server
    print("Starting server...")
    server = subprocess.Popen(["python3", "-m", "http.server", "8002"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch()
            page = browser.new_page()

            print("Navigating...")
            page.goto("http://localhost:8002/index.html?startDate=0203")

            # Wait for meaningful content (e.g. verse)
            # Escaping dots in selector for ID
            print("Waiting for content...")
            page.wait_for_selector("#footer", timeout=10000)

            print("Taking screenshot...")
            page.screenshot(path="verification/screenshot.png")

            print("Verification Complete.")
            browser.close()
    except Exception as e:
        print(f"Error: {e}")
        # Print page content for debugging if possible
    finally:
        server.terminate()

if __name__ == "__main__":
    run_test()
