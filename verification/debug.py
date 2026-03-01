import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser error: {err}"))

        page.goto("http://localhost:3000/bible.html")
        page.wait_for_timeout(2000)

        print("Took debug start")
        page.screenshot(path="verification/error.png")

        browser.close()

if __name__ == "__main__":
    run()
