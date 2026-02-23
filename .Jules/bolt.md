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

## 2026-02-12 - Asset Reuse & Safe Fallbacks
**Learning:** Cross-page asset reuse (using the same WebP file on 404 page as the homepage) significantly reduces total payload and leverages browser caching. Using the `<picture>` element with a `source` for the modern format and `img` for the legacy format ensures robust fallback without JavaScript.
**Action:** Audit secondary pages (like 404) for opportunities to reuse main assets via `<picture>` tags instead of loading unique/legacy formats.

## 2026-02-12 - Third-Party Script Performance
**Learning:** Injected tracking scripts from hosting providers (like GoDaddy's `tccl.min.js`) can impact performance and are outside our direct control.
**Action:** Monitor these scripts' impact on Core Web Vitals. Since they are required for the hosting platform, ensure our own scripts remain optimized to offset any potential overhead.

## 2026-02-13 - Font Synthesis Optimization
**Learning:** Browsers synthesize "faux bold" (and italic) styles when a requested font weight (e.g., 700) isn't loaded, degrading visual quality and performance.
**Action:** Always verify that CSS `font-weight` values match the actually loaded font files. If a weight is missing, switch the element to a font family that has the weight loaded (e.g., UI elements using Inter 700 instead of Source Sans Pro 700).

## 2026-02-13 - Blocking RUM Scripts
**Learning:** Blocking hosting provider RUM scripts avoids performance overhead and potential connection errors.
**Action:** Enforce strict CSP to block these scripts, prioritizing performance and stability.

## 2026-02-13 - Static Site CSS Cleanup
**Learning:** In static sites with inline styles, unused CSS rules accumulate easily over time (e.g., from moved features). Tools like `grep` are essential for auditing class usage when no build step tree-shakes CSS.
**Action:** Before optimizing assets, perform a usage audit of CSS classes against HTML to identify and remove dead code.
## 2025-05-15 - Font Loading Optimization
**Learning:** `Source Sans Pro` weight 600 was loaded but only used by `.logo-tagline`, `.check-icon`, and `.team-role`. These elements work equally well with `Inter` (which already has 600 loaded).
**Action:** Consolidate UI elements to use `Inter` and remove `Source Sans Pro` 600 to save ~20KB on initial load.

## 2025-05-15 - Async Font Loading & Favicon Fix
**Learning:** Strict CSP prevents inline `onload` handlers for font loading. Using an external `async` script (`js/load-fonts.js`) allows earlier font activation than `defer`, improving FCP. Also, missing favicons caused 404s; replaced with `pics/logo.png`.
**Action:** Use external async scripts for critical resource activation under strict CSP. Verify asset existence to avoid 404s.
