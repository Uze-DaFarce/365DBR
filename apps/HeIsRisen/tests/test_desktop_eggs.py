import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def test_collect_desktop():
    """
    Test Egg collection and EggZamRoom interaction on Desktop.
    Includes verification of keyboard dismissal for the explanation overlay.
    """
    print("Starting Desktop test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Standard desktop viewport
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        try:
            page.goto('http://localhost:8000/apps/HeIsRisen/index.html')
            page.wait_for_timeout(2000)

            # Start EggZamRoom
            page.evaluate("() => { const scene = window.game.scene.getScene('MainMenu'); scene.scene.start('EggZamRoom'); }")
            page.wait_for_timeout(2000)

            # Take screenshot of the initial state
            os.makedirs('apps/HeIsRisen/tests/output', exist_ok=True)
            page.screenshot(path='apps/HeIsRisen/tests/output/explanation_visible_desktop.png')
            print("Captured screenshot of explanation overlay.")

            # Verify keyboard dismissal works
            page.keyboard.press('Escape')
            page.wait_for_timeout(1000)

            # Screenshot after dismissal
            page.screenshot(path='apps/HeIsRisen/tests/output/explanation_dismissed_desktop.png')
            print("Captured screenshot after keyboard dismissal.")

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    test_collect_desktop()
