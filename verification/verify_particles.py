from playwright.sync_api import sync_playwright
import time

def test_particles():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        page.goto("http://localhost:8000/apps/HeIsRisen/index.html")

        # Wait for the MainMenu scene to be active
        page.wait_for_function("window.game && window.game.scene && window.game.scene.getScene('MainMenu') && window.game.scene.getScene('MainMenu').scene.isActive()", timeout=10000)

        # Bypass audio context splash screen
        page.locator('canvas').first.click(force=True)
        page.wait_for_timeout(1500)

        # Inject fake data into the registry to test EggZamRoom immediately
        page.evaluate("""
            window.game.registry.set('foundEggs', [{
                eggId: 1,
                symbolData: {
                    name: "Cross",
                    category: "Christian",
                    filename: "assets/symbols/christian/cross.png",
                    explanation: "Test explanation",
                    scripture: "John 3:16"
                },
                categorized: false
            }]);
        """)

        # Force transition to EggZamRoom directly via Phaser API
        page.evaluate("window.game.scene.getScene('MainMenu').scene.start('EggZamRoom')")

        # Wait for EggZamRoom to be active
        page.wait_for_function("window.game.scene.getScene('EggZamRoom') && window.game.scene.getScene('EggZamRoom').scene.isActive()", timeout=10000)
        page.wait_for_timeout(1000)

        # Click the left bottle zone to trigger playGoodEggAnimation (Christian)
        # Center of Left Bottle Zone = 540, 540
        page.mouse.move(540, 540)
        page.mouse.down()
        page.mouse.up()

        # The animation takes 800ms to lift the egg, then sparks/halo appear.
        # Wait until we are right in the middle of the sparkle particle emission
        page.wait_for_timeout(1000)

        page.screenshot(path="verification/eggjam_particle_good.png")

        browser.close()

if __name__ == "__main__":
    test_particles()
