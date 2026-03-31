import os
import sys
import glob
from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        page.goto("http://127.0.0.1:8080/index.html")

        # Wait for canvas to be fully loaded
        canvas = page.locator("canvas")
        canvas.wait_for()
        page.wait_for_timeout(3000)

        # Start the game
        page.evaluate("""() => {
            const scene = window.game.scene.getScene('MainMenu');
            scene.scene.start('MapScene');
        }""")
        page.wait_for_timeout(2000)

        # Start SectionHunt
        page.evaluate("""() => {
            const scene = window.game.scene.getScene('MapScene');
            const sections = scene.registry.get('sections');
            if (sections && sections.length > 0) {
                scene.scene.start('SectionHunt', { sectionName: sections[0].name, mapKey: sections[0].id });
            } else {
                scene.scene.start('SectionHunt', { sectionName: 'Yellowstone Lake', mapKey: 'yellowstone-lake' });
            }
        }""")
        page.wait_for_timeout(2000)

        # Collect an egg
        page.evaluate("""() => {
            const scene = window.game.scene.getScene('SectionHunt');
            if (!scene || !scene.eggs) return;

            if (scene.eggs && scene.eggs.children.entries.length > 0) {
                const egg = scene.eggs.children.entries[0];
                scene.collectEgg(egg);
            }
        }""")

        # Take screenshot during animation
        page.wait_for_timeout(300)
        os.makedirs("test_screenshots", exist_ok=True)
        page.screenshot(path="test_screenshots/collection_juice.png")
        page.wait_for_timeout(1000)

        context.close()
        browser.close()

if __name__ == "__main__":
    run_test()
