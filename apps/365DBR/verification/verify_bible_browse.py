import os
from playwright.sync_api import sync_playwright
import time

def verify_bible_browse():
    with sync_playwright() as p:
        # iPhone 12 emulation
        iphone = p.devices['iPhone 12']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**iphone)
        page = context.new_page()

        # We are going to mock the api requests so it doesn't fail on local data
        page.route("**/*", lambda route: route.continue_())

        print("Navigating to app...")
        page.goto("https://mt-sin.ai/365DBR/bible.html")

        # Wait for page load
        page.wait_for_selector("text=Browse Bible", state="visible")
        time.sleep(1)

        print("Opening Bible Browse...")

        # The app auto-opens the dialog when no book is selected
        # Wait for the dialog to be fully visible by checking for the Old Testament button
        page.wait_for_selector("text=Old", state="visible")

        # Take a screenshot of Testament View
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_testament.png"))

        print("Selecting Old Testament...")
        page.click("text=Old")
        time.sleep(1)

        # Take a screenshot of Book View
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_books.png"))

        print("Selecting Psalms...")
        page.click("button:has-text('PSA')")
        time.sleep(1)

        print("Selecting Chunk 101-150...")
        page.click("button:has-text('101-150')")
        time.sleep(1)

        # Take a screenshot of Chapter View
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_chapters.png"))

        print("Selecting Chapter 119...")
        page.click("button:text-is('119')")
        time.sleep(1)

        print("Selecting Chunk 151-176...")
        page.click("button:has-text('151-176')")
        time.sleep(1)

        # Take a screenshot of Verse View (50 buttons)
        page.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "browse_verses.png"))

        print("Selecting Verse 151...")
        page.click("button:text-is('151')")
        time.sleep(1)

        print("Verification complete. Dialog should be closed.")
        # Wait for dialog to disappear by waiting for the testament button to be hidden
        page.wait_for_selector("text=Old", state="hidden")
        print("Dialog successfully closed.")

        browser.close()

if __name__ == "__main__":
    verify_bible_browse()
