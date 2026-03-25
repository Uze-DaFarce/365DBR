import pytest
from playwright.sync_api import Page, expect

def trigger_egg_collection(page: Page):
    # Instead of clicking blindly, we inject a script to find an active egg and call collectEgg directly
    # Because window.game is not global, we have to find the Phaser canvas and trigger a custom event
    # or rely on the scene's internal state. But Playwright can't easily access scoped variables.
    # The simplest way is to overwrite the global Date or similar temporarily, but we can also
    # mock the collectEgg function or just trust the previous integration.
    # Actually, we can dispatch a click directly onto the canvas in a grid until we hit an egg,
    # and then assert vibrate was called.
    pass

def test_haptic_feedback_desktop(page: Page):
    """Verifies haptic vibration is called on desktop"""
    page.goto("http://localhost:8000/")
    page.evaluate('''() => {
        window.vibratedAmount = 0;
        navigator.vibrate = function(pattern) {
            window.vibratedAmount += (typeof pattern === 'number' ? pattern : pattern[0]);
            return true;
        };
    }''')
    page.wait_for_selector("canvas", state="visible")
    page.wait_for_timeout(2000)

    # We will dispatch clicks across the screen until vibratedAmount > 0
    canvas_box = page.locator("canvas").bounding_box()
    if canvas_box:
        for x in range(int(canvas_box['width'] // 8), int(canvas_box['width']), int(canvas_box['width'] // 8)):
            for y in range(int(canvas_box['height'] // 8), int(canvas_box['height']), int(canvas_box['height'] // 8)):
                page.mouse.click(canvas_box['x'] + x, canvas_box['y'] + y)
                page.wait_for_timeout(50)
                vibrated = page.evaluate("() => window.vibratedAmount")
                if vibrated > 0:
                    break
            if page.evaluate("() => window.vibratedAmount") > 0:
                break

    vibrated = page.evaluate("() => window.vibratedAmount")
    assert vibrated > 0, "Haptic feedback was not triggered on desktop (could not hit an egg or vibrate missing)"

def test_haptic_feedback_mobile(page: Page, browser):
    """Verifies haptic vibration is called on mobile"""
    context = browser.new_context(is_mobile=True, has_touch=True, viewport={'width': 844, 'height': 390})
    m_page = context.new_page()
    m_page.goto("http://localhost:8000/m/")

    m_page.evaluate('''() => {
        window.vibratedAmount = 0;
        navigator.vibrate = function(pattern) {
            window.vibratedAmount += (typeof pattern === 'number' ? pattern : pattern[0]);
            return true;
        };
    }''')
    m_page.wait_for_selector("canvas", state="visible")
    m_page.wait_for_timeout(2000)

    canvas_box = m_page.locator("canvas").bounding_box()
    if canvas_box:
        for x in range(int(canvas_box['width'] // 8), int(canvas_box['width']), int(canvas_box['width'] // 8)):
            for y in range(int(canvas_box['height'] // 8), int(canvas_box['height']), int(canvas_box['height'] // 8)):
                m_page.mouse.click(canvas_box['x'] + x, canvas_box['y'] + y)
                m_page.wait_for_timeout(50)
                vibrated = m_page.evaluate("() => window.vibratedAmount")
                if vibrated > 0:
                    break
            if m_page.evaluate("() => window.vibratedAmount") > 0:
                break

    vibrated = m_page.evaluate("() => window.vibratedAmount")
    assert vibrated > 0, "Haptic feedback was not triggered on mobile (could not hit an egg or vibrate missing)"
    context.close()
