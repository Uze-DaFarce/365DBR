import pytest
import os
import time
from test_helpers import start_server, assert_not_blank_screen

@pytest.fixture(scope="module")
def app_server():
    server = start_server(os.path.join(os.path.dirname(__file__), ".."))
    yield
    server.terminate()
    server.wait()


def test_eggzam_categorization(page, app_server):
    # Navigate to app
    page.goto("http://localhost:8080/index.html")

    # Wait for the game to load
    page.wait_for_function("() => window.game && window.game.scene.getScenes(true).length > 0")
    time.sleep(1)

    # Click to start the intro
    page.mouse.click(640, 360)
    time.sleep(1)

    # Skip right to EggZamRoom using global evaluate
    page.evaluate("window.game.scene.getScenes(true)[0].scene.start('EggZamRoom')")

    # Wait for EggZamRoom to be active
    page.wait_for_function("() => window.game.scene.getScene('EggZamRoom').scene.isActive()")
    time.sleep(2)

    # Inject a test egg into the registry so the room has something to categorize
    page.evaluate("""() => {
        const scene = window.game.scene.getScene('EggZamRoom');
        scene.registry.set('foundEggs', [
            {
                eggId: 1,
                symbolData: {
                    name: 'Test Christian Symbol',
                    category: 'Christian',
                    explanation: 'This is a test explanation for a Christian symbol.',
                    scripture: 'John 3:16',
                    filename: 'assets/map/new-map.png' // Use an existing asset so it loads
                },
                categorized: false
            }
        ]);
        scene.displayRandomEggInfo(0, 0, 1);
    }""")
    time.sleep(1)

    # Click the Egg-cellent button
    # stinkyBtn = 640 - 120 = 520, eggCellentBtn = 640 + 120 = 760
    # centerBottomY = 720 - 100 = 620
    page.mouse.click(760, 620)

    # Wait for animation and popup to appear
    time.sleep(4)

    # Save screenshot to test-results directory
    os.makedirs("apps/HeIsRisen/test-results", exist_ok=True)
    screenshot_path = "apps/HeIsRisen/test-results/eggzam_categorization_test.png"
    page.screenshot(path=screenshot_path)

    # Ensure screen is not blank/solid color
    with open(screenshot_path, 'rb') as f:
        assert_not_blank_screen(page, "EggZamRoom categorization screen is blank")
