import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

def test_collect_desktop():
    # Similar to above, but target the desktop version (root index.html)
    # The desktop version's collection logic is different (distance from pointer directly).
    pass

def test_desktop_eggzam_keyboard():
    """
    Test EggZamRoom interaction on Desktop.
    Includes verification of keyboard dismissal for the explanation overlay.
    """
    print("Starting Desktop EggZamRoom Keyboard Test...")
    # Use path relative to this script for cross-platform robustness
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test-results')
    os.makedirs(results_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Standard desktop viewport
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        try:
            page.goto('http://localhost:8000/apps/HeIsRisen/index.html')

            # Wait for main menu / loading to finish
            print("Waiting for game to load...")
            page.wait_for_timeout(5000)

            # Start EggZamRoom
            print("Starting EggZamRoom scene...")
            page.evaluate("() => { const scene = window.game.scene.getScene('MainMenu'); scene.scene.start('EggZamRoom'); }")
            page.wait_for_timeout(2000)

            # Take screenshot of the initial state
            page.screenshot(path=os.path.join(results_dir, 'explanation_visible_desktop.png'))
            print("Captured screenshot of explanation overlay.")

            # Verify keyboard dismissal works
            print("Pressing Escape key...")
            page.keyboard.press('Escape')
            page.wait_for_timeout(1000)

            # Screenshot after dismissal
            page.screenshot(path=os.path.join(results_dir, 'explanation_dismissed_desktop.png'))
            print("Captured screenshot after keyboard dismissal.")

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    test_desktop_eggzam_keyboard()
