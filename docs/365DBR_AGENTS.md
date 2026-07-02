# 365DBR Critical Constraints (Moved to Root docs/ for Centralization)

**Note**: This was originally in apps/mtsinai/AGENTS.md but applies only to 365DBR. Moved here per documentation consolidation. Bible is primary truth; these are implementation constraints.

## Code Stability
* **Do NOT modify `verseMap` structure in `index.html` without verifying all consumers.**
  - Specifically, the `loadDailyBread` function performs an optimization to flatten verse text arrays into single strings.
  - The `playVerse` function relies on this data structure.
  - Any changes to `loadDailyBread` (e.g., reverting to arrays or changing the structure) MUST be accompanied by updates to `playVerse` to handle the new format robustly.
  - **Always verify audio playback** after modifying text parsing logic.

## Verification
* If you modify `index.html`, you must run a visual verification test using Playwright (or manually) to ensure critical features like audio playback are not broken.

## Relation to Current Focus
- These constraints support reliable 365DBR as foundation for S.I.
- See docs/365DBR/Data-Sources.md for data access (use production only).
- Agent prompts (in docs/Agents/) have additional relevant rules for testing, git, etc.
