## 2025-02-03 - Embedded React Optimization
**Learning:** This project uses embedded React (via `esm.sh`) in a single `index.html` file without a build step. Standard performance profiling tools are harder to use. The monolithic `App` component caused all list items to re-render on every state change (like playback progress).
**Action:** Extract list items into `React.memo` components. Pass boolean flags (`isActive`, `isDimmed`) instead of raw ID state to minimize prop changes and maximize memoization hits.
