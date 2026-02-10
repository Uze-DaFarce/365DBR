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

## 2026-02-23 - Persisting Layout Context
**Learning:** In single-page apps, replacing the entire UI with a full-screen loader during navigation (even for 200ms) causes jarring layout shifts and disorients users, especially when navigation controls disappear.
**Action:** Always Implement an "App Shell" pattern where the `<Header>` and `<Footer>` remain visible during loading states. Only the content area (`<main>`) should display the spinner/skeleton.

## 2026-02-08 - Contextual Actions on Active State
**Learning:** In a long list of items (verses), placing action buttons (like Copy) on every item creates visual clutter and tab-order fatigue.
**Action:** Only reveal contextual actions on the "active" or "focused" item. This keeps the UI clean while ensuring the feature is available when the user's attention is on that specific content. Use conditional rendering (e.g., `{isActive && <Button />}`) to manage focus order efficiently.

## 2026-02-08 - Mode-Dependent Interactions
**Learning:** During passive consumption modes (like auto-scrolling playback), "lean-in" interactive elements (like Copy buttons) become moving targets that create visual noise and user frustration.
**Action:** Hide secondary interactive elements during passive modes (playback). The interface should be "calm" when the user is watching/listening, and "active" when the user is in control.
