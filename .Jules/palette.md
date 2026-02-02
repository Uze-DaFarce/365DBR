## 2025-05-20 - Pivot to Professional Redesign
**Learning:** The initial goal was a "micro-UX" fix (skip link), but the user explicitly requested a full "professional visual redesign".
**Action:** Prioritized user goal over persona constraints.

**Implemented Changes:**
- **Theme:** Purple (`#401b51`) & Gold (`#F4A623`) identity.
- **Layout:** Card-based grids.
- **Assets:** High-quality backgrounds.

## 2025-05-20 - Content Preservation & Grid Precision
**Learning:**
1.  **Content Loss:** When redesigning, *never* remove content (like reviews) without explicit permission. Even if it looks "cleaner", users value their social proof.
    *   *Fix:* Restored all 16 reviews, using a "Read More" toggle to manage visual clutter.
2.  **Grid Layouts:** `auto-fit` can create awkward "orphan" items (e.g., 3 items on row 1, 1 on row 2).
    *   *Fix:* Use explicit media queries to force 4-col, 2-col, or 1-col layouts (powers of 2) to ensure balanced rows.
3.  **Hover States:** Avoid `transform: translate` on hover for small UI elements like social icons if it causes visual "jumping" or layout shifts that annoy users.
    *   *Fix:* Use color/background transitions instead of movement for cleaner interaction.

## 2025-05-20 - Accessible Accordion Animation
**Learning:** `display: none` is necessary for accessibility (hiding content from screen readers) but prevents CSS transitions.
**Action:** Use a combination of `grid-template-rows` transition for the visual animation and the `transitionend` event listener to toggle the `hidden` class (display: none). This ensures both a smooth delight (animation) and robust accessibility.

## 2026-01-29 - Brand-Aligned Focus Indicators
**Learning:** Default browser focus rings (usually blue) often clash with brand palettes or lack sufficient contrast against custom backgrounds (like purple headers).
**Action:** Implemented a pattern of context-aware `:focus-visible` styles:
1.  **Global Default:** Brand Primary Color (Purple) with `outline-offset` for visibility on white.
2.  **Dark Contexts:** Brand Secondary Color (Gold) for high contrast on dark backgrounds (Header/Footer).
