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
