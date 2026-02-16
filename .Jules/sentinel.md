# Sentinel's Security Journal

## 2024-05-23 - Referrer Policy for Static Sites
**Vulnerability:** Default browser referrer behavior can leak full URL paths (potentially containing sensitive query parameters) to third-party sites.
**Learning:** Static sites hosted without server configuration access (like .htaccess or _headers) cannot easily set HTTP security headers.
**Prevention:** Use `<meta name="referrer" content="strict-origin-when-cross-origin">` in the HTML `<head>` to enforce privacy at the document level.

## 2026-02-05 - Vulnerability Disclosure Policy
**Vulnerability:** Lack of a clear channel for security researchers to report vulnerabilities can lead to irresponsible disclosure or unpatched issues.
**Learning:** Even static sites benefit from a formal security policy.
**Prevention:** Added `.well-known/security.txt` following RFC 9116 to define contact methods and policy expiration.

## 2026-02-06 - Maximized CSP for Static Sites
**Vulnerability:** Incremental CSP hardening leaves gaps and annoys developers. Meta-tag CSPs have limitations (e.g., `frame-ancestors` is ignored).
**Learning:** To "max out" a meta-tag CSP for a static site, enable `require-trusted-types-for 'script'` and `worker-src 'none'` alongside standard directives. Do not attempt `frame-ancestors` in meta tags.
**Prevention:** Enforce a comprehensive CSP in a single pass: `default-src 'self'`, strict `script-src` (no 'unsafe-inline' if possible), `worker-src 'none'`, and Trusted Types.

## 2026-02-07 - Robots.txt Hardening for Sensitive Directories
**Vulnerability:** Default crawler behavior indexes all accessible directories, potentially exposing `.git` metadata or internal documentation (`.Jules`) if server directory listing is enabled or paths are guessed.
**Learning:** In static hosting environments without server-side access controls (like .htaccess), `robots.txt` acts as a critical line of defense against information leakage via search engines.
**Prevention:** Explicitly `Disallow` known sensitive directories (like `/.git/` and `/.Jules/`) in `robots.txt` to prevent indexing.
## 2026-02-08 - Defense in Depth with robots.txt
**Vulnerability:** Default server configurations may inadvertently expose hidden directories (like `.git/` or `.Jules/`) containing sensitive metadata or journals.
**Learning:** Relying solely on "security through obscurity" (hidden folders) or web server config is risky; `robots.txt` acts as an additional, though advisory, layer of defense against reputable crawlers.
**Prevention:** Explicitly disallow sensitive paths in `robots.txt` to signal intent and prevent accidental indexing by search engines.

## 2026-02-09 - CSP Violation by Inline Scripts
**Vulnerability:** An inline script block for critical functionality (clipboard copy) violated the strict `script-src 'self'` CSP directive, rendering the feature non-functional.
**Learning:** Defining a strict CSP in `<meta>` tags without auditing existing codebase for inline scripts creates a false sense of security and breaks functionality.
**Prevention:** Audit all `<script>` tags before enforcing `script-src 'self'`. Move logic to external files to ensure compliance and functionality.

## 2026-02-12 - Hosting Provider CSP Injection
**Vulnerability:** Hosting providers (e.g., GoDaddy) may inject scripts for analytics or tracking, which are blocked by a strict `script-src 'self'` CSP.
**Learning:** Automatically injected scripts often use inline code or external domains (like `img1.wsimg.com`). These must be explicitly allowed in the CSP.
**Prevention:** Monitor console errors for blocked scripts. Allow trusted domains and use SHA-256 hashes for specific inline scripts to maintain security without using `'unsafe-inline'`.

## 2026-02-13 - Blocking Hosting Provider Scripts
**Vulnerability:** Hosting provider scripts can introduce unauthorized tracking and console noise.
**Learning:** Allowing these scripts compromises the security posture and causes connection errors.
**Prevention:** Intentionally block hosting provider scripts via strict CSP (`script-src 'self'`) to prevent unauthorized tracking and console noise.

## 2026-02-14 - Sub-Site CSP Inheritance
**Vulnerability:** Strict root CSP headers are inherited by sub-directories, breaking third-party applications (e.g., games using Phaser) that require looser policies (unsafe-eval, CDN access).
**Learning:** Apache's configuration inheritance applies security headers downwards. Sub-sites need explicit overrides to function if they have different security requirements.
**Prevention:** Created `SUB_SITES.md` to document the pattern of placing a relaxed `.htaccess` in sub-directories (`Header set Content-Security-Policy ...`) to override the root policy without compromising the main site.

## 2026-02-15 - Permissions Policy Hardening with Sub-Site Consideration
**Vulnerability:** Unused browser features (like `usb`, `browsing-topics`) increase the attack surface and potential for fingerprinting/tracking.
**Learning:** Root `.htaccess` headers propagate to sub-sites. Hardening policies like `Permissions-Policy` (e.g., disabling `publickey-credentials-get` for WebAuthn) can silently break sub-site functionality (like user login in `365DBR`) if inheritance is not managed.
**Prevention:** Explicitly create configuration scaffolds (like `.htaccess`) for sub-sites—even if their content is external—to ensure they override strict root policies. This prevents "invisible" breakage where a sub-site inherits breaking changes from the root.
