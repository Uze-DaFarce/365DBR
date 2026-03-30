# BOLT'S JOURNAL - CRITICAL LEARNINGS ONLY

## 2024-05-23 - Static Site Image Optimization
**Learning:** In a pure static site (HTML/CSS) without a build process, image optimization relies heavily on manual HTML attributes (`loading="lazy"`, `width`, `height`) and resource hints (`preload`).
**Action:** Always check for missing image attributes in static HTML files as a primary optimization step.

## 2026-02-03 - Native CSS Smooth Scroll
**Learning:** Replacing JS-based smooth scrolling with `html { scroll-behavior: smooth; }` reduces main thread work, enables native accessibility support (reduced-motion), and fixes deep linking (URL hash updates), which JS implementations often break by preventing default.
**Action:** Always prefer native CSS over JS for scrolling behaviors in static sites.

## 2026-02-04 - Image Decoding & Priority
**Learning:** `fetchpriority="high"` on the LCP preload link significantly hints priority to the browser, while `decoding="async"` on below-the-fold images effectively moves decoding off the main thread, reducing UI jank during scroll without visual side effects.
**Action:** Default to `decoding="async"` for all below-fold images and `fetchpriority="high"` for the explicit LCP preload.

## 2026-02-12 - Asset Reuse & Safe Fallbacks
**Learning:** Cross-page asset reuse (using the same WebP file on 404 page as the homepage) significantly reduces total payload and leverages browser caching. Using the `<picture>` element with a `source` for the modern format and `img` for the legacy format ensures robust fallback without JavaScript.
**Action:** Audit secondary pages (like 404) for opportunities to reuse main assets via `<picture>` tags instead of loading unique/legacy formats.

