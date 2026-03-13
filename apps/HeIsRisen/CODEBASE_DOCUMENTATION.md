# Codebase Documentation

## Project Overview
"He Is Risen" is a Christian Easter Egg Hunt game built using the Phaser 3 framework. The game involves hunting for Easter eggs hidden across various map sections (based on Yellowstone National Park). Each egg contains a symbol which is either "Christian" or "Pagan" (Worldly). After collecting eggs, the player enters the "EggZam Room" to categorize the found symbols, learning about their meanings.

The project is split into two distinct versions:
- **Desktop Version**: Located in the root directory.
- **Mobile Version**: Located in the `m/` directory.
    ### Critical:
    - **IN PRODUCTION ENVIRONMENT**: They are both under the root so ./m/ is mobile and ./HeIsRisen/ is desktop!!
    - So like https://mt-sin.ai/ is root, and the games are at https://mt-sin.ai/HeIsRisen/ and https://mt-sin.ai/m/ there is also a webapp https://mt-sin.ai/365DBR/
    - **IN GITHUB**: the root (./) is "mt-sin.ai", "HeIsRisen" is for both games. m/ is a sub-directory (only in the repository) and "HeIsRisen" 
## File Structure

### Root Directory (Desktop)
- `index.html`: Entry point for the desktop game. Links `styles.css` and `main.js`.
- `main.js`: Contains the entire game logic for the desktop version, including all Phaser Scenes (`MainMenu`, `MapScene`, `SectionHunt`, `EggZamRoom`).
- `styles.css`: Basic styling for the game container.
- `package.json`: NPM configuration, primarily for `http-server` to run the game locally.
- `README.md`: Project description and status.
- `LICENCE.md`: License file.
- `assets/`: Contains all game assets (images, JSON data).

### `m/` Directory (Mobile)
- `m/index.html`: Entry point for the mobile game. Handles viewport meta tags for mobile devices.
- `m/main.js`: Game logic for the mobile version. Similar to the desktop version but includes mobile-specific optimizations (scaling, touch inputs, orientation locking).
- `m/styles.css`: Mobile-specific styling.
- `m/home.html`: A "Coming Soon" page (seems unused in the main flow).

### `assets/` Directory
- `assets/symbols.json`: The core data file containing the list of symbols.
    - **Structure**: Array of objects with `name`, `filename`, `category`, `scripture`, and `explanation`.
    - **Current State**: Contains **56** symbols.
- `assets/map/map_sections.json`: Defines the click zones on the main map.
    - **Structure**: Array of objects with `name`, `coords` (x, y, width, height), and `background` image filename.
- `assets/eggs/`: Images for the eggs. **Found 60 files** (likely `egg-1.png` to `egg-60.png`).
- `assets/symbols/`: Images for the symbols (split into `christian` and `pagan` subdirectories).
- `assets/map/`: Background images for the map and rooms.
- `assets/objects/`: UI elements and interactables.
- `assets/cursor/`: Custom cursor images.

## Architecture & Logic

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

### Data Discrepancies
- **Target Goal**: 60 Eggs (30 Christian, 30 Worldly).
- **`symbols.json`**: Contains **56** entries.
- **Desktop (`main.js`)**:
    - Hardcoded expectation of **57** eggs in some places (e.g., `scoreText`).
    - `MapScene` logic slices an array of 57 eggs.
    - Preloads `egg-1` to `egg-57`.
- **Mobile (`m/main.js`)**:
    - Defines `const TOTAL_EGGS = 60`.
    - Logic attempts to distribute 60 eggs.
    - Preloads `egg-1` to `egg-60` (which might fail if files don't exist).

### Critical Issues
1.  **Symbol Count Mismatch**: The game data (`symbols.json`) has 56 items, but the code expects 57 or 60 depending on the version. This causes `undefined` symbol data when accessing indices > 55.
2.  **Egg Image Count**: The code tries to load egg images up to 57 or 60. If `assets/eggs/` only contains images up to 57, the mobile version will throw 404 errors for `egg-58`, `egg-59`, `egg-60`.
3.  **Code Duplication**: Any fix applied to `main.js` must be manually ported to `m/main.js`, leading to drift (as seen in the different egg handling logic).
4.  **Scaling**: Mobile version has complex scaling logic to fit different aspect ratios, while desktop is more rigid.

## Recommendations for Next Steps

1.  **Standardize Data**:
    - Update `symbols.json` to have exactly 60 entries (30 Christian, 30 Pagan).
    - `assets/eggs/` already has 60 images, so this is good. Just need matching symbol data.
2.  **Refactor Code**:
    - Unify the logic where possible. The "Desktop" version could likely be made responsive to serve both platforms, or at least share the game configuration and data handling logic.
3.  **Fix Logic Bugs**:
    - Ensure loop bounds match the actual data length.
    - Add error handling for missing assets.
4.  **Gameplay Polish**:
    - The "Magnifying Glass" mechanic on mobile might need adjustment for better usability (currently implemented but noted as potentially problematic in comments).

# Codebase Documentation

## Project Structure
- `index.html`: Desktop entry point.
- `main.js`: Desktop game logic.
- `m/index.html`: Mobile entry point.
- `m/main.js`: Mobile game logic.

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
