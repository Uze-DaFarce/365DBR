# BOLT'S JOURNAL - CRITICAL LEARNINGS ONLY

## 2024-05-23 - Static Site Image Optimization
**Learning:** In a pure static site (HTML/CSS) without a build process, image optimization relies heavily on manual HTML attributes (`loading="lazy"`, `width`, `height`) and resource hints (`preload`).
**Action:** Always check for missing image attributes in static HTML files as a primary optimization step.

## 2026-02-03 - Native CSS Smooth Scroll
**Learning:** Replacing JS-based smooth scrolling with `html { scroll-behavior: smooth; }` reduces main thread work, enables native accessibility support (reduced-motion), and fixes deep linking (URL hash updates), which JS implementations often break by preventing default.
**Action:** Always prefer native CSS over JS for scrolling behaviors in static sites.

## 2026-02-04 - Image Decoding & Priority
**Learning:** `fetchpriority="high"` on the LCP preload link significantly hints priority to the browser, while `decoding="async"` on below-the-fold images effectively moves decoding off the main thread, reducing UI jank during scroll without visual side effects.
**Action:** Default to `decoding="async"` for all below-fold images and `fetchpriority="high"` for the explicit LCP preload.
