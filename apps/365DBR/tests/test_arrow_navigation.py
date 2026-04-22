import os
import sys
import time
from playwright.sync_api import sync_playwright

# Ensure bible_common can be imported from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_arrow_navigation():
    """Test arrow key navigation in bible.html using production data"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser to debug
        page = browser.new_page()
        
        # Use production URL
        print("Loading bible.html from production...")
        page.goto("https://mt-sin.ai/365DBR/bible.html", timeout=60000)
        
        # Wait for content to load
        print("Waiting for content to load...")
        page.wait_for_selector(".verse-block", timeout=30000)
        time.sleep(2)
        
        # Get initial active verse
        active_verses = page.query_selector_all(".verse-block[data-active='true']")
        print(f"Initial active verses: {len(active_verses)}")
        if active_verses:
            vid = active_verses[0].get_attribute("data-vid")
            print(f"Starting verse: {vid}")
        
        # Press down arrow and observe
        print("\nTest 1: Press down arrow once")
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        active_verses = page.query_selector_all(".verse-block[data-active='true']")
        print(f"After 1st press: {len(active_verses)} active verses")
        if active_verses:
            vid = active_verses[0].get_attribute("data-vid")
            print(f"Current verse after 1st press: {vid}")
        
        # Press down arrow again
        print("\nTest 2: Press down arrow second time")
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        active_verses = page.query_selector_all(".verse-block[data-active='true']")
        print(f"After 2nd press: {len(active_verses)} active verses")
        if active_verses:
            vid = active_verses[0].get_attribute("data-vid")
            print(f"Current verse after 2nd press: {vid}")
        
        # Take screenshots
        test_dir = os.path.dirname(os.path.abspath(__file__))
        page.screenshot(path=os.path.join(test_dir, "arrow_nav_before.png"))
        time.sleep(5)
        page.screenshot(path=os.path.join(test_dir, "arrow_nav_after.png"))
        
        browser.close()
        print("\nArrow navigation test complete!")

if __name__ == "__main__":
    test_arrow_navigation()
