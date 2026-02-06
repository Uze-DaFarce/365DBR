## 2025-02-03 - Embedded React Optimization
**Learning:** This project uses embedded React (via `esm.sh`) in a single `index.html` file without a build step. Standard performance profiling tools are harder to use. The monolithic `App` component caused all list items to re-render on every state change (like playback progress).
**Action:** Extract list items into `React.memo` components. Pass boolean flags (`isActive`, `isDimmed`) instead of raw ID state to minimize prop changes and maximize memoization hits.

## 2025-02-23 - Memoizing Internal Component Logic
**Learning:** `React.memo` only prevents re-renders if props stay equal. When props *do* change (e.g. `isActive` toggling during scroll), the component re-renders and executes all internal logic. For components with expensive string manipulation (like `VerseGroup` joining verse parts), this internal work can be redundant.
**Action:** Wrap expensive internal content derivations in `useMemo` dependent only on stable data props (like `verseMap` and `group`), ensuring that transient UI state changes (like `isActive`) only trigger a cheap virtual DOM diff, not a full re-computation of text content.
