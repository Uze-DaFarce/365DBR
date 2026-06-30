# Critical Constraints

## Code Stability
* **Do NOT modify `verseMap` structure in `index.html` without verifying all consumers.**
  - Specifically, the `loadDailyBread` function performs an optimization to flatten verse text arrays into single strings.
  - The `playVerse` function relies on this data structure.
  - Any changes to `loadDailyBread` (e.g., reverting to arrays or changing the structure) MUST be accompanied by updates to `playVerse` to handle the new format robustly.
  - **Always verify audio playback** after modifying text parsing logic.

## Verification
* If you modify `index.html`, you must run a visual verification test using Playwright (or manually) to ensure critical features like audio playback are not broken.
