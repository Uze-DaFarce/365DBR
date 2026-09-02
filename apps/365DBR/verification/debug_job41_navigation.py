from playwright.sync_api import sync_playwright

URL = 'http://localhost:5500/bible.html?book=JOB&chapter=41&verse=1'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    page.goto(URL, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_selector('.verse-block', timeout=60000)
    page.wait_for_timeout(2500)
    ids = page.locator('.verse-block').evaluate_all("els => els.map(e => ({id:e.id, text:e.innerText.slice(0,180)}))")
    print('url:', page.url)
    print('blocks:', ids[:12])
    print('scrollY:', page.evaluate('window.scrollY'))
    assert page.url.endswith('book=JOB&chapter=41&verse=1'), page.url
    assert [item['id'] for item in ids[:9]] == [f'verse-JOB.41.{i}' for i in range(1, 10)]
    first_block = page.locator('[id="verse-JOB.41.1"]')
    assert 'LSB - LEGACY STANDARD BIBLE' in first_block.inner_text()
    assert 'Can you draw out Leviathan' in first_block.inner_text()
    browser.close()
