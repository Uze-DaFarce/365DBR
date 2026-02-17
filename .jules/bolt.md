## 2025-02-03 - Embedded React Optimization
**Learning:** This project uses embedded React (via `esm.sh`) in a single `index.html` file without a build step. Standard performance profiling tools are harder to use. The monolithic `App` component caused all list items to re-render on every state change (like playback progress).
**Action:** Extract list items into `React.memo` components. Pass boolean flags (`isActive`, `isDimmed`) instead of raw ID state to minimize prop changes and maximize memoization hits.

## 2025-02-23 - Memoizing Internal Component Logic
**Learning:** `React.memo` only prevents re-renders if props stay equal. When props *do* change (e.g. `isActive` toggling during scroll), the component re-renders and executes all internal logic. For components with expensive string manipulation (like `VerseGroup` joining verse parts), this internal work can be redundant.
**Action:** Wrap expensive internal content derivations in `useMemo` dependent only on stable data props (like `verseMap` and `group`), ensuring that transient UI state changes (like `isActive`) only trigger a cheap virtual DOM diff, not a full re-computation of text content.

## 2025-03-09 - Constant Hoisting & O(1) Lookups
**Learning:** In hot render paths (like list item rendering), even small allocations (like array literals) and O(N) searches (like `.includes()`) add up when multiplied by hundreds of items.
**Action:** Replaced inline array allocation `['MAT', ...].includes(book)` with global `Set` lookup `NT_BOOKS.has(book)` in `VerseGroup`. Hoisted `months` array out of `formatDate` to avoid reallocation.

## 2025-03-10 - Event Handler Stabilization
**Learning:** In a monolithic React component, event handlers (like `handleToggle`) often depend on rapidly changing state (like `activeVerseId` during scroll). This causes the handler to be recreated on every scroll tick. If this handler is passed to child components (like a Header), those children re-render unnecessarily, even if `React.memo` is used.
**Action:** Use the "Ref Pattern": Store the volatile state in a `useRef` and keep it synced via `useEffect`. Have the event handler read from `.current` instead of the state directly. This removes the state from the handler's dependency array, stabilizing its identity and preventing child re-renders.
