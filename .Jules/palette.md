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
**Action:** Only reveal contextual actions on the "active" or "focused" item. This keeps the UI clean while ensuring the feature is available when the user is in control. Use conditional rendering (e.g., `{isActive && <Button />}`) to manage focus order efficiently.

## 2026-02-08 - Mode-Dependent Interactions
**Learning:** During passive consumption modes (like auto-scrolling playback), "lean-in" interactive elements (like Copy buttons) become moving targets that create visual noise and user frustration.
**Action:** Hide secondary interactive elements during passive modes (playback). The interface should be "calm" when the user is watching/listening, and "active" when the user is in control.

## 2026-02-10 - Programmatic Shortcut Discovery
**Learning:** While visual tooltips help mouse users discover keyboard shortcuts, screen reader users are often left guessing.
**Action:** Always add the `aria-keyshortcuts` attribute (e.g., `aria-keyshortcuts="ArrowLeft"`) to interactive elements that have associated key listeners. This makes the invisible shortcuts explicit to assistive technologies without cluttering the visual UI.

## 2026-02-18 - Quick Return to Present
**Learning:** In date-based navigation apps, users often get lost in past/future dates and need a quick way to return to "Today" without manually navigating or refreshing.
**Action:** Make the current date display interactive (e.g., a button) when it deviates from the actual today, providing a one-click "Jump to Today" action.

## 2026-02-24 - Progressive Disclosure for Mouse vs Keyboard
**Learning:** Mouse users can easily scan and target arbitrary items, while keyboard users rely on linear navigation. Forcing keyboard users to tab through actions for every item in a long list is tedious.
**Action:** Allow mouse users to reveal actions via hover on *any* item (using `group-hover`), but restrict keyboard access (via `tabIndex`) to only the *active* or *focused* item to keep the tab order clean.

## 2026-02-24 - Discoverability vs Clutter
**Learning:** While "hover-to-reveal" reduces visual clutter, users perceive it as "hidden" or "easter egg" functionality for core utilities like Copying.
**Action:** For primary actions (like Copy), prefer persistent visibility (even if subtle) over hidden states. Use opacity/color to manage visual weight instead of `display:none` or `opacity:0`.

## 2026-02-25 - Click-to-Focus for Focal Interfaces
**Learning:** In interfaces where scrolling determines the "active" item (like a focal verse list), users instinctively click items to select or focus them. Relying solely on scroll position frustrates users who want manual control or struggle with scroll precision.
**Action:** Implement `onClick` handlers that smoothly scroll the target item into the "focal zone" (e.g., using `scrollIntoView`), but ensure to gate it against text selection interactions (check `window.getSelection()`).

## 2026-02-26 - Mobile Feature Parity
**Learning:** Hiding core navigation (like "Browse" mode) on mobile devices to save space creates a second-class experience for mobile users, effectively locking them out of major features.
**Action:** Use responsive utility classes to adapt the *presentation* of the link (e.g., hiding the text label but keeping the icon) rather than hiding the entire element. This preserves functionality while respecting mobile constraints.

## 2026-02-27 - Unified Keyboard Shortcuts
**Learning:** Users expect consistent keyboard shortcuts across all modes of an application (e.g., Daily Reader vs. Bible Browser), even if the modes serve different purposes. Inconsistency here breaks muscle memory.
**Action:** Centralize keyboard shortcut logic or ensure parity (e.g., Arrow keys for navigation, 'k' for playback) across all distinct views/pages.

## 2026-02-24 - Time Investment Transparency
**Learning:** In daily habit apps (like Bible reading), users often hesitate to start a session if they are unsure of the length. Providing a time estimate reduces friction and encourages engagement ("It's only 5 mins").
**Action:** Calculate and display estimated reading time (e.g., '5 min read') based on content length (approx. 200-250 wpm) near the primary content label or footer to set clear expectations.

## 2024-03-08 - Automated Screenshot Reviews
**Learning:** Users want to visually review test output screenshots (.png), but committing these to Git causes code review failures and repo bloat.
**Action:** Always configure the CI pipeline (e.g. GitHub Actions) to automatically upload `test-results` and `playwright-report` as downloadable artifacts rather than ignoring them completely. This makes visual regressions visible without git consequences.