## 2026-02-12 - Third-Party Script Performance
**Learning:** Injected tracking scripts from hosting providers (like GoDaddy's `tccl.min.js`) can impact performance and are outside our direct control.
**Action:** Monitor these scripts' impact on Core Web Vitals. Since they are required for the hosting platform, ensure our own scripts remain optimized to offset any potential overhead.

## 2026-02-13 - Font Synthesis Optimization
**Learning:** Browsers synthesize "faux bold" (and italic) styles when a requested font weight (e.g., 700) isn't loaded, degrading visual quality and performance.
**Action:** Always verify that CSS `font-weight` values match the actually loaded font files. If a weight is missing, switch the element to a font family that has the weight loaded (e.g., UI elements using Inter 700 instead of Source Sans Pro 700).

## 2026-02-13 - Blocking RUM Scripts
**Learning:** Blocking hosting provider RUM scripts avoids performance overhead and potential connection errors.
**Action:** Enforce strict CSP to block these scripts, prioritizing performance and stability.

## 2026-02-13 - Static Site CSS Cleanup
**Learning:** In static sites with inline styles, unused CSS rules accumulate easily over time (e.g., from moved features). Tools like `grep` are essential for auditing class usage when no build step tree-shakes CSS.
**Action:** Before optimizing assets, perform a usage audit of CSS classes against HTML to identify and remove dead code.
## 2025-05-15 - Font Loading Optimization
**Learning:** `Source Sans Pro` weight 600 was loaded but only used by `.logo-tagline`, `.check-icon`, and `.team-role`. These elements work equally well with `Inter` (which already has 600 loaded).
**Action:** Consolidate UI elements to use `Inter` and remove `Source Sans Pro` 600 to save ~20KB on initial load.

## 2025-05-15 - Async Font Loading & Favicon Fix
**Learning:** Strict CSP prevents inline `onload` handlers for font loading. Using an external `async` script (`js/load-fonts.js`) allows earlier font activation than `defer`, improving FCP. Also, missing favicons caused 404s; replaced with `pics/logo.png`.
**Action:** Use external async scripts for critical resource activation under strict CSP. Verify asset existence to avoid 404s.

## 2026-03-04 - DOM Read/Write Interleaving
**Learning:** During element initialization (like scroll reveals), iterating through elements and performing a DOM layout read (e.g. `getBoundingClientRect()`) followed immediately by a DOM write (e.g. `classList.add()`) inside the same loop forces the browser to recalculate the layout synchronously for each element, causing severe layout thrashing.
**Action:** Always separate DOM reads and writes into distinct phases (a read loop followed by a write loop) to allow the browser to batch layout recalculations and optimize rendering performance.

## 2026-03-05 - LCP Priority Contention
**Learning:** Using `fetchpriority="high"` on multiple resources, such as a site logo and a Hero background image, causes them to compete for bandwidth during the initial load, which can delay the actual Largest Contentful Paint (LCP) element (the Hero image).
**Action:** Ensure `fetchpriority="high"` is only applied to the actual LCP element and not secondary decorative elements like logos, so the critical resource loads first.
## 2024-05-22 - [Phaser 3 Asset Loading Redundancy]
**Learning:** Phaser 3 scenes re-run `preload()` every time they are started. If assets (like 60+ images) are defined in `preload()` of a gameplay scene that is revisited, they are re-requested and re-processed, causing significant performance overhead and network traffic.
**Action:** Centralize static/global asset loading in a dedicated `Boot` or `MainMenu` scene. In gameplay scenes, remove the redundant `load.image` calls or wrap them in `if (!this.textures.exists(key))` checks. This pattern was applied to both the desktop (`main.js`) and mobile (`m/main.js`) versions of the game.

## 2024-05-22 - [Map Section SVG Preloading]
**Learning:** Loading large SVG assets for map sections on-demand in `SectionHunt` caused a delay when entering each section. Since there are a small number of sections (11), preloading them all in `MainMenu` eliminates this friction.
**Action:** Added a `filecomplete` listener in `MainMenu` to iterate over the `map_sections` JSON and preload all section SVGs upfront. Removed individual SVG loading from `SectionHunt`.
## 2025-02-03 - Embedded React Optimization
**Learning:** This project uses embedded React (via `esm.sh`) in a single `index.html` file without a build step. Standard performance profiling tools are harder to use. The monolithic `App` component caused all list items to re-render on every state change (like playback progress).
**Action:** Extract list items into `React.memo` components. Pass boolean flags (`isActive`, `isDimmed`) instead of raw ID state to minimize prop changes and maximize memoization hits.

## 2025-02-23 - Memoizing Internal Component Logic
**Learning:** `React.memo` only prevents re-renders if props stay equal. When props *do* change (e.g. `isActive` toggling during scroll), the component re-renders and executes all internal logic. For components with expensive string manipulation (like `VerseGroup` joining verse parts), this internal work can be redundant.
**Action:** Wrap expensive internal content derivations in `useMemo` dependent only on stable data props (like `verseMap` and `group`), ensuring that transient UI state changes (like `isActive`) only trigger a cheap virtual DOM diff, not a full re-computation of text content.

## 2025-03-09 - Constant Hoisting & O(1) Lookups
**Learning:** In hot render paths (like list item rendering), even small allocations (like array literals) and O(N) searches (like `.includes()`) add up when multiplied by hundreds of items.
**Action:** Replaced inline array allocation `['MAT', ...].includes(book)` with global `Set` lookup `NT_BOOKS.has(book)` in `VerseGroup`. Hoisted `months` array out of `formatDate` to avoid reallocation.

## 2026-02-21 - State to Memo Conversion
**Learning:** In React components without a build step (using `esm.sh`), hoisting derived state from `useState` + `useEffect` to `useMemo` significantly reduces render cycles. However, strict attention must be paid to variable definition order (TDZ) within the function body, as `useMemo` executes immediately during render, unlike `useEffect` which runs after.
**Action:** When converting Effects to Memos, always ensure the new Memo is defined *before* any other Memos or variables that depend on it.

## 2026-05-19 - Inline JSX Performance Trap
**Learning:** In a single-file React app, it's easy to keep components like `Footer` inline within the main `App` for convenience. However, this causes the entire footer (and its diffing cost) to run on every `App` re-render (e.g., during scrolling).
**Action:** Extracted `Footer` to a `React.memo` component and memoized its callbacks (`navigateVerse`). This isolates the footer from scroll-driven state updates, reducing main thread work during the critical scroll interaction.

## 2026-08-14 - Broken Memoization from Inline Functions
**Learning:** Passing an inline arrow function as a prop (e.g. `onBookmark={(vid) => setBookmarkDialogTarget(vid)}`) to a `React.memo` component (like `VerseGroup`) creates a new function reference on every parent render. This defeats the memoization, causing all instances of the component to re-render whenever the parent updates (e.g., during high-frequency events like scrolling that update `activeVerseId`).
**Action:** Pass the state setter function directly (e.g., `onBookmark={setBookmarkDialogTarget}`) since React guarantees state setters maintain a stable reference across renders, preserving the memoization and preventing O(N) re-renders.

## 2026-03-14 - [Security Enhancement] Enforced Strict Path Validation & URL Encoding

**Learning:** The `validate_safe_path` function previously only checked for directory traversal characters (`..`, `/`, `\`), which left the door open for other forms of injection or invalid characters when generating filenames or parsing inputs. Furthermore, external API endpoints were constructed without explicitly encoding dynamic parameters like `passage_range` and `bible_id`.

**Action:**
1. Updated `validate_safe_path` in `bible_common.py` to use a strict regex `r'^[a-zA-Z0-9.\-]+$'`, definitively blocking any unexpected characters from entering file paths or internal string references.
2. Updated `fetch_readings.py`, `check_data_integrity.py`, and `fetch_omissions_cache.py` to aggressively encode API URL parameters using `urllib.parse.quote()` to prevent HTTP parameter pollution or API endpoint manipulation.

## 2026-03-16 - Redundant Array Allocation and Transform Computations in Update Loop
**Learning:** During continuous execution loops like Phaser's `update()`, initializing arrays implicitly (e.g. `[this.button1, this.button2].forEach(...)`) causes constant garbage collection pressure from creating array instances every frame. Furthermore, consecutive scale/size alterations (e.g. `setDisplaySize()` immediately followed by `setScale()`) result in multiple redundant transformation matrix recalculations behind the scenes per frame.
**Action:** Always allocate array references outside of hot paths like `update()` loops, and calculate the target explicit transform values (`baseScale` * `zoom`) using math directly ahead of applying a single setting method.

## 2026-03-16 - Environment Desync Circuit Breaker
**Learning:** When a tool or environment limit (like a massive git diff warning) is triggered silently or inconsistently, it traps the session in a state where the agent is seeing an outdated version of the world while trying to operate on the new one. Attempting to reconcile this reality results in a death spiral of wasted tokens and failed attempts, as the agent operates on corrupted state.
**Action:** If `git diff` or `git status` throws a "Diff size unusually large" warning, or otherwise prevents file state verification, IMMEDIATELY trigger a hard circuit breaker. Do not attempt to forcefully reconcile or guess the state. Halt all operations, alert the user to the desync, and request a fresh session to start cleanly.

## 2026-03-18 - [Optimizing Phaser Update Loops]
**Learning:** In Phaser scenes, continuously polling the DOM (like `this.input.setDefaultCursor('none')`) or performing redundant scaling calculations (like determining `this.scale.width` ratios) inside the `update()` loop is highly inefficient as it runs 60 times a second. Static DOM operations should be moved to `create()`. Scaling logic should be moved to a `resize` event listener (`this.scale.on('resize', ...)`). However, state-syncing logic (like reading `foundEggsCount` from the registry to update a text field) CANNOT simply be removed from the `update()` loop without replacing it with an event listener (`this.registry.events.on('changedata', ...)`), or else it causes a functional regression where the UI stops updating.
**Action:** When optimizing `update()` loops, classify operations: DOM manipulation -> move to `create()`. Resizing/scaling -> move to `resize` event listener. State syncing -> replace with registry event listeners.

## 2026-03-19 - Closure Allocations in Hot Paths
**Learning:** In Phaser 3 games, executing array methods that require lambda function closures (like `.forEach()`) inside high-frequency paths such as the 60fps `update()` loop or pointer-move/pointer-down handlers causes significant closure allocations on every frame. This creates constant garbage collection pressure, which can result in noticeable stutter or frame drops, particularly on underpowered mobile devices.
**Action:** Replace `.forEach()` closures with high-performance standard `for` loops (e.g., `for (let i = 0, len = arr.length; i < len; i++)`) in all hot execution paths, including `update()` loops and frequent input handlers, to eliminate closure allocations.

## 2026-03-21 - Redundant Registry Polling in Phaser Update Loops
**Learning:** Continuously polling the Phaser registry (e.g. `this.registry.get('foundEggs').length`) inside `update()` loops (running at 60fps) just to check if UI text needs updating is an inefficient anti-pattern. If the underlying data structure only changes on explicit events (like `collectEgg` or initialization), the UI should be updated explicitly in those specific handlers or via `changedata` events, entirely avoiding the 60fps array length lookup and property comparison.
**Action:** Always map static UI updates directly to explicit action handlers or registry event listeners, and completely remove redundant state-polling logic from the 60fps `update()` loops to reduce main thread pressure.

## 2026-03-25 - Inlining Math and Hoisting Constants in Hot Paths
**Learning:** In Phaser 3, executing math utility functions (like `Phaser.Math.Distance.Squared`) inside inner loops within the 60fps `update()` loop introduces unnecessary function call overhead. Additionally, recalculating loop-invariant constants (like squaring a constant radius or extracting `pointer.x` / `pointer.y`) on every iteration multiplies the performance penalty.
**Action:** Inline simple math calculations (e.g., `dx * dx + dy * dy`) and strictly hoist any loop-invariant property extractions and calculations out of inner `for` loops in hot execution paths.
## 2026-03-27 - [Optimizing Phaser Update Loops Scaling Checks]
**Learning:** Continuously polling for video metadata availability (like `introVideo.width > 0`) and recalculating `scale` properties (e.g. `setDisplaySize`) inside a Phaser 60fps `update()` loop creates a heavy, redundant performance bottleneck. In both desktop and mobile versions, these static calculations were running continuously despite the video size only needing to be calculated once it begins playing or when the window resizes.
**Action:** Removed continuous scale checks from the `update()` loops in `MainMenu` and `SectionHunt` across both desktop and mobile. Instead, bound the scaling logic to one-time `introVideo.once('play')` and continuous `this.scale.on('resize')` event listeners.

## 2026-03-30 - Global Cursor Override & Video Output Restrictions
**Learning:**
1. The user explicitly prefers the `fingerCursor` to remain visible alongside the magnifying glass during `SectionHunt`. Attempting to "fix" this by hiding the finger cursor when the magnifying glass is active is viewed as a regression of a happy accident that improved UX.
2. Furthermore, the user strictly forbids using default Windows cursors (like arrow, pointer, etc) in addition to the custom cursors, which previously resulted in double-cursor rendering over interactive DOM elements or unhandled states.
3. The Playwright UI does NOT support `.webm` video playback without merging to main. Including `.webm` files in PRs clutters the history and frustrates the user, who cannot view them.
**Action:**
1. Reverted the logic that manually toggles `fingerCursor` visibility based on the magnifying glass state in `SectionHunt`. Let both show simultaneously.
2. Verified all `setDefaultCursor('none')` logic is centralized in the global `CursorScene` for both desktop and mobile to permanently prevent default OS cursors from appearing over the game canvas.
3. Configured Playwright verification scripts to NOT record or save `.webm` videos. Only generate `.png` screenshots for frontend verification steps.
