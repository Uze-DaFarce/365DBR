## 2025-02-18 - Keyboard Navigation Visibility
**Learning:** In Tailwind projects without a global focus reset, buttons often lack visible focus states, making keyboard navigation impossible for accessibility users. relying on browser defaults is unreliable.
**Action:** Establish a standard "focus ring" utility class pattern (e.g., `focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2`) and apply it to *every* interactive element by default.

## 2025-02-18 - Keyboard Shortcuts for Sequential Content
**Learning:** For apps with sequential navigation (like a daily reader), keyboard shortcuts (Arrows, Space/k) significantly improve usability and are expected by power users.
**Action:** Always map Left/Right arrows to previous/next navigation and provide visual hints (e.g. in tooltips) for discovery.

## 2026-02-04 - Graceful Error States in Single-File React
**Learning:** In single-file React apps without a build step, strict data dependencies (like daily JSON) can cause silent failures (white screen) if not explicitly caught.
**Action:** Always implement a dedicated `error` state in the main App component and render a user-friendly, centered 'Retry' UI that matches the serif/book aesthetic.
