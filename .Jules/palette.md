## 2025-02-18 - Keyboard Navigation Visibility
**Learning:** In Tailwind projects without a global focus reset, buttons often lack visible focus states, making keyboard navigation impossible for accessibility users. relying on browser defaults is unreliable.
**Action:** Establish a standard "focus ring" utility class pattern (e.g., `focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2`) and apply it to *every* interactive element by default.
