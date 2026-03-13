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
