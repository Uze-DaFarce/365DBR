import subprocess
import time
from playwright.sync_api import sync_playwright

p_server = subprocess.Popen(["npx", "http-server", "-p", "8080", "-c-1"], cwd="apps/HeIsRisen", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8080/")

        # Wait for the game to load completely
        page.wait_for_selector('canvas', state='attached')

        time.sleep(10)

        cache_keys = page.evaluate("() => window.game.scene.getScene('MainMenu').cache.audio.getKeys()")
        print(f"MainMenu cache audio keys: {cache_keys}")

        browser.close()
finally:
    p_server.terminate()
