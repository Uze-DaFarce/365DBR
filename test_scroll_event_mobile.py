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

            # Test 2: Mobile
            mobile_context = browser.new_context(
                viewport={'width': 844, 'height': 390},
                is_mobile=True,
                has_touch=True
            )
            mobile_page = mobile_context.new_page()

            print("Navigating to Mobile view...")
            mobile_page.goto("http://127.0.0.1:8080/apps/HeIsRisen/m/index.html")
            mobile_page.wait_for_timeout(2000)

            mobile_page.evaluate("""() => {
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

            print("Waiting for iframe to load and scroll on mobile...")
            mobile_page.wait_for_timeout(5000)
            mobile_page.wait_for_timeout(2000)

            mobile_page.screenshot(path="tests/mobile_iframe_scroll2.png")
            print("Mobile screenshot saved.")
            mobile_context.close()

            browser.close()
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_test()
