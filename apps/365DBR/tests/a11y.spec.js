import { test, expect } from '@playwright/test';

test('verify a11y labels in index.html', async ({ page }) => {
  await page.goto('/data/0101/index.html');

  // Wait for the main body of content to load
  await page.waitForSelector("button[aria-label='Bookmark verse']", { timeout: 10000 });

  // Bookmark dialog
  await page.locator("button[aria-label='Bookmark verse']").first().click();

  await page.waitForSelector("button[aria-label='Close Bookmark Dialog']", { timeout: 10000 });
  await page.waitForSelector("button[aria-label='Select slot 1']", { timeout: 10000 });
  await page.waitForSelector("button[aria-label='Save bookmark']", { timeout: 10000 });

  // Verify Playback Toggle Label exists on index.html
  await page.waitForSelector("button[aria-label*='Playback']", { timeout: 10000 });

  await page.screenshot({ path: require('path').join(__dirname, '..', 'test-results', 'a11y_index.png') });
});

test('verify a11y labels in bible.html', async ({ page }) => {
  await page.goto('/bible.html');

  // Wait for the Browse Bible button. It appears behind the bible browse modal which opens by default in some configurations.
  // Close it first if it's open.
  try {
    await page.locator("button[aria-label='Close dialog']").click({ timeout: 2000 });
  } catch (e) {
    // Ignore if not present
  }

  await page.waitForSelector("button[aria-label='Browse Bible']", { timeout: 10000 });
  await page.locator("button[aria-label='Browse Bible']").click();
  await page.waitForSelector("button[aria-label='Select Old Testament']", { timeout: 10000 });

  await page.screenshot({ path: require('path').join(__dirname, '..', 'test-results', 'a11y_bible.png') });
});
