import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

def wait_for_scene(page, scene_key):
    # Polling until the specific scene is active
    page.wait_for_function(f"window.game && window.game.scene && window.game.scene.getScene('{scene_key}') && window.game.scene.getScene('{scene_key}').scene.isActive()", timeout=10000)

def test_desktop_a11y_sr_only(browser_context):
    context = browser_context.new_context(viewport={'width': 1280, 'height': 720})
    page = context.new_page()
    page.goto("http://localhost:8000/apps/HeIsRisen/index.html")

    # Wait for the MainMenu scene to be active to ensure game is loaded
    wait_for_scene(page, 'MainMenu')

    # Bypass audio context splash screen
    page.locator('canvas').first.click(force=True)
    page.wait_for_timeout(1500)

    # Verify the sr-only div exists
    sr_div = page.locator("#game-instructions")
    assert sr_div.count() == 1, "The #game-instructions div should exist"

    # Verify it has the correct text content
    text_content = sr_div.text_content()
    assert "Keyboard Controls" in text_content, "Div should contain 'Keyboard Controls'"
    assert "Press Escape to toggle settings menu" in text_content, "Instructions text is missing"

    # Verify it has the sr-only class
    assert "sr-only" in sr_div.get_attribute("class"), "Div should have 'sr-only' class"

    # Verify the canvas container has aria-describedby
    canvas_container = page.locator("#game")
    assert canvas_container.get_attribute("aria-describedby") == "game-instructions", "Canvas container is missing aria-describedby"

    # Save a visual screenshot for manual verification
    import os
    os.makedirs("verification", exist_ok=True)
    page.screenshot(path="verification/desktop_a11y_sr_only.png")

    context.close()

def test_mobile_a11y_sr_only(browser_context):
    # Landscape orientation for mobile game
    context = browser_context.new_context(viewport={'width': 844, 'height': 390})
    page = context.new_page()
    page.goto("http://localhost:8000/apps/HeIsRisen/m/index.html")

    # Wait for the MainMenu scene to be active
    wait_for_scene(page, 'MainMenu')

    # Bypass audio context splash screen
    page.locator('canvas').first.click(force=True)
    page.wait_for_timeout(1500)

    # Verify the sr-only div exists
    sr_div = page.locator("#game-instructions")
    assert sr_div.count() == 1, "The #game-instructions div should exist in mobile"

    # Verify it has the correct text content
    text_content = sr_div.text_content()
    assert "Keyboard Controls" in text_content, "Div should contain 'Keyboard Controls' in mobile"

    # Verify it has the sr-only class
    assert "sr-only" in sr_div.get_attribute("class"), "Div should have 'sr-only' class in mobile"

    # Verify the canvas container has aria-describedby
    canvas_container = page.locator("#game-container")
    assert canvas_container.get_attribute("aria-describedby") == "game-instructions", "Mobile canvas container is missing aria-describedby"

    # Save a visual screenshot for manual verification
    page.screenshot(path="verification/mobile_a11y_sr_only.png")

    context.close()
