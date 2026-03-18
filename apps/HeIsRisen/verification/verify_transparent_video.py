from playwright.sync_api import Page, expect, sync_playwright

def verify_feature(page: Page):
  page.goto("http://localhost:8080/HeIsRisen/index.html")
  page.wait_for_timeout(500)

  # Check that the intro video element is available
  expect(page.locator("canvas")).to_be_visible()
  page.wait_for_timeout(1000)

  # Tap anywhere to start intro sequence
  page.locator("canvas").click()
  page.wait_for_timeout(4000)

  # Start game from menu
  page.locator("canvas").click()
  page.wait_for_timeout(2000)

  # Wait for MapScene to load and map to show
  page.wait_for_timeout(2000)

  # Emulate clicking on a map section zone to play a level and show transparency
  # The zones are added dynamically, we'll try to click the first one roughly in the center-left
  page.mouse.click(600, 300)
  page.wait_for_timeout(3000)

  # Wait for SectionHunt to load
  page.wait_for_timeout(2000)

  # Use the evaluation to spoof collecting eggs
  page.evaluate("""() => {
    const registry = window.game.registry;
    const foundEggs = [];
    const sections = registry.get('sections');
    const firstSection = sections[0].name;
    const eggs = registry.get('eggData').filter(e => e.section === firstSection);

    eggs.forEach(egg => {
        foundEggs.push({
            eggId: egg.eggId,
            symbolData: egg.symbol,
            categorized: false
        });
        egg.collected = true;
    });
    registry.set('foundEggs', foundEggs);
    registry.set('eggData', registry.get('eggData'));
  }""")

  page.wait_for_timeout(2000)

  page.mouse.click(600, 300) # collect one to trigger checkLevelComplete

  page.wait_for_timeout(2000)

  # Go back to MapScene
  page.goto("http://localhost:8080/HeIsRisen/index.html")
  page.wait_for_timeout(500)

  page.screenshot(path="/home/jules/verification/verification.png")
  page.wait_for_timeout(1000)

if __name__ == "__main__":
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(record_video_dir="/home/jules/verification/video")
    page = context.new_page()
    try:
      verify_feature(page)
    finally:
      context.close()
      browser.close()
