1. **Validate arrays loaded from `localStorage` in HeIsRisen desktop (`apps/HeIsRisen/main.js`)**
    - The `initializeGameData` function checks `Array.isArray(savedState.eggData)` and `Array.isArray(savedState.sections)`. However, it doesn't validate the inner contents of these arrays.
    - If `eggData` or `sections` contains `null` or corrupted string objects instead of valid objects, it causes runtime errors later.
    - `eggData` objects are expected to have `eggId` (Number), `section` (String). (Checked source code: `eggId` is a Number since it is initialized with `Array.from({ length: TOTAL_EGGS }, (_, i) => i + 1)`, and `section` is `section.name` which is a string).
    - `sections` objects are expected to have `name` (String).
    - `foundEggs` objects are pushed as `eggData` objects: `{ eggId, symbolData, categorized }`. So `eggId` is expected to be a Number.
    - `stampedSections` is an array of section name strings.
    - I will add strict validation before accepting the arrays from `localStorage`:
        ```javascript
        const isValidEggData = Array.isArray(savedState.eggData) && savedState.eggData.every(e => e && typeof e === 'object' && typeof e.eggId === 'number' && typeof e.section === 'string');
        const isValidSections = Array.isArray(savedState.sections) && savedState.sections.every(s => s && typeof s === 'object' && typeof s.name === 'string');
        const isValidFoundEggs = Array.isArray(savedState.foundEggs) && savedState.foundEggs.every(e => e && typeof e === 'object' && typeof e.eggId === 'number');
        const isValidStampedSections = Array.isArray(savedState.stampedSections) && savedState.stampedSections.every(s => typeof s === 'string');

        if (savedState && typeof savedState === 'object' && isValidEggData && isValidSections) {
        ...
            registry.set('foundEggs', isValidFoundEggs ? savedState.foundEggs : []);
            registry.set('stampedSections', isValidStampedSections ? savedState.stampedSections : []);
        ...
        ```

2. **Validate arrays loaded from `localStorage` in HeIsRisen mobile (`apps/HeIsRisen/m/main.js`)**
    - Apply the exact same inner validation for `eggData`, `sections`, `foundEggs`, and `stampedSections` in the mobile app.

3. **Verify the fix using the inner corruption test**
    - Run `python3 apps/HeIsRisen/tests/test_inner_corruption.py` to confirm the game no longer crashes and initializes a fresh state safely.

4. **Run other corruption and state tests to ensure regressions are not introduced**
    - Run `python3 apps/HeIsRisen/tests/test_state_corruption.py` to make sure standard corruption tests still pass.
    - Run `python3 apps/HeIsRisen/tests/test_full_game_loop.py` to make sure the game loop test passes.

5. **Complete pre commit steps**
    - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
