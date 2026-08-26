"""One-off check: Psalm 17 heading visible once on daily reader + bible browser."""
from playwright.sync_api import sync_playwright

PHRASE = "A Prayer of David"


def inspect(page, label):
    found = page.get_by_text(PHRASE, exact=False)
    count = found.count()
    print(f"{label} phrase count: {count}")
    if count:
        found.first.scroll_into_view_if_needed()
        page.wait_for_timeout(400)
    blocks = page.locator(".verse-block").filter(has_text=PHRASE)
    print(f"{label} verse-blocks with phrase: {blocks.count()}")
    headings = page.locator("span", has_text="Heading")
    print(f"{label} Heading labels: {headings.count()}")
    if blocks.count():
        sample = blocks.first.inner_text().replace("\n", " | ")[:600]
        print(f"{label} sample: {sample}")
        # Focal slot should contain Heading; middle should not repeat the phrase
        # after display-strip. Count phrase occurrences inside the first matching block.
        inner = blocks.first.inner_text()
        print(f"{label} phrase occurrences in first block: {inner.count(PHRASE)}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_extra_http_headers({"Cache-Control": "no-cache"})

        page.goto(
            "http://127.0.0.1:5500/index.html?startDate=0123",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector(".verse-block", timeout=60000)
        page.wait_for_timeout(1500)
        inspect(page, "index")
        page.screenshot(
            path=r"D:\Users\uzeda\Mt. Sinai LLC\monorepo\apps\365DBR\verification\title_index_0123.png"
        )

        page.goto(
            "http://127.0.0.1:5500/bible.html?book=PSA&chapter=17",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(2000)
        closer = page.locator("button[aria-label='Close dialog']")
        if closer.count():
            try:
                closer.first.click(timeout=2000)
            except Exception:
                pass
        page.wait_for_selector(".verse-block", timeout=60000)
        page.wait_for_timeout(1000)
        inspect(page, "bible")
        page.screenshot(
            path=r"D:\Users\uzeda\Mt. Sinai LLC\monorepo\apps\365DBR\verification\title_bible_psa17.png"
        )

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(
            "http://127.0.0.1:5500/index.html?startDate=0123",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        mobile.wait_for_selector(".verse-block", timeout=60000)
        mobile.wait_for_timeout(1500)
        mobile.get_by_text(PHRASE, exact=False).first.scroll_into_view_if_needed()
        mobile.wait_for_timeout(400)
        print("mobile Heading labels:", mobile.locator("span", has_text="Heading").count())
        mobile.screenshot(
            path=r"D:\Users\uzeda\Mt. Sinai LLC\monorepo\apps\365DBR\verification\title_index_0123_mobile.png"
        )
        mobile.close()
        browser.close()
    print("DONE")


if __name__ == "__main__":
    main()
