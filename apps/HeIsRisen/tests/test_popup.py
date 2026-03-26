import os
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

def start_server(port, directory):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    httpd = HTTPServer(('', port), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

def create_mock_and_show_popup(page, app_path):
    page.goto(f"http://localhost:8080/{app_path}")
    page.wait_for_timeout(3000)

    # Click anywhere to bypass any intro or initialize audio context
    page.mouse.click(page.viewport_size['width'] // 2, page.viewport_size['height'] // 2)
    page.wait_for_timeout(1000)

    # Expose scenes and jump to EggZamRoom with a mock egg
    # Add dummy egg to localStorage since window.game isn't globally exposed
    page.evaluate('''() => {
        const dummyGameState = {
            currentLevelIndex: 1,
            foundEggs: [{
                eggId: 1,
                categorized: false,
                symbolData: {
                    name: "The Cross",
                    filename: "symbol-1",
                    explanation: "The cross represents Jesus’ sacrifice for our sins. The cross represents Jesus’ sacrifice for our sins. The cross represents Jesus’ sacrifice for our sins. The cross represents Jesus’ sacrifice for our sins. The cross represents Jesus’ sacrifice for our sins. The cross represents Jesus’ sacrifice for our sins.",
                    scripture: "John 3:16",
                    category: "Christian"
                }
            }],
            levels: [],
            highScore: 0,
            sfx: true,
            music: true
        };
        localStorage.setItem('heIsRisenGameState', JSON.stringify(dummyGameState));
        // Force reload so game picks up local storage
        window.location.reload();
    }''')

    page.wait_for_timeout(3000)

    # We are in MapScene. Click the Play/Menu to bypass things if needed.
    page.mouse.click(page.viewport_size['width'] // 2, page.viewport_size['height'] // 2)
    page.wait_for_timeout(1000)

    # Click Machine on map
    # Machine coords are approx top-middle
    page.mouse.click(page.viewport_size['width'] // 2, page.viewport_size['height'] // 4)
    page.wait_for_timeout(2000)

    # Click screen coords to trigger sorting to left bottle
    page.mouse.click(page.viewport_size['width'] // 4, page.viewport_size['height'] // 2)
    page.wait_for_timeout(1000)

def verify_desktop():
    print("Starting desktop test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        create_mock_and_show_popup(page, "apps/HeIsRisen/")

        page.screenshot(path="apps/HeIsRisen/tests/verification/desktop_popup.png")
        print("Desktop popup screenshot saved.")

        # Press SPACE to open scripture iframe
        page.keyboard.press("Space")
        page.wait_for_timeout(2000)

        page.screenshot(path="apps/HeIsRisen/tests/verification/desktop_iframe.png")
        print("Desktop iframe screenshot saved.")

        # Click close button on iframe
        page.mouse.click(1240, 40) # Approximate close button coordinates top right
        page.wait_for_timeout(1000)

        # Press ESC to close popup
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        page.screenshot(path="apps/HeIsRisen/tests/verification/desktop_closed.png")
        print("Desktop closed screenshot saved.")

def verify_mobile():
    print("Starting mobile test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # iPhone 12/13 landscape dimension
        context = browser.new_context(
            viewport={'width': 844, 'height': 390},
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()

        create_mock_and_show_popup(page, "apps/HeIsRisen/m/")

        page.screenshot(path="apps/HeIsRisen/tests/verification/mobile_popup.png")
        print("Mobile popup screenshot saved.")

        # Press SPACE to open scripture iframe
        page.keyboard.press("Space")
        page.wait_for_timeout(2000)

        page.screenshot(path="apps/HeIsRisen/tests/verification/mobile_iframe.png")
        print("Mobile iframe screenshot saved.")

        # Click close button on iframe
        page.mouse.click(824, 20) # Approximate close button coordinates top right
        page.wait_for_timeout(1000)

        # Press ESC to close popup
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        page.screenshot(path="apps/HeIsRisen/tests/verification/mobile_closed.png")
        print("Mobile closed screenshot saved.")

if __name__ == "__main__":
    os.makedirs("apps/HeIsRisen/tests/verification", exist_ok=True)
    httpd = start_server(8080, ".")
    print("Server started on port 8080")

    try:
        verify_desktop()
        verify_mobile()
    finally:
        httpd.shutdown()
        print("Server shutdown")
