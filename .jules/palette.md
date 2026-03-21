<<<<<<< .jules/palette.md
## 2024-03-08 - Automated Screenshot Reviews
**Learning:** Users want to visually review test output screenshots (.png), but committing these to Git causes code review failures and repo bloat.
**Action:** Always configure the CI pipeline (e.g. GitHub Actions) to automatically upload `test-results` and `playwright-report` as downloadable artifacts rather than ignoring them completely. This makes visual regressions visible without git consequences.

## 2025-02-18 - Keyboard Navigation Visibility
**Learning:** In Tailwind projects without a global focus reset, buttons often lack visible focus states, making keyboard navigation impossible for accessibility users. relying on browser defaults is unreliable.
**Action:** Establish a standard "focus ring" utility class pattern (e.g., `focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2`) and apply it to *every* interactive element by default.

## 2025-02-18 - Keyboard Shortcuts for Sequential Content
**Learning:** For apps with sequential navigation (like a daily reader), keyboard shortcuts (Arrows, Space/k) significantly improve usability and are expected by power users.
**Action:** Always map Left/Right arrows to previous/next navigation and provide visual hints (e.g. in tooltips) for discovery.

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

## 2026-02-05 - Skip Links for Sticky Headers
**Learning:** In single-page apps with complex sticky headers (nav, settings, playback controls), keyboard users are forced to tab through 10+ elements before reaching the content. This causes fatigue and makes the app feel "heavy".
**Action:** Always include a "Skip to Content" link (`href="#main"`) as the first interactive element. Use `sr-only focus:not-sr-only` to keep it hidden until needed, and ensure the target has `tabIndex="-1"` and `outline-none` for correct focus behavior without visual clutter.

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

## 2026-02-08 - Contextual Actions on Active State
**Learning:** In a long list of items (verses), placing action buttons (like Copy) on every item creates visual clutter and tab-order fatigue.
**Action:** Only reveal contextual actions on the "active" or "focused" item. This keeps the UI clean while ensuring the feature is available when the user is in control. Use conditional rendering (e.g., `{isActive && <Button />}`) to manage focus order efficiently.

## 2026-02-08 - Mode-Dependent Interactions
**Learning:** During passive consumption modes (like auto-scrolling playback), "lean-in" interactive elements (like Copy buttons) become moving targets that create visual noise and user frustration.
**Action:** Hide secondary interactive elements during passive modes (playback). The interface should be "calm" when the user is watching/listening, and "active" when the user is in control.

