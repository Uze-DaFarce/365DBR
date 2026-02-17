## 2025-05-15 - Font Loading Optimization
**Learning:** `Source Sans Pro` weight 600 was loaded but only used by `.logo-tagline`, `.check-icon`, and `.team-role`. These elements work equally well with `Inter` (which already has 600 loaded).
**Action:** Consolidate UI elements to use `Inter` and remove `Source Sans Pro` 600 to save ~20KB on initial load.
