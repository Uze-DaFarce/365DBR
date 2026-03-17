import { test, expect } from '@playwright/test';

test('test fullscreen crash', async ({ page }) => {
  page.on('console', msg => console.log(msg.text()));
  page.on('pageerror', error => console.log('ERROR:', error.message));

  await page.goto('http://127.0.0.1:8000/apps/HeIsRisen/');

  // wait for game to load
  await page.waitForTimeout(2000);

  // trigger click to start, this also starts fullscreen
  await page.mouse.click(500, 500);

  await page.waitForTimeout(5000);

});
