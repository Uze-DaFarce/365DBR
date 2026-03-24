from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu', '--disable-webgl', '--use-gl=swiftshader'])
        context = browser.new_context()
        page = context.new_page()

        print("Loading Desktop App...")
        page.goto("http://localhost:8080/HeIsRisen/")
        page.wait_for_timeout(2000)

        # Click anywhere to start
        page.mouse.click(640, 360)
        page.wait_for_timeout(1000)

        print("Clicking START NEW GAME on Main Menu (right side)...")
        # Center is at width/2, height*0.8 + 50 = 640, 576+50 = 626. Button width is 400.
        # Right edge is 640 + 200 = 840. We click at 820.
        page.mouse.click(820, 626)
        page.wait_for_timeout(1000)

        # Click confirmation YES button right side to ensure that works too
        print("Clicking YES on confirmation...")
        # Yes button is at -100, +50 from center. Center is 640, 360.
        # X: 540. Width is 100. Center is 540. Right edge is 590. Click at 580.
        page.mouse.click(580, 410)
        page.wait_for_timeout(2000)

        # Click PLAY NOW
        print("Clicking PLAY NOW/CONTINUE THE HUNT on the right side...")
        # Button is roughly at 640, 576. Width is 400. Center is 640. Right edge is 840. Click at 820.
        page.mouse.click(820, 576)
        page.wait_for_timeout(2000)

        # We are on MapScene. Click the first map zone (e.g. Garden of Gethsemane)
        print("Clicking Map Zone...")
        page.mouse.click(387, 554)
        page.wait_for_timeout(2000)

        print("Opening Settings...")
        page.mouse.click(1250, 30) # Cog is at top right
        page.wait_for_timeout(1000)

        # Click START NEW GAME button but on the far RIGHT side to test the hitbox fix!
        # Screen width is 1280, center is 640. Modal height logic: y + height - 50 = 360 + 200 - 50 = 510.
        # Button width is 250, so right edge is 640 + 125 = 765. Let's click at 750, 510.
        print("Clicking START NEW GAME on the right side...")
        page.mouse.click(750, 510)
        page.wait_for_timeout(1000)

        page.screenshot(path="apps/HeIsRisen/tests/settings_hitbox_desktop.png")

        print("Clicking No on the confirmation modal (right side)...")
        # No button is at 640 + 100 = 740. Y is 360 + 50 = 410. Width is 100.
        # Right edge is 740 + 50 = 790. Click at 780.
        page.mouse.click(780, 410)
        page.wait_for_timeout(1000)

        # Close settings
        print("Closing Settings...")
        page.mouse.click(1250, 30)
        page.wait_for_timeout(1000)

        print("Harvesting...")
        page.mouse.move(640, 360)
        page.wait_for_timeout(500)
        # Click around to find an egg, then pause for the harvest animation to play
        page.mouse.click(640, 360)
        page.wait_for_timeout(200)
        page.mouse.click(400, 400)
        page.wait_for_timeout(200)
        page.mouse.click(800, 300)
        page.wait_for_timeout(200)
        page.mouse.click(200, 600)
        # Wait enough time for the harvest animation to actually appear on screen
        page.wait_for_timeout(1000)

        page.screenshot(path="apps/HeIsRisen/tests/harvest_desktop.png")
        page.wait_for_timeout(1000)

        context.close()
        browser.close()

if __name__ == "__main__":
    run()