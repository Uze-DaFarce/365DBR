import asyncio
from playwright.async_api import async_playwright
import time
import os

async def verify_main_menu_buttons():
    os.makedirs('apps/HeIsRisen/verification/screenshots', exist_ok=True)

    # Needs a local server, we assume test_helpers.start_server will be running, or we just use python -m http.server 8080

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)

        # Test Desktop
        context_desktop = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page_desktop = await context_desktop.new_page()

        await page_desktop.goto("http://127.0.0.1:8080/")
        await page_desktop.evaluate("""
            window.localStorage.setItem('musicVolume', '0.0');
            window.localStorage.setItem('ambientVolume', '0.0');
            window.localStorage.setItem('sfxVolume', '0.0');
            // Force a save state to show the START NEW GAME button
            window.localStorage.setItem('heIsRisenGameState', JSON.stringify({
                eggData: [],
                sections: [],
                foundEggs: [1],
                stampedSections: [],
                correctCategorizations: 0,
                currentScore: 10
            }));
        """)
        await page_desktop.reload()

        await page_desktop.wait_for_selector("canvas", timeout=10000)

        # Click to start intro (dismissing "Click anywhere to start")
        await page_desktop.mouse.click(640, 360)
        await asyncio.sleep(2) # wait for animations and buttons to appear

        # Capture default state
        await page_desktop.screenshot(path="apps/HeIsRisen/verification/screenshots/desktop_main_menu_default.png")

        # Hover over PLAY NOW
        await page_desktop.mouse.move(640, 520) # Approx position of PLAY NOW mainBtnContainer
        await asyncio.sleep(0.5)
        await page_desktop.screenshot(path="apps/HeIsRisen/verification/screenshots/desktop_main_menu_hover_play.png")

        # Hover over START NEW GAME
        await page_desktop.mouse.move(640, 570) # Approx position of newGameBtnContainer
        await asyncio.sleep(0.5)
        await page_desktop.screenshot(path="apps/HeIsRisen/verification/screenshots/desktop_main_menu_hover_new.png")

        # Press START NEW GAME
        await page_desktop.mouse.down()
        await asyncio.sleep(0.1)
        await page_desktop.screenshot(path="apps/HeIsRisen/verification/screenshots/desktop_main_menu_press_new.png")
        await page_desktop.mouse.up()
        await asyncio.sleep(1) # wait for confirmation

        await context_desktop.close()

        # Test Mobile
        context_mobile = await browser.new_context(
            viewport={'width': 844, 'height': 390},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        )
        page_mobile = await context_mobile.new_page()

        await page_mobile.goto("http://127.0.0.1:8080/m/")
        await page_mobile.evaluate("""
            window.localStorage.setItem('musicVolume', '0.0');
            window.localStorage.setItem('ambientVolume', '0.0');
            window.localStorage.setItem('sfxVolume', '0.0');
            // Force a save state to show the START NEW GAME button
            window.localStorage.setItem('heIsRisenGameState', JSON.stringify({
                eggData: [],
                sections: [],
                foundEggs: [1],
                stampedSections: [],
                correctCategorizations: 0,
                currentScore: 10
            }));
        """)
        await page_mobile.reload()

        await page_mobile.wait_for_selector("canvas", timeout=10000)

        # Click to start intro
        await page_mobile.mouse.click(400, 200)
        await asyncio.sleep(2)

        await page_mobile.screenshot(path="apps/HeIsRisen/verification/screenshots/mobile_main_menu_default.png")

        # Hover over PLAY NOW
        await page_mobile.mouse.move(422, 312) # Approx position of mainBtnContainer
        await asyncio.sleep(0.5)
        await page_mobile.screenshot(path="apps/HeIsRisen/verification/screenshots/mobile_main_menu_hover_play.png")

        # Press PLAY NOW
        await page_mobile.mouse.down()
        await asyncio.sleep(0.1)
        await page_mobile.screenshot(path="apps/HeIsRisen/verification/screenshots/mobile_main_menu_press_play.png")
        await page_mobile.mouse.up()
        await asyncio.sleep(1)

        await context_mobile.close()
        await browser.close()
        print("Verification complete. Screenshots saved to apps/HeIsRisen/verification/screenshots/")

if __name__ == '__main__':
    asyncio.run(verify_main_menu_buttons())
