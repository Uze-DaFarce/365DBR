# Gemini Code Assist - Project Analysis

This document provides a summary of the current state, purpose, and key features of the projects within this monorepo, based on an analysis of the provided source code and all relevant markdown documentation.

## HeIsRisen (Phaser Game)

### Purpose
An Easter-themed hidden object game built with Phaser 3. It has distinct, intentionally separate versions for mobile (`m/main.js`) and desktop (`main.js`). The core gameplay involves finding hidden eggs, examining them in the "EggZamRoom", and categorizing the religious symbols found on them.

### Key Improvements & Current State
*   **Performance:** Asset loading has been heavily optimized. All static game assets (eggs, symbols, map backgrounds) are now preloaded in the initial `MainMenu` scene. This was a critical fix to prevent stuttering and re-loading when players enter new game areas.
*   **User Experience (UX):** A major focus has been on creating consistent and clear interaction feedback.
    *   All interactive buttons use a standardized `addButtonInteraction` helper for consistent hover and press animations.
    *   Interactive zones on the map and in the `EggZamRoom` minigame now have visual hover outlines for better discoverability.
*   **Responsiveness:** The UI and HUD are designed to be responsive. The code contains logic to adjust font sizes and element positions for both mobile and desktop views, preventing visual overlap. The game itself uses a `RESIZE` scaling mode to fill the browser window.
*   **Accessibility (A11y):**
    *   Core keyboard navigation is supported, including using `ESC` to close modals and `Enter`/`Space` on final calls-to-action like "Play Again".
    *   The game canvas is now auto-focused on load, making it easier for screen readers to discover and announce the game's presence.

### Testing Notes
*   Playwright is used for automated testing.
*   A known issue with mobile emulation in Playwright requires manually swapping the viewport `width` and `height` to correctly simulate landscape mode.
*   Input handling for draggable UI elements (like volume sliders) requires a specific Phaser 3 pattern: `scene.input.setDraggable(container)`.

### Architectural Notes & Data Integrity
*   **Intentional Code Separation**: The desktop (`main.js`) and mobile (`m/main.js`) versions are maintained as separate files. This is a deliberate architectural choice to provide distinct user experiences for mouse vs. touch inputs, especially in the `SectionHunt` scene's magnifying glass mechanic. **These files should not be merged.**
*   **Data Standardization**: Both the desktop and mobile versions are standardized to use a total of **60 eggs**. The `TOTAL_EGGS` constant is set to `60` in both `main.js` and `m/main.js`.
*   **Asset Dependency**: The game expects `assets/symbols.json` to contain exactly 60 symbol objects. The `MainMenu` scene includes a check that will log an error to the console if the number of symbols does not match `TOTAL_EGGS`.

---

## 365DBR (Daily Bible Reader)

### Purpose
A single-page web application for daily Bible readings. It is built with React (loaded via `esm.sh`, without a traditional build step) and is supported by a suite of Python scripts for fetching data from the `api.bible` service (`fetch_readings.py`) and compiling the app into a static site (`compile_site.py`).

### Key Improvements & Current State
*   **Performance:** The React front-end has undergone significant performance tuning.
    *   Extensive use of `React.memo` and `useMemo` prevents unnecessary re-renders during high-frequency events like scrolling.
    *   The "App Shell" pattern is used, keeping the header and footer static during content loads to prevent disorienting layout shifts.
    *   The Largest Contentful Paint (LCP) image is prioritized with `fetchpriority="high"`.
*   **Security:** The Python data-fetching scripts have been hardened.
    *   The `validate_safe_path` function now uses a strict regex to prevent path traversal and other injection attacks.
    *   All dynamic parameters in API calls are now properly URL-encoded.
*   **Accessibility (A11y):** This has been a major area of focus, resulting in a highly accessible experience.
    *   **Navigation:** A "Skip to Content" link is present, and the active navigation link is always visible and marked with `aria-current`.
    *   **Focus Management:** All interactive elements have clear, context-aware focus rings. Modals and overlays properly trap focus and can be dismissed with the `Escape` key.
    *   **Assistive Tech:** All decorative icons use `aria-hidden="true"` to reduce auditory clutter for screen readers. Keyboard shortcuts are explicitly declared with `aria-keyshortcuts`.
    *   **Motion:** Animations respect user preferences via `@media (prefers-reduced-motion: reduce)`.
*   **User Experience (UX):**
    *   **Keyboard-First:** Keyboard shortcuts (Arrow keys, Space, etc.) are unified across all application modes for a consistent experience.
    *   **Context & Transparency:** The UI provides an estimated reading time to set expectations. When collapsing large sections, the view smoothly scrolls to maintain the user's context.
    *   **Print Optimization:** A dedicated print stylesheet ensures a clean, professional, and ink-friendly output when printing to paper or PDF.

### Status of Markdown Journals
*   **`README.md`**: The main entry point for the repository. It provides the mission statement, a list of all applications, and detailed setup/usage instructions for the `365DBR` application, including environment setup and command-line usage.

*   **`palette.md`**: A development journal focused on **user experience and accessibility**. It documents learnings and actions related to UI/UX design, keyboard navigation, focus management, ARIA implementation, and responsive design for the web applications.

*   **`bolt.md`**: A development journal focused on **performance and optimization**. It logs critical learnings about asset loading (images, fonts), static site optimization, React performance tuning (`memo`, `useMemo`), and fixing game-specific performance bottlenecks in Phaser.

*   **`sentinel.md`**: A security-focused journal that tracks **vulnerabilities and hardening measures**. It details the implementation of security headers (CSP, Permissions-Policy), server configuration hardening (`.htaccess`, `robots.txt`), and prevention of common web vulnerabilities like script injection and information leakage.