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

## 2025-05-21 - Focus Indicators & Transition Performance
**Learning:**
1. **Focus Visibility:** Standard `transition: all` on links causes focus outlines to animate from 0px width, making them feel sluggish or invisible during rapid keyboard navigation.
   * *Fix:* Changed `transition: all` to `transition: color` (or specific properties) on `nav a` to ensure the focus ring appears instantly.
2. **Accessible Colors:** Applied specific focus colors: Purple (`#401b51`) for light backgrounds and Gold (`#F4A623`) for dark contexts (Header, Footer) to ensure 3:1+ contrast ratio.
## 2025-05-20 - Context-Aware Focus Indicators
**Learning:** Default focus rings often fail contrast requirements on branded backgrounds. A single global focus color (e.g., Purple) becomes invisible on a Purple header/footer.
**Action:** Implemented context-aware focus colors using CSS nesting or specific selectors.
*   **Default:** Purple (`#401b51`) for light backgrounds.
*   **Dark Contexts:** Gold (`#F4A623`) for Header/Footer elements to ensure high visibility and brand alignment.
## 2026-01-29 - Brand-Aligned Focus Indicators
**Learning:** Default browser focus rings (usually blue) often clash with brand palettes or lack sufficient contrast against custom backgrounds (like purple headers).
**Action:** Implemented a pattern of context-aware `:focus-visible` styles:
1.  **Global Default:** Brand Primary Color (Purple) with `outline-offset` for visibility on white.
2.  **Dark Contexts:** Brand Secondary Color (Gold) for high contrast on dark backgrounds (Header/Footer).

## 2026-02-02 - Active Nav State & Wayfinding
**Learning:**
On single-page sites with sticky headers, users often lose context of "where they are" relative to the navigation structure. Relying solely on hover states makes the interface feel static and unresponsive.
**Action:**
Implemented an "Active Nav State" pattern:
1.  **Visual Feedback:** Applied the same styles as `:hover` (Color/Underline) to the `.active` class for consistency.
2.  **Logic:** Used a "Last Passed" algorithm in JS (checking scroll position against target offsets) to ensure the active state persists even when scrolling through "gap" sections (like #bookkeeping) that aren't explicitly in the top-level nav but belong to the previous section's flow.
3.  **Accessibility:** Added `aria-current="page"` dynamically to the active link to communicate context to assistive technologies.

## 2026-02-03 - Accessible Modal Overlay Pattern
**Learning:**
Custom JS-based overlays/modals often lack basic accessibility features (focus trap, ARIA roles, keyboard dismissal), creating barriers for keyboard and screen reader users.
**Action:**
Implemented a robust pattern for dynamic overlays:
1.  **Roles:** `role="alertdialog"` and `aria-modal="true"`.
2.  **Focus Management:** Explicitly move focus to the overlay on open (`tabindex="0"`), and restore focus to the triggering element on close.
3.  **Keyboard Support:** Listen for `Escape`, `Enter`, and `Space` to allow dismissal without a mouse.

## 2026-02-04 - Decorative Icon Accessibility
**Learning:**
Using emojis or icons as primary visual anchors (e.g., in service cards or lists) creates auditory clutter for screen reader users if not properly managed. Hearing "Chart increasing" before "Bookkeeping" is redundant and distracting.
**Action:**
Systematically apply `aria-hidden="true"` to all decorative icon containers. For mixed content (e.g., `<li>📊 <a...`), wrap the decorative element in a `<span>` to apply the attribute without hiding the semantic content.

## 2026-02-05 - Clickable Cards & Focus Management
**Learning:**
1. **Clickable Cards:** Users expect cards to be clickable. The most robust accessible pattern is expanding the primary link's hit area using `::after` (absolute position) over a `position: relative` card container. This preserves semantic HTML structure.
2. **Focus Traps:** "Back to Top" buttons that disappear (via `visibility: hidden` or `display: none`) must explicitly move focus to a logical start point (e.g., Logo) to prevent leaving keyboard users stranded.
**Action:**
Applied `position: relative` to cards and `::after` overlay to links. Updated JS to focus logo on scroll-to-top.
