from playwright.sync_api import sync_playwright

def test_explanation_dismissal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use landscape view for mobile version
        context = browser.new_context(viewport={'width': 844, 'height': 390})
        page = context.new_page()

        try:
            page.goto('http://localhost:8000/apps/HeIsRisen/m/index.html')
            page.wait_for_timeout(2000)

            # Start EggZamRoom
            page.evaluate("() => { const scene = window.game.scene.getScene('MainMenu'); scene.scene.start('EggZamRoom'); }")
            page.wait_for_timeout(2000)

            page.screenshot(path='verification/explanation_visible.png')

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    test_explanation_dismissal()
