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

## 2026-02-06 - Form Handoff Pattern
**Learning:**
External forms (like Google Forms) create a disconnect when users click a "Contact" button and are immediately taken away. Standard "success" overlays on the original tab confuse users who haven't submitted anything yet.
**Action:**
Implemented a "Form Handoff" overlay:
1. **Expectation Management:** Changed text from "Thank you" to "Opening Secure Form...".
2. **Visual Cue:** Used a Memo emoji (📝) instead of Prayer Hands (🙏).
3. **Accessibility:** Updated `aria-label` to explicitly state "Form Handoff".
This pattern ensures users know they are entering a secure external flow.

## 2026-02-07 - Visible Exit Strategy for Overlays
**Learning:**
Even with `Escape` key support and click-outside dismissal, users (especially in high-stakes "leaving site" flows) experience anxiety without a visible "Close" button.
**Action:**
Added a high-contrast "✕" button to the Form Handoff overlay.
1.  **Affordance:** Explicit visual cue to cancel the action.
2.  **Accessibility:** `aria-label="Close"` and large touch target (44px).
3.  **Feedback:** Hover/Focus states to indicate interactivity.

## 2026-02-08 - Mobile Nav Auto-Scroll
**Learning:**
On mobile devices with horizontally scrolling navigation, the "active" link can become hidden off-screen as the user scrolls down the page (since the nav doesn't automatically follow). This breaks the "Where am I?" feedback loop.
**Action:**
Added logic to the scroll handler to automatically scroll the active navigation link into view (`scrollIntoView` with `inline: 'center'`). This ensures the wayfinding indicator is always visible without requiring user interaction.

## 2026-02-12 - UI Injection Awareness
**Learning:** Hosting providers may inject scripts that can manipulate the DOM or add invisible tracking elements.
**Action:** Be aware that "invisible" scripts (like analytics) might occasionally inject elements that could interfere with layout or accessibility. Inspect the live DOM if unexpected elements appear.

## 2026-02-13 - Persistent Tooltip UX
**Learning:**
Traditional `title` attributes are slow to appear and lack styling control. Relying on click-only feedback for "Copy" actions misses the opportunity to guide the user *before* the interaction.
**Action:**
Replaced the `title` attribute with a custom, persistently present (but visually toggled) tooltip.
1.  **Discoverability:** Tooltip appears instantly on hover/focus ("Copy email").
2.  **Feedback:** Text updates dynamically to "Copied!" on success without layout shifts or DOM thrashing (using `replaceWith` and text updates instead of full rebuilds).

## 2026-02-13 - Preventing UI Injections
**Learning:** Blocking hosting provider scripts prevents potential UI injections that can interfere with layout or accessibility.
**Action:** Enforce strict CSP to ensure no unauthorized elements are injected into the DOM.

## 2026-02-14 - Clickable Card Focus & Performance
**Learning:**
1. **Focus Rings:** Using `transition: all` on buttons/cards causes the focus ring (`outline`) to animate/grow, which feels sluggish and degrades perceived performance.
   * *Fix:* Use specific transition properties (e.g., `transform`, `box-shadow`) to ensure focus rings snap instantly.
2. **Card Focus:** When a card is fully clickable via an overlay link, the default focus state usually only highlights the inner text link. This disconnects the visual focus from the actual click target (the whole card).
   * *Fix:* Use `:focus-within` on the card container to apply the focus ring to the entire card, and hide the inner link's default focus ring.

## 2026-02-15 - Dynamic Copy Button Logic
**Learning:**
Refactoring a single-use "Copy" button to a reusable pattern requires careful state management. When multiple buttons exist, relying on global selectors (like `document.querySelector`) breaks functionality for subsequent elements.
**Action:**
Use `querySelectorAll` and iterate with `forEach`. Store element-specific state (like `originalLabel`) within the event handler closure to ensure the correct text is restored for each specific button after the "Copied!" timeout.
## 2026-02-15 - Visual Polish & Accessibility Micro-Fixes
**Learning:**
1. **Aspect Ratio Distortion:** Fixed width (e.g., `width: 90px`) on responsive images (logos) often causes distortion (squashing) when combined with `max-height` constraints.
   * *Fix:* Use `width: auto` + `max-height` to respect the image's intrinsic aspect ratio across all viewports.
2. **Redundant Alt Text:** Images used as logos next to text (e.g., `<img alt="Company Logo"> Company Name`) create redundant auditory clutter for screen readers.
   * *Fix:* Set `alt=""` on the image to mark it as decorative, allowing the screen reader to focus on the semantic text content.
3. **Decorative SVGs:** Inline SVGs in links (like social icons) can be announced as "group" or "image" by screen readers, adding noise.
   * *Fix:* Add `aria-hidden="true"` to these decorative SVGs to ensure a clean, text-only announcement of the link's label.

## 2026-02-16 - Print Optimization
**Learning:**
Users often "Print to PDF" to share service details with stakeholders. Standard web pages include clutter (nav bars, buttons, dark backgrounds) that waste ink and look unprofessional on paper.
**Action:**
Implemented a `@media print` stylesheet to create a clean, document-like output:
1.  **Hidden UI:** Removed navigation, footer links, and interactive buttons (`.header`, `.footer`, `.buttons`).
2.  **Ink Saving:** Forced high-contrast text (`color: #000`) and white backgrounds, removing shadows and colorful hero sections.
3.  **Layout:** Reset containers to 100% width and allowed natural page breaks for long content (like Reviews).

## 2026-02-16 - Context Maintenance on Collapse
**Learning:**
When collapsible sections (like "Read More" reviews) are closed from the bottom, the page height shrinks upwards, leaving the user's viewport stranded in empty space or unrelated content (like the footer). This causes disorientation and loss of context.
**Action:**
Implemented a smooth scroll behavior that returns the user to the top of the section immediately upon triggering the collapse. This ensures the user is grounded in the original context (the start of the list) rather than being left behind by the shrinking layout.

## 2026-02-18 - Scroll Progress Indicator
**Learning:**
On long landing pages, users benefit from a visual indicator of their progress, especially when the header is sticky.
**Action:**
Implemented a lightweight Scroll Progress Bar:
1.  **Structure:** Added `.scroll-progress-container` absolute positioned at the bottom of the sticky `<header>`.
2.  **Logic:** Calculated scroll percentage `(scrollY / (scrollHeight - clientHeight))` in the existing `requestAnimationFrame` loop to avoid performance overhead.
3.  **Visuals:** Used the brand's secondary color (Gold) for high contrast against the primary header color (Purple).

## 2026-02-18 - Focus Management & Context Preservation
**Learning:**
1.  **Expanded Content Visibility:** When expanding content (like "Read More" reviews), screen reader users often miss the new content if it appears visually *before* the trigger button.
    *   *Fix:* Programmatically move focus to the expanded container (`tabindex="-1"`) immediately upon expansion.
2.  **Collapsed Context Loss:** When collapsing a large section from the bottom, the page shrinks, potentially leaving the viewport stranded in empty space below the content. Scrolling to the *top* of the section can also be disorienting as it forces the user to re-read content.
    *   *Fix:* Scroll the viewport to center the **toggle button** itself. This keeps the user grounded at their current "decision point" in the flow, ready to proceed.
## 2026-02-18 - Focus Lift & Reduced Motion
**Learning:**
1. **Focus Parity:** Keyboard users often miss out on the "delight" of interaction (like card lifts on hover). Adding `:focus-within` triggers to the same transform properties ensures parity.
2. **Motion Sensitivity:** Applying transforms on hover/focus can cause motion sickness for some users. It is critical to wrap these effects in `@media (prefers-reduced-motion: reduce)` to disable them.
**Action:**
1. Added `.service-card:focus-within` and `.project-card:focus-within` to match hover states.
2. Implemented a consolidated `@media (prefers-reduced-motion: reduce)` block to force `transform: none` and `transition: none` on all interactive elements (`.service-card`, `.project-card`, `.team-member`, `.btn-primary`, `.back-to-top`).
