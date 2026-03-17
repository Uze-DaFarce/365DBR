import { test, expect, devices } from '@playwright/test';

test.use({
  ...devices['Pixel 5'],
  viewport: { width: 844, height: 390 }, // Landscape
  isMobile: true,
  hasTouch: true,
});

test('test mobile play crash', async ({ page }) => {
  page.on('console', msg => console.log(msg.text()));
  page.on('pageerror', error => console.log('ERROR:', error.message));

  await page.goto('http://127.0.0.1:8000/apps/HeIsRisen/m/');

  // wait for game to load
  await page.waitForTimeout(2000);

  // trigger click to start, this also starts fullscreen on mobile
  await page.mouse.click(422, 195);

  await page.waitForTimeout(2000);

  // click play
  await page.mouse.click(422, 312); // Center of play button

  await page.waitForTimeout(4000);
});
