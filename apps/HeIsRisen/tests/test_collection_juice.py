import os
import sys
import glob
from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # DESKTOP
        print("Testing Desktop Version")
        context_desktop = browser.new_context(viewport={'width': 1280, 'height': 720})
        page_desktop = context_desktop.new_page()
        page_desktop.goto("http://127.0.0.1:8080/index.html")

        # Wait for canvas to be fully loaded
        page_desktop.locator("canvas").wait_for()
        page_desktop.wait_for_timeout(3000)

        # Start the game
        page_desktop.evaluate("""() => {
            const scene = window.game.scene.getScene('MainMenu');
            scene.scene.start('MapScene');
        }""")
        page_desktop.wait_for_timeout(2000)

        # Start SectionHunt
        page_desktop.evaluate("""() => {
            const scene = window.game.scene.getScene('MapScene');
            const sections = scene.registry.get('sections');
            if (sections && sections.length > 0) {
                scene.scene.start('SectionHunt', { sectionName: sections[0].name, mapKey: sections[0].id });
            } else {
                scene.scene.start('SectionHunt', { sectionName: 'Yellowstone Lake', mapKey: 'yellowstone-lake' });
            }
        }""")
        page_desktop.wait_for_timeout(2000)

        # Collect an egg
        page_desktop.evaluate("""() => {
            const scene = window.game.scene.getScene('SectionHunt');
            if (!scene || !scene.eggs) return;

            if (scene.eggs && scene.eggs.children.entries.length > 0) {
                const egg = scene.eggs.children.entries[0];
                scene.collectEgg(egg);
            }
        }""")

        page_desktop.wait_for_timeout(300)
        os.makedirs("test_screenshots", exist_ok=True)
        page_desktop.screenshot(path="test_screenshots/collection_juice_desktop.png")
        page_desktop.wait_for_timeout(1000)
        context_desktop.close()

        # MOBILE
        print("Testing Mobile Version")
        context_mobile = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
        page_mobile = context_mobile.new_page()
        page_mobile.goto("http://127.0.0.1:8080/m/index.html")

        page_mobile.locator("canvas").wait_for()
        page_mobile.wait_for_timeout(3000)

        page_mobile.evaluate("""() => {
            const scene = window.game.scene.getScene('MainMenu');
            scene.scene.start('MapScene');
        }""")
        page_mobile.wait_for_timeout(2000)

        page_mobile.evaluate("""() => {
            const scene = window.game.scene.getScene('MapScene');
            const sections = scene.registry.get('sections');
            if (sections && sections.length > 0) {
                scene.scene.start('SectionHunt', { sectionName: sections[0].name, mapKey: sections[0].id });
            } else {
                scene.scene.start('SectionHunt', { sectionName: 'Yellowstone Lake', mapKey: 'yellowstone-lake' });
            }
        }""")
        page_mobile.wait_for_timeout(2000)

        page_mobile.evaluate("""() => {
            const scene = window.game.scene.getScene('SectionHunt');
            if (!scene || !scene.eggs) return;

            if (scene.eggs && scene.eggs.children.entries.length > 0) {
                const egg = scene.eggs.children.entries[0];
                scene.collectEgg(egg);
            }
        }""")

        page_mobile.wait_for_timeout(300)
        page_mobile.screenshot(path="test_screenshots/collection_juice_mobile.png")
        page_mobile.wait_for_timeout(1000)
        context_mobile.close()

        browser.close()

if __name__ == "__main__":
    run_test()
