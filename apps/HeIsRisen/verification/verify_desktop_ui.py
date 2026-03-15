import asyncio
from playwright.async_api import async_playwright
import os

async def verify_desktop_map():
    print("Starting Desktop Map verification...")

    # Ensure background server is running (fallback port 8080)
    server_port = 8080

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Desktop viewport
        context = await browser.new_context(viewport={'width': 1376, 'height': 768})
        page = await context.new_page()

        # Load game
        await page.goto(f"http://localhost:{server_port}/")

        # Wait for the game canvas to load
        await page.wait_for_selector('canvas', state='attached')
        await asyncio.sleep(2) # Allow Phaser to initialize

        # Click the "PLAY NOW" text (which is actually a DOM element in this game)
        # However, looking at the code, it might just need a click anywhere on the canvas
        print("Clicking canvas to start...")
        await page.mouse.click(500, 500)

        # Wait for map scene
        print("Waiting for MapScene...")
        await asyncio.sleep(3) # allow transition

        # Take a screenshot
        screenshot_path = os.path.join(os.path.dirname(__file__), "desktop_map_scene_test.png")
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_desktop_map())
