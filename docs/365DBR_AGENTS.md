# 365DBR Critical Constraints (Moved to Root docs/ for Centralization)

**Note**: This was originally in apps/mtsinai/AGENTS.md but applies only to 365DBR. Moved here per documentation consolidation. Bible is primary truth; these are implementation constraints.

## Code Stability
* **Do NOT modify `verseMap` structure in `index.html` without verifying all consumers.**
  - Specifically, the `loadDailyBread` function performs an optimization to flatten verse text arrays into single strings.
  - The `playVerse` function relies on this data structure.
  - Any changes to `loadDailyBread` (e.g., reverting to arrays or changing the structure) MUST be accompanied by updates to `playVerse` to handle the new format robustly.
  - **Always verify audio playback** after modifying text parsing logic.

## Optional Strong's / word study (Phase 4)
* **Enabled when** local query API `/health` succeeds (feature-detect). No opt-in flag. Hide control if API down.
* **Current UX**: original-first Word study (correct for data we have: original tokens + Strong's).
* **Desired later (free/open only — owner has no budget for paid RI data)**: hover English word → original + Strong's for *that* word. Requires honest EN↔token alignment from open sources; do not invent maps. See `docs/365DBR/Word-Study-and-Alignment.md`.
* **Static JSON remains primary**. Do **not** route `loadDailyBread` / `verseMap` / `playVerse` through the DB API without Option B + audio verification.

## Verification
* If you modify `index.html`, you must run a visual verification test using Playwright (or manually) to ensure critical features like audio playback are not broken.

## Relation to Current Focus
- These constraints support reliable 365DBR as foundation for S.I.
- See docs/365DBR/Data-Sources.md for data access (use production only).
- Agent prompts (in docs/Agents/) have additional relevant rules for testing, git, etc.
