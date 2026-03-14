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

## 2026-03-14 - String Allocation Performance in Critical Loops
**Learning:** Using `String.split()` for simple boundary checks or data extraction inside large `while` loops (like grouping hundreds of verses per day during app initialization) causes significant array allocation overhead and increased garbage collection pressure on mobile devices.
**Action:** Replace `String.split()` with `String.substring()` and `String.indexOf()` when extracting parts of structured IDs within performance-critical initialization or rendering loops.
