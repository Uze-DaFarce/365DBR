"""Verify focal-only bookmark, per-translation copy, and OT-only Word Study."""
import json
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000/apps/365DBR"
OUT = r"D:\Users\uzeda\Mt. Sinai LLC\monorepo\apps\365DBR\verification"
AA = "button[aria-label=\"Word study — original words and Strong's numbers\"]"
BM = "button[aria-label='Bookmark verse']"
COPY = "button[aria-label='Copy verse']"
SEED_BOOKMARKS = {
    "1": {
        "vid": "2KI.1.1",
        "color": {
            "bg": "bg-red-500",
            "hover": "hover:bg-red-600",
            "ring": "focus:ring-red-500",
            "name": "Red",
        },
    }
}


def seed(page):
    page.add_init_script(
        f"localStorage.setItem('bible_browser_bookmarks', {json.dumps(json.dumps(SEED_BOOKMARKS))});"
    )


def wait_verses(page, prefix, timeout=45000):
    page.wait_for_selector(f"[id^='verse-{prefix}']", timeout=timeout)


def counts_in(page, verse_id):
    block = page.locator(f'[id="verse-{verse_id}"]')
    block.wait_for(timeout=20000)
    return {
        "copy": block.locator(COPY).count(),
        "bookmark": block.locator(BM).count(),
        "aa": block.locator(AA).count(),
    }


def wait_aa_or_timeout(page, timeout_ms=8000):
    try:
        page.wait_for_selector(AA, timeout=timeout_ms)
        return True
    except Exception:
        return False


def run():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))

        seed(page)

        # --- OT bible: 2 Kings 1:1 should have copy x3, bookmark x1, Aa x1 ---
        page.goto(f"{BASE}/bible.html?book=2KI&chapter=1&verse=1", wait_until="domcontentloaded")
        wait_verses(page, "2KI")
        page.wait_for_selector(BM, timeout=20000)
        wait_aa_or_timeout(page, 8000)
        ot = counts_in(page, "2KI.1.1")
        print("bible 2KI.1.1", ot)
        page.screenshot(path=f"{OUT}/gate_bible_2ki1.png")
        if ot["copy"] != 3:
            raise SystemExit(f"FAIL: 2KI.1.1 expected 3 copy buttons, got {ot['copy']}")
        if ot["bookmark"] != 1:
            raise SystemExit(f"FAIL: 2KI.1.1 expected 1 bookmark (focal only), got {ot['bookmark']}")
        if ot["aa"] != 1:
            raise SystemExit(f"FAIL: 2KI.1.1 expected Aa (OT Strong's), got {ot['aa']}")

        # --- NT bible: Matthew 1:1 should have copy x3, bookmark x1, no Aa ---
        page.goto(f"{BASE}/bible.html?book=MAT&chapter=1&verse=1", wait_until="domcontentloaded")
        wait_verses(page, "MAT")
        page.wait_for_selector(BM, timeout=20000)
        page.wait_for_timeout(2500)  # allow Word Study probe to finish
        nt = counts_in(page, "MAT.1.1")
        print("bible MAT.1.1", nt)
        page.screenshot(path=f"{OUT}/gate_bible_mat1.png")
        if nt["copy"] != 3:
            raise SystemExit(f"FAIL: MAT.1.1 expected 3 copy buttons, got {nt['copy']}")
        if nt["bookmark"] != 1:
            raise SystemExit(f"FAIL: MAT.1.1 expected 1 bookmark (focal only), got {nt['bookmark']}")
        if nt["aa"] != 0:
            raise SystemExit(f"FAIL: MAT.1.1 expected no Aa (no NT Strong's), got {nt['aa']}")

        # --- Daily bread 0913: Job (OT) has Aa, 1 Cor (NT) does not ---
        page.goto(f"{BASE}/index.html?startDate=0913", wait_until="domcontentloaded")
        wait_verses(page, "JOB")
        page.wait_for_selector(BM, timeout=20000)
        wait_aa_or_timeout(page, 8000)
        page.wait_for_timeout(1500)
        job = counts_in(page, "JOB.41.1")
        print("index JOB.41.1", job)
        page.screenshot(path=f"{OUT}/gate_index_job41.png")
        if job["copy"] != 3:
            raise SystemExit(f"FAIL: JOB.41.1 expected 3 copy buttons, got {job['copy']}")
        if job["bookmark"] != 1:
            raise SystemExit(f"FAIL: JOB.41.1 expected 1 bookmark, got {job['bookmark']}")
        if job["aa"] != 1:
            raise SystemExit(f"FAIL: JOB.41.1 expected Aa, got {job['aa']}")

        page.locator('[id="verse-1CO.15.20"]').scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        co = counts_in(page, "1CO.15.20")
        print("index 1CO.15.20", co)
        page.screenshot(path=f"{OUT}/gate_index_1co15.png")
        if co["copy"] != 3:
            raise SystemExit(f"FAIL: 1CO.15.20 expected 3 copy buttons, got {co['copy']}")
        if co["bookmark"] != 1:
            raise SystemExit(f"FAIL: 1CO.15.20 expected 1 bookmark, got {co['bookmark']}")
        if co["aa"] != 0:
            raise SystemExit(f"FAIL: 1CO.15.20 expected no Aa, got {co['aa']}")

        browser.close()

    print("js/page errors:", errors[:8])
    print("OK")


if __name__ == "__main__":
    run()
