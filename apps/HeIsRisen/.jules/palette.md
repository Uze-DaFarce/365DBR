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