## 2026-02-08 - Mobile Nav Auto-Scroll
**Learning:**
On mobile devices with horizontally scrolling navigation, the "active" link can become hidden off-screen as the user scrolls down the page (since the nav doesn't automatically follow). This breaks the "Where am I?" feedback loop.
**Action:**
Added logic to the scroll handler to automatically scroll the active navigation link into view (`scrollIntoView` with `inline: 'center'`). This ensures the wayfinding indicator is always visible without requiring user interaction.

## 2026-02-10 - Programmatic Shortcut Discovery
**Learning:** While visual tooltips help mouse users discover keyboard shortcuts, screen reader users are often left guessing.
**Action:** Always add the `aria-keyshortcuts` attribute (e.g., `aria-keyshortcuts="ArrowLeft"`) to interactive elements that have associated key listeners. This makes the invisible shortcuts explicit to assistive technologies without cluttering the visual UI.

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

## 2026-02-18 - Quick Return to Present
**Learning:** In date-based navigation apps, users often get lost in past/future dates and need a quick way to return to "Today" without manually navigating or refreshing.
**Action:** Make the current date display interactive (e.g., a button) when it deviates from the actual today, providing a one-click "Jump to Today" action.

## 2026-02-18 - Focus Lift & Reduced Motion
**Learning:**
1. **Focus Parity:** Keyboard users often miss out on the "delight" of interaction (like card lifts on hover). Adding `:focus-within` triggers to the same transform properties ensures parity.
2. **Motion Sensitivity:** Applying transforms on hover/focus can cause motion sickness for some users. It is critical to wrap these effects in `@media (prefers-reduced-motion: reduce)` to disable them.
**Action:**
1. Added `.service-card:focus-within` and `.project-card:focus-within` to match hover states.
2. Implemented a consolidated `@media (prefers-reduced-motion: reduce)` block to force `transform: none` and `transition: none` on all interactive elements (`.service-card`, `.project-card`, `.team-member`, `.btn-primary`, `.back-to-top`).

## 2026-02-19 - Manual State Indicators
**Learning:** In "home-grown" UI components (like manual dropdowns in embedded React), users lack standard cues like checkmarks or focus trapping. Visual feedback becomes critical.
**Action:** Always explicitely add state indicators (checkmarks for selection, rotation for open state) to custom controls, as they won't inherit browser or library defaults.

## 2026-02-23 - Persisting Layout Context
**Learning:** In single-page apps, replacing the entire UI with a full-screen loader during navigation (even for 200ms) causes jarring layout shifts and disorients users, especially when navigation controls disappear.
**Action:** Always Implement an "App Shell" pattern where the `<Header>` and `<Footer>` remain visible during loading states. Only the content area (`<main>`) should display the spinner/skeleton.

## 2026-02-24 - Progressive Disclosure for Mouse vs Keyboard
**Learning:** Mouse users can easily scan and target arbitrary items, while keyboard users rely on linear navigation. Forcing keyboard users to tab through actions for every item in a long list is tedious.
**Action:** Allow mouse users to reveal actions via hover on *any* item (using `group-hover`), but restrict keyboard access (via `tabIndex`) to only the *active* or *focused* item to keep the tab order clean.

## 2026-02-24 - Discoverability vs Clutter
**Learning:** While "hover-to-reveal" reduces visual clutter, users perceive it as "hidden" or "easter egg" functionality for core utilities like Copying.
**Action:** For primary actions (like Copy), prefer persistent visibility (even if subtle) over hidden states. Use opacity/color to manage visual weight instead of `display:none` or `opacity:0`.

## 2026-02-24 - Time Investment Transparency
**Learning:** In daily habit apps (like Bible reading), users often hesitate to start a session if they are unsure of the length. Providing a time estimate reduces friction and encourages engagement ("It's only 5 mins").
**Action:** Calculate and display estimated reading time (e.g., '5 min read') based on content length (approx. 200-250 wpm) near the primary content label or footer to set clear expectations.

## 2026-02-25 - Click-to-Focus for Focal Interfaces
**Learning:** In interfaces where scrolling determines the "active" item (like a focal verse list), users instinctively click items to select or focus them. Relying solely on scroll position frustrates users who want manual control or struggle with scroll precision.
**Action:** Implement `onClick` handlers that smoothly scroll the target item into the "focal zone" (e.g., using `scrollIntoView`), but ensure to gate it against text selection interactions (check `window.getSelection()`).

## 2026-02-26 - Mobile Feature Parity
**Learning:** Hiding core navigation (like "Browse" mode) on mobile devices to save space creates a second-class experience for mobile users, effectively locking them out of major features.
**Action:** Use responsive utility classes to adapt the *presentation* of the link (e.g., hiding the text label but keeping the icon) rather than hiding the entire element. This preserves functionality while respecting mobile constraints.

## 2026-02-27 - Unified Keyboard Shortcuts
**Learning:** Users expect consistent keyboard shortcuts across all modes of an application (e.g., Daily Reader vs. Bible Browser), even if the modes serve different purposes. Inconsistency here breaks muscle memory.
**Action:** Centralize keyboard shortcut logic or ensure parity (e.g., Arrow keys for navigation, 'k' for playback) across all distinct views/pages.

## 2026-03-04 - State Affordance via Animated Icons
**Learning:**
Buttons that toggle large state changes (like expanding a section) lack predictability if their action is implied only by text changes after the fact. Visual indicators of directionality improve usability.
**Action:**
1.  **Iconography:** Added an explicit `<svg>` chevron to the expand/collapse button.
2.  **Animation:** Tied the CSS `transform: rotate(180deg)` directly to the button's `aria-expanded` state, ensuring visual and semantic state remain perfectly in sync.
3.  **DOM Preservation:** Modified JavaScript logic to selectively update only a `<span class="btn-text">` inside the button, preventing the `textContent` assignment from obliterating the SVG icon.

## 2026-03-04 - Activity States during Delays
**Learning:**
Overlays that impose a time delay (like the Form Handoff's 8-second redirect/dismiss window) can feel "stuck" if there is no visual indicator of ongoing activity.
**Action:**
1.  **Visual Cue:** Added a subtle CSS `@keyframes pulse-emoji` animation to the Form Handoff emoji (`.pulsing-emoji`).
2.  **Accessibility Check:** Wrapped the animation in `@media (prefers-reduced-motion: reduce) { animation: none; }` to protect users with motion sensitivity.

## 2026-03-04 - Native Smooth Scroll Focus Synchronization
**Learning:**
When using native CSS smooth scrolling (`scroll-behavior: smooth`) alongside internal anchor links (`href="#target"`), the visual viewport moves to the target, but keyboard focus often remains on the clicked link. This strands keyboard/screen reader users.
**Action:**
Added a global JavaScript event listener for all `a[href^="#"]` links that:
1.  **Extracts** the target ID.
2.  **Sets** `tabindex="-1"` on the target element (making it programmatically focusable).
3.  **Applies** `.focus({ preventScroll: true })` inside a `setTimeout` (to allow smooth scroll to execute) so users can immediately continue tabbing from their new visual location.
## 2024-05-22 - Map Interaction Feedback
**Learning:** Invisible hit areas on maps leave users guessing; adding a simple hover outline significantly improves discoverability.
**Action:** Ensure all interactive zones, especially non-rectangular ones, have a visual hover state (outline or tint).

## 2024-05-25 - Consistent Interaction Feedback
**Learning:** Users expect consistent feedback across scenes. Since `MapScene` provided hover outlines and cursor scaling, the absence of these in `EggZamRoom` made the interactive zones feel broken or undiscoverable.
**Action:** Reused the feedback pattern (yellow outline + cursor scale) from `MapScene` in `EggZamRoom` to maintain consistency and improve discoverability.

## 2024-05-26 - Center Alignment for Labels
**Learning:** Left-aligned labels in fixed-width containers often look unbalanced or get clipped if the container logic isn't perfect. Centering text (`setOrigin(0.5)`) ensures it expands evenly and looks more polished in score boxes.
**Action:** Use centered origin for HUD labels like scores or counts to prevent visual imbalance.

## 2024-05-27 - Responsive HUD Text Scaling
**Learning:** HUD text that looks perfect on mobile often overlaps or feels overwhelmingly large when the same codebase is rendered on desktop (e.g., in responsive or emulated views). Checking `sys.game.device.os.desktop` allows for nuanced typography adjustments.
**Action:** Always verify HUD element spacing on both mobile and desktop contexts, and use device detection to scale font sizes and adjust vertical spacing to prevent overlap.

## 2026-03-02 - Keyboard Accessibility Parity on Mobile
**Learning:** Dismissing overlays or modals via keyboard commands (like `ESC`) is frequently missed on "mobile" environments where touch is presumed to be the only input. However, on tablets or mobile web views attached to external keyboards, the absence of basic keyboard navigation feels broken. Parity with the desktop codebase on core keyboard interactions is essential.
**Action:** Ensure standard keyboard dismiss handlers (`ESC`, `ENTER` for modals) are consistently applied across both desktop and mobile scenes.

## 2026-03-08 - Auto-focus Game Canvas for Screen Readers
**Learning:** HTML5 canvas games (like Phaser) wrapped in an `aria-label` container rely on that container gaining focus to be announced by screen readers. Since games don't inherently pull focus without interaction, users relying on keyboards/screen readers might have difficulty discovering the game if it is not explicitly focused on load. The existing `tabindex="0"` on the wrapper requires the user to manually `Tab` to it first.
**Action:** Always add a `window.addEventListener('load', () => { container.focus() })` to auto-focus the game container on load, and ensure a `:focus-visible` CSS rule provides a visual outline for sighted keyboard users.

## 2026-03-11 - Endgame Keyboard Accessibility Parity
**Learning:** When adding end-of-game actions like "Play Again" buttons, relying solely on pointer events breaks the loop for keyboard users who might have navigated the final modals using Space/Enter. Critical flow actions must always have keyboard parity.
**Action:** Always bind `Space` and `Enter` keys to primary final-screen CTAs (like Restart/Play Again) to ensure the game loop can be completed without a mouse.
## 2025-05-15 - Consistent Interaction Patterns
**Learning:** The project uses a custom `addButtonInteraction` function to provide scale-based hover/press feedback for `Phaser.GameObjects`. This pattern was missing from the `UIScene` Gear Icon, leading to an inconsistent feel.
**Action:** Always check for existing interaction helpers (like `addButtonInteraction`) before implementing custom pointer handlers. When modifying UI elements, ensure they use the established feedback patterns (scale 1.1x on hover, 0.9x on press) for a cohesive experience.

## 2025-05-15 - Asset Orientation and Hotspots
**Learning:** When using directional cursors (like a pointing finger), `setOrigin` and `angle` must be coordinated to align the visual "tip" with the logical "hotspot" (coordinates). Specifically, flipping a cursor 180 degrees requires changing the origin (e.g., from Center or Top-Left to match the new Tip location relative to the unrotated texture) so that the GameObject's `(x, y)` position remains the click point.
**Action:** When rotating interaction cursors, visualize the texture in local space. If the "hotspot" moves due to rotation, adjust `setOrigin` so the pivot point remains the desired hotspot (e.g., the fingertip).

## 2024-05-24 - [Slider and Settings UX]
**Learning:** Phaser 3's `setInteractive` on shapes doesn't automatically enable the pointer cursor unless configured. Furthermore, small interactive elements (like slider tracks) need larger invisible hit areas to be accessible and easy to use.
**Action:** Always add an invisible, larger "hit area" rectangle/circle behind small UI elements and explicitly set `{ cursor: 'pointer' }` or `object.input.cursor = 'pointer'` for better affordance.

## 2024-05-22 - [Phaser 3 Input & Playwright Mobile]
**Learning:**
1.  **Phaser 3 Container Draggability:**
    *   Using `container.setInteractive(hitArea, callback, { draggable: true })` does NOT automatically enable dragging.
    *   Correct pattern: Call `container.setInteractive(...)` then explicitly call `scene.input.setDraggable(container)`.
    *   This is critical for mobile sliders using Container wrappers for larger hit areas.

2.  **Playwright Mobile Emulation:**
    *   `iPhone 12 Landscape` is not a valid device descriptor.
    *   To emulate landscape on mobile devices in Playwright, use the base device (e.g., `iPhone 12`) and manually swap the viewport width/height in the context options.

**Action:**
*   Always use `input.setDraggable(obj)` for draggable elements.
*   Use manual viewport swapping for landscape mobile tests.
## 2026-03-16 - Semantic Wrappers for Full-Screen Apps
**Learning:** Even fully Canvas-rendered apps (like Phaser games) benefit from `<main>` semantic wrappers and `<noscript>` tags at the HTML level. It provides structure for screen readers and graceful degradation for users without JS without disrupting the game container.
**Action:** Always wrap `#game` or `#game-container` in `<main>` when scaffolding new Phaser apps in the monorepo, and provide a `<noscript>` styled fallback.
## 2024-03-17 - [Native feel for Canvas HTML5 Games]
**Learning:** Adding `user-select: none` and `touch-action: none` (or `-webkit-tap-highlight-color: transparent`) to the CSS body or canvas container of a fullscreen HTML5 game prevents accidental text selection highlights and tap-highlight flashes on mobile devices.
**Action:** Always apply these CSS rules to HTML5 canvas games to make the game feel like a native app and improve the interactive UX.

## 2026-03-18 - Juicy Core Loops
**Learning:** When a game revolves around a single core action repeated dozens of times (like collecting 60 eggs), a basic fade-out feedback makes the game feel flat and unrewarding. Kids respond strongly to "juiciness"—exaggerated feedback on their actions.
**Action:** Enhance primary collection interactions with multiple simultaneous, playful tweens (e.g., scaling up to 1.5x with a 360-degree rotation while floating upwards). These micro-UX changes make the core loop deeply satisfying without requiring new art assets.

## 2026-03-19 - Tactile Feedback Requires Delay
**Learning:**
When upgrading buttons that trigger immediate scene transitions (like Restart or Close buttons) to use standard tactile feedback tweens (e.g., `addButtonInteraction`), the immediate callback execution cuts off the visual and auditory feedback. The interaction feels broken because the scene unloads before the tween or audio finishes.
**Action:**
Whenever adding `addButtonInteraction` to a button that transitions or unloads the scene, always wrap the callback logic in a `this.time.delayedCall(150, () => { ... })` to allow the user to see and hear the satisfying "pop" and "click" before the screen changes.

## 2026-03-20 - Empty State Calls to Action
**Learning:** Presenting a static "All items categorized" empty state when the user is only partially through the game creates a "dead end" in the flow. Users may mistakenly believe they have finished the entire game rather than just their current batch.
**Action:** Always provide explicit, contextual Calls to Action (CTAs) in empty states (e.g., "Return to the map to find more") so the user clearly understands what to do next to continue the core game loop.
=======
<<<<<<< SEARCH
=======
## 2026-03-21 - [Smart Audio Looping for Repetitive Video]
**Learning:** In Phaser 3, when a video or audio object is configured to loop (e.g., `play(true)`), it emits the `'loop'` event upon repeating, not the `'complete'` event.
**Action:** Implemented a smart audio looping feature by binding to `.on('loop', ...)` that mutes background videos after the first play and unmutes them every 5th loop, preventing audio fatigue from short clips.
>>>>>>> REPLACE
>>>>>>> .jules/palette.md.patch
