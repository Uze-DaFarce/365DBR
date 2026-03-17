import os
from playwright.sync_api import Page, expect, sync_playwright

def verify_game(page: Page):
    page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"Browser error: {exc}"))

    print("Navigating to desktop game...")
    page.goto("http://localhost:8000/apps/HeIsRisen/index.html")
    page.wait_for_timeout(5000)
    page.screenshot(path="verification/test_black_screen.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        try:
            verify_game(page)
        finally:
            context.close()
        browser.close()
