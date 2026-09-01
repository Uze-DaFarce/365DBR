from playwright.sync_api import sync_playwright

PHRASE = "A Psalm of David"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto("http://localhost:5500/bible.html?book=PSA&chapter=3&verse=1", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector(".verse-block", timeout=60000)
        page.wait_for_timeout(1500)

        btn = page.locator('button[aria-label^="Word study"]').first
        btn.click(timeout=15000)
        page.wait_for_timeout(1000)

        panel = page.locator('[role="dialog"][aria-label^="Word study"]')
        text = panel.inner_text()
        print("word-study text snippet:", text[:500].replace("\n", " | "))
        print("title phrase in panel:", PHRASE in text)
        assert PHRASE not in text, "word study should not show Psalm title text"
        browser.close()


if __name__ == "__main__":
    main()
