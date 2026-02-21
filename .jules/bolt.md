## 2025-05-15 - Font Loading Optimization
**Learning:** `Source Sans Pro` weight 600 was loaded but only used by `.logo-tagline`, `.check-icon`, and `.team-role`. These elements work equally well with `Inter` (which already has 600 loaded).
**Action:** Consolidate UI elements to use `Inter` and remove `Source Sans Pro` 600 to save ~20KB on initial load.

## 2025-05-15 - Async Font Loading & Favicon Fix
**Learning:** Strict CSP prevents inline `onload` handlers for font loading. Using an external `async` script (`js/load-fonts.js`) allows earlier font activation than `defer`, improving FCP. Also, missing favicons caused 404s; replaced with `pics/logo.png`.
**Action:** Use external async scripts for critical resource activation under strict CSP. Verify asset existence to avoid 404s.
