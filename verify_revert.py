from playwright.sync_api import sync_playwright

def verify_logos_revert():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Scenario 1: Desktop - index.html
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto("http://localhost:8000/index.html")
        page.wait_for_load_state("networkidle")

        # Check Alt Text
        logo_img = page.locator(".logo-icon").first
        alt_text = logo_img.get_attribute("alt")
        print(f"Index Logo Alt: '{alt_text}'")
        assert alt_text == "", f"Expected '', got '{alt_text}' (Logo is decorative)"

        logo_img.screenshot(path="revert_index_desktop.png")

        # Scenario 2: Desktop - 404.html
        page_404 = browser.new_page(viewport={'width': 1280, 'height': 800})
        page_404.goto("http://localhost:8000/404.html")
        page_404.wait_for_load_state("networkidle")

        logo_img_404 = page_404.locator(".logo-icon").first
        alt_text_404 = logo_img_404.get_attribute("alt")
        print(f"404 Logo Alt: '{alt_text_404}'")
        assert alt_text_404 == "", f"Expected '', got '{alt_text_404}' (Logo is decorative)"

        logo_img_404.screenshot(path="revert_404_desktop.png")

        browser.close()

if __name__ == "__main__":
    verify_logos_revert()
