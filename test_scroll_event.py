from playwright.sync_api import sync_playwright
import time
import subprocess
import os

def run_test():
    print("Starting server...")
    subprocess.run(['pkill', '-f', 'http.server'])
    server_process = subprocess.Popen(['python3', '-m', 'http.server', '8080'], cwd=os.getcwd())
    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Use real app URLs to prevent CSP/import issues that cause blank screens
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            print("Navigating to HeIsRisen...")
            page.goto("http://127.0.0.1:8080/apps/HeIsRisen/index.html")
            page.wait_for_timeout(2000)

            page.evaluate("""() => {
                // Simulate an egg click that opens MAT 28:1
                const iframeOverlay = document.createElement('div');
                iframeOverlay.style.position = 'fixed';
                iframeOverlay.style.top = '0';
                iframeOverlay.style.left = '0';
                iframeOverlay.style.width = '100vw';
                iframeOverlay.style.height = '100vh';
                iframeOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                iframeOverlay.style.zIndex = '9999';
                iframeOverlay.style.display = 'flex';
                iframeOverlay.style.flexDirection = 'column';
                iframeOverlay.style.alignItems = 'center';
                iframeOverlay.style.justifyContent = 'center';

                const iframe = document.createElement('iframe');
                iframe.src = "http://127.0.0.1:8080/apps/365DBR/bible.html?book=MAT&chapter=28&verse=1";
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = '4px solid white';
                iframe.style.borderRadius = '10px';
                iframe.style.backgroundColor = 'white';

                iframeOverlay.appendChild(iframe);
                document.body.appendChild(iframeOverlay);
            }""")

            print("Waiting for iframe to load and scroll...")
            page.wait_for_timeout(5000) # Give React inside the iframe enough time to fetch and scroll

            # Additional wait specifically for scroll locks or smooth scroll to settle
            page.wait_for_timeout(2000)

            page.screenshot(path="tests/desktop_iframe_scroll2.png")
            print("Desktop screenshot saved.")
            context.close()
            browser.close()
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_test()
