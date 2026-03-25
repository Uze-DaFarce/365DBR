## 2024-03-20 - [Add Screen Reader Announcements to Canvas Games]
**Learning:** HTML5 Canvas games (like Phaser 3) natively trap screen readers because the internal game state is completely hidden from the DOM. Without explicit DOM elements, critical gameplay interactions (like collecting an item or completing a level) are completely invisible to assistive technologies.
**Action:** Always inject an invisible `aria-live="polite"` DOM element (e.g., `<div id="sr-announcer" class="sr-only" aria-live="polite"></div>`) alongside the canvas element. Update its `textContent` dynamically via JavaScript when critical game events occur to make the canvas experience accessible without disrupting the visual UI.

## 2024-03-20 - [Engage the Sense of Touch via Haptic Feedback]
**Learning:** For mobile and tablet users playing highly repetitive or visually focused games, adding short bursts of haptic feedback (vibration) for key successful interactions (like collecting an item) significantly increases the feeling of reward and tactility for the vast majority of players.
**Action:** Use `if (navigator && navigator.vibrate) { navigator.vibrate(50); }` to provide a subtle 50ms pulse of tactile feedback upon a successful user interaction, creating a more multi-sensory and engaging micro-UX.
