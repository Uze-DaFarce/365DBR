from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu', '--disable-webgl', '--use-gl=swiftshader'])
        # Mobile viewport 640x360 landscape
        context = browser.new_context(viewport={'width': 640, 'height': 360})
        page = context.new_page()

        print("Loading Mobile App...")
        page.goto("http://localhost:8080/HeIsRisen/m/")
        page.wait_for_timeout(3000)

        # Click anywhere to start
        page.mouse.click(320, 180)
        page.wait_for_timeout(2000)

        # Click PLAY NOW on the right side
        print("Clicking PLAY NOW...")
        # Mobile center is 320, 290. Button width is 400.
        # Click on right side: 320 + 150 = 470
        page.mouse.click(470, 290)
        page.wait_for_timeout(2000)

        # We are on MapScene. Click the first map zone (Gethsemane)
        print("Clicking Map Zone...")
        page.mouse.click(193, 277)
        page.wait_for_timeout(2000)

        # Click settings cog to open settings menu and test "START NEW GAME" button hitbox
        print("Opening Settings...")
        page.mouse.click(610, 25) # Cog is at top right
        page.wait_for_timeout(1000)

        # Click START NEW GAME button but on the far RIGHT side to test the hitbox fix!
        print("Clicking START NEW GAME on the right side...")
        # Screen width is 640. Center is 320.
        # Content top starts slightly offset. Y position is y + height - 40 in the Modal.
        # Modal is centered at 320, 180. The button is placed at 320, 180 + 100 = 280 roughly.
        # Button width is 200, so right edge is 420. Click at 400, 280.
        page.mouse.click(400, 280)
        page.wait_for_timeout(1000)

        page.screenshot(path="apps/HeIsRisen/tests/settings_hitbox_mobile.png")

        # Click No on confirmation modal
        # No button is roughly right side of the box. Center is at width/2 + 100, height/2 + 50
        # Mobile is 640x360. Center is 320, 180. No button is at 320 + 100 = 420, 180 + 50 = 230.
        # Width is 100. Right edge is 420 + 50 = 470. We click at 460.
        page.mouse.click(460, 230)
        page.wait_for_timeout(1000)

        # Close settings
        print("Closing Settings...")
        page.mouse.click(500, 30)
        page.wait_for_timeout(1000)

        # Harvest an egg
        print("Harvesting...")
        page.mouse.move(320, 180)
        page.mouse.down()
        page.wait_for_timeout(500)
        page.mouse.move(200, 200)
        page.wait_for_timeout(500)
        page.screenshot(path="apps/HeIsRisen/tests/harvest_mobile.png")
        page.mouse.up()

        page.wait_for_timeout(1000)

        context.close()
        browser.close()

if __name__ == "__main__":
    run()
