## 2025-02-18 - Keyboard Navigation Visibility
**Learning:** In Tailwind projects without a global focus reset, buttons often lack visible focus states, making keyboard navigation impossible for accessibility users. relying on browser defaults is unreliable.
**Action:** Establish a standard "focus ring" utility class pattern (e.g., `focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2`) and apply it to *every* interactive element by default.

## 2025-02-18 - Keyboard Shortcuts for Sequential Content
**Learning:** For apps with sequential navigation (like a daily reader), keyboard shortcuts (Arrows, Space/k) significantly improve usability and are expected by power users.
**Action:** Always map Left/Right arrows to previous/next navigation and provide visual hints (e.g. in tooltips) for discovery.

## 2026-02-05 - Skip Links for Sticky Headers
**Learning:** In single-page apps with complex sticky headers (nav, settings, playback controls), keyboard users are forced to tab through 10+ elements before reaching the content. This causes fatigue and makes the app feel "heavy".
**Action:** Always include a "Skip to Content" link (`href="#main"`) as the first interactive element. Use `sr-only focus:not-sr-only` to keep it hidden until needed, and ensure the target has `tabIndex="-1"` and `outline-none` for correct focus behavior without visual clutter.

## 2026-02-19 - Manual State Indicators
**Learning:** In "home-grown" UI components (like manual dropdowns in embedded React), users lack standard cues like checkmarks or focus trapping. Visual feedback becomes critical.
**Action:** Always explicitely add state indicators (checkmarks for selection, rotation for open state) to custom controls, as they won't inherit browser or library defaults.
