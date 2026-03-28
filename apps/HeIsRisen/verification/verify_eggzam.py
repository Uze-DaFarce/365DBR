import sys
import os
import subprocess
import time

def ensure_dependencies():
    try:
        import playwright
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

ensure_dependencies()

from playwright.sync_api import sync_playwright

def start_server():
    subprocess.run(['pkill', '-f', 'http.server'])
    server = subprocess.Popen([sys.executable, "-m", "http.server", "8080"], cwd=os.path.join(os.getcwd(), "apps", "HeIsRisen"))
    time.sleep(2)
    return server

def test_eggzam():
    server = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("http://localhost:8080/")

            # Mute audio to avoid issues
            page.evaluate("""
                window.localStorage.setItem('musicVolume', '0.0');
                window.localStorage.setItem('ambientVolume', '0.0');
                window.localStorage.setItem('sfxVolume', '0.0');
            """)
            page.reload()

            print("Waiting for game canvas...")
            page.wait_for_selector("canvas", timeout=10000)

            # Start EggZamRoom directly
            print("Starting EggZamRoom...")
            page.evaluate("""
                const gameScene = window.game.scene.scenes[0];
                gameScene.registry.set('eggData', [
                    { eggId: '1', symbolData: { name: 'Cross', category: 'Christian', explanation: 'A Christian symbol.', scripture: 'John 3:16' } }
                ]);
                gameScene.registry.set('foundEggs', [
                    { eggId: '1', categorized: false, symbolData: { name: 'Cross', category: 'Christian', explanation: 'A Christian symbol.', scripture: 'John 3:16' } }
                ]);
                gameScene.scene.start('EggZamRoom');
            """)

            time.sleep(3) # Wait for room to load and ambient to settle

            print("Clicking Egg-cellent button to categorize the egg...")
            # Egg-cellent button coordinates on desktop UI
            page.mouse.click(760, 620)

            print("Waiting for video complete and popup to show (up to 8 seconds)...")
            time.sleep(8)

            out_dir = os.path.join(os.getcwd(), "apps", "HeIsRisen", "verification")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, "eggzam_popup.png")
            page.screenshot(path=out_path)
            print(f"Saved {out_path}")

            browser.close()
    finally:
        server.terminate()
        server.wait()

if __name__ == '__main__':
    test_eggzam()
