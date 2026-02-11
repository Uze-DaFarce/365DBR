## 2026-02-07 - Visible Exit Strategy for Overlays
**Learning:**
Even with `Escape` key support and click-outside dismissal, users (especially in high-stakes "leaving site" flows) experience anxiety without a visible "Close" button.
**Action:**
Added a high-contrast "✕" button to the Form Handoff overlay.
1.  **Affordance:** Explicit visual cue to cancel the action.
2.  **Accessibility:** `aria-label="Close"` and large touch target (44px).
3.  **Feedback:** Hover/Focus states to indicate interactivity.
