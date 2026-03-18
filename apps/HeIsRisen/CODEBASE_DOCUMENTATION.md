# HeIsRisen - Codebase Documentation

This document outlines the architecture, data dependencies, and key mechanics of the `HeIsRisen` Phaser 3 game.

## Project Overview

The project is split into two distinct versions:
- **Desktop Version**: Located in the root directory.
- **Mobile Version**: Located in the `m/` directory.
    ### Critical:
    - **IN PRODUCTION ENVIRONMENT**: They are both under the root so ./m/ is mobile and ./HeIsRisen/ is desktop!!
    - So like https://mt-sin.ai/ is root, and the games are at https://mt-sin.ai/HeIsRisen/ and https://mt-sin.ai/m/ there is also a webapp https://mt-sin.ai/365DBR/

The core gameplay loop involves finding hidden eggs on various maps, collecting them, and then categorizing the religious symbols found on them in a minigame.

## Architectural Constraints

### Intentional Code Separation

The desktop and mobile versions of the game are maintained in separate, parallel files (`main.js` and `m/main.js`). This is a **deliberate architectural decision** and these files should not be merged.
The primary reason for this separation is to provide a tailored User Experience (UX) for different input methods:
*   **Desktop (`main.js`):** The `SectionHunt` scene features a magnifying glass mechanic where the zoomed-in view is centered directly on the mouse cursor. This provides a direct and intuitive experience for mouse users.
*   **Mobile (`m/main.js`):** The `SectionHunt` scene uses a magnifying glass that is visually offset from the user's touch point. This allows the user to see what is under the "lens" without their finger obscuring the view, which is critical for touch-based gameplay.
This difference in the core hunting mechanic necessitates separate `update` loops and input handling logic in the `SectionHunt` scene.

### Game Flow
1. **MainMenu**:
    - Loads initial assets.
    - Displays title and "Start" interaction.
    - Loads `symbols.json`.
2. **MapScene**:
    - Displays the main map of Yellowstone.
    - Interactive zones correspond to entries in `map_sections.json`.
    - Clicking a zone transitions to `SectionHunt`.
    - Also allows access to `EggZamRoom`.
3. **SectionHunt**:
    - Displays a specific map section.
    - Eggs are hidden in the scene.
    - **Desktop**: Hardcoded specific eggs per section (logic in `MapScene` creates the distribution).
    - **Mobile**: Randomly distributes eggs based on `TOTAL_EGGS` constant.
    - Mechanics:
        - "Magnifying glass" effect (using a mask) reveals eggs.
        - Clicking an egg collects it and adds it to the registry.
4. **EggZamRoom**:
    - The sorting minigame.
    - Displays a collected egg and its symbol.
    - Player sorts the egg into "Christian" or "Pagan" bottles.
    - Provides feedback and scripture/explanation.



## Data & Asset Integrity

## Recommendations for Next Steps

### Egg and Symbol Count
*   **Standardized Total:** Both the desktop and mobile versions are standardized to use a total of **60 eggs**. The global constant `TOTAL_EGGS` is set to `60` at the top of both `main.js` and `m/main.js`.
*   **Symbol JSON Dependency:** The game's `MainMenu` scene loads symbol data from `assets/symbols.json`. It explicitly checks that the number of symbol objects in this file matches the `TOTAL_EGGS` count (60).
*   **Error Condition:** If `symbols.json` contains a number of symbols other than 60, the game will log an error to the console during the loading sequence. This mismatch can cause runtime errors or undefined behavior later in the game, particularly when trying to access symbol data for an egg that has no corresponding entry.

### Asset Preloading

To ensure smooth gameplay and prevent stuttering, all critical game assets are preloaded in the `MainMenu` scene. This includes:
*   All 60 egg images (`egg-1.png` through `egg-60.png`).
*   All symbol images (dynamically loaded based on the contents of `symbols.json`).
*   All map section backgrounds and video assets.
*   All UI components and audio files.

## Platform Differences (Crucial)
The gameplay mechanics for `SectionHunt` (the magnifying glass search) are **intentionally different** between Desktop and Mobile to account for input methods (Mouse vs Touch) and screen size.

### Desktop (`main.js`)
- **Input:** Mouse.
- **Magnifying Glass:**
  - Uses a `RenderTexture` with an internal Camera (`zoomedView.camera`).
  - Masking is applied via `createGeometryMask` on a Graphics object.
  - The lens is smaller (Radius: 50, Diameter: 100).
  - The zoom level is moderate (2x).
  - Interaction relies on mouse hover and precise clicking.

### Mobile (`m/main.js`)
- **Input:** Touch.
- **Magnifying Glass:**
  - Uses manual coordinate calculation (`(x - scrollX) * zoom`) because `RenderTexture` cameras behave differently on some mobile contexts or for performance reasons.
  - **Scale:** All gameplay elements (Cursor, Eggs, Lens) are scaled up (approx 2x) to be touch-friendly.
  - **Lens:** Significantly larger to allow seeing under the finger.
  - **Egg Spawning:** Constrained to visible bounds (50px margin) to prevent eggs from being unclickable at the edges.
  - **Helpers:** Includes an idle help prompt ("Eggs left here: X") to assist users on small screens.

**DO NOT MERGE THESE LOGICS.**
Future optimizations must respect these differences. "Fixing" the desktop version to look like the mobile version (or vice-versa) without explicit instruction is a regression.
