import sys
import os
import subprocess
import time
sys.path.append(os.path.abspath('apps/HeIsRisen/tests'))
from playwright.sync_api import sync_playwright
import test_helpers as th

server_process = subprocess.Popen([sys.executable, '-m', 'http.server', '8080'])
time.sleep(1)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(record_video_dir="apps/HeIsRisen/tests/videos", viewport={"width": 375, "height": 667})
        page = context.new_page()
        page.goto('http://127.0.0.1:8080/apps/HeIsRisen/m/index.html')
        page.wait_for_timeout(3000)
        page.evaluate('''() => {
            window.game.registry.set('foundEggs', [{eggId: 1, categorized: false, symbolData: {category: "Christian", filename: "cross.png"}}]);
            window.game.scene.start('EggZamRoom');
        }''')
        page.wait_for_timeout(3000)

        # Click the "Egg-cellent" button to trigger the good egg animation and video
        page.mouse.click(250, 600) # approximate click on right button based on mobile layout

        # Wait for video to finish and popup to show
        page.wait_for_timeout(5000)

        page.screenshot(path='apps/HeIsRisen/tests/mobile_eggzam_room_completed.png')
        page.wait_for_timeout(1000)
        context.close()
        browser.close()
finally:
    server_process.terminate()
