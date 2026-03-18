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

## 2026-02-20 - Protocol-Agnostic Link Interception
**Vulnerability:** Users clicking on insecure (http) links to Google Forms bypass the security overlay warning, potentially reducing awareness of leaving the site.
**Learning:** Protocol-specific selectors (like `href^="https://"`) are fragile and can be bypassed by simple protocol changes or typos, even if the destination eventually redirects to HTTPS.
**Prevention:** Use protocol-agnostic selectors or explicitly include both `http` and `https` variants to ensure consistent behavior regardless of the link format.

## 2026-03-04 - Safe Server Hardening
**Vulnerability:** Server configuration files leaking server version and technology stack information, which can assist attackers in fingerprinting vulnerabilities.
**Learning:** Hardening the root `.htaccess` file can easily break unrepresented production sub-sites. I must only apply modifications that are 100% safe to inherit. Adding `Cross-Origin-Resource-Policy "same-site"` or expanding `RedirectMatch 403` to block database extensions (e.g. `.sqlite`, `.db`) risks breaking legitimate client-side database downloads or cross-origin features required by sub-sites like `365DBR`.
**Prevention:** Consolidated safe server hardening in `.htaccess` avoiding assumptions: added `ServerSignature Off` and `Header unset X-Powered-By`. These changes do not affect application routing or sub-site features.
## 2026-02-23 - [Input Validation for Static Assets]
**Vulnerability:** Game logic blindly trusted `symbols.json` content for file paths, potentially allowing Path Traversal or loading of unintended resources if the file was tampered with (e.g., via compromised CDN).
**Learning:** Even "static" JSON configuration files should be treated as untrusted input. Validating file paths against a strict whitelist (e.g., relative path, specific extension, no `..`) prevents unexpected behavior and potential exploits.
**Prevention:** Implement strict schema validation and path sanitization for all external data loaded by the application, regardless of source.

## 2026-02-23 - [Playwright Localhost Resolution]
**Vulnerability:** Playwright scripts using `localhost` failed due to IPv6 resolution (`::1`) when the server only listened on IPv4 (`127.0.0.1`).
**Learning:** Reliability of local verification scripts depends on explicit IP binding. `localhost` is ambiguous.
**Prevention:** Use `127.0.0.1` explicitly in local verification scripts to avoid IPv6/IPv4 mismatches.
## 2025-02-12 - CSP Alignment Mismatch
**Vulnerability:** The Apache server configuration (`.htaccess`) was explicitly set to a "Relaxed Sub-site Policy" allowing `unsafe-eval` and `https:` wildcards, while the client-side HTML meta tags enforced a strict policy.
**Learning:** This created a potential security gap where removing the client-side meta tag (e.g., during development or by accident) would silently degrade security to a very permissive level.
**Prevention:** Ensure server-side security headers (CSP) align strictly with client-side requirements (meta tags) to provide consistent defense-in-depth. Removed `unsafe-eval` from `.htaccess` as Phaser 3 runs without it.

## 2026-03-06 - [Defensive Apache Header Inheritance]
**Vulnerability:** Upstream applications or CDNs (e.g., the corporate parent site) set security headers (like CSP) using `.htaccess` or server configs. Due to Apache inheritance, simply setting headers locally using `Header set` might not reliably override the upstream if they used `Header always set` or had complex proxy rules, leading to the application breaking from an overly strict upstream policy.
**Learning:** To guarantee control over the application's security policy, local configurations must forcefully clear the state before setting their own. Using both `Header always unset` and `Header unset` ensures no ghost headers remain in either Apache header table (success vs always) before applying the definitive local `Header always set`.
**Prevention:** In environments with hierarchical `.htaccess` configurations, use the defensive pattern: `always unset`, `unset`, and `always set` for all critical security headers (CSP, X-Frame-Options, Permissions-Policy, etc.).

## 2024-03-16 - [Testing Depth & Production Reality]
**Learning:** Testing against static, stale sample data (like `0101` and `0102` directories left in the repo) hides edge cases and produces false positives. The `check_data_integrity.py` script previously had no simple mechanism to sample production JSONs randomly or efficiently check wide swaths of the plan when `--days` was limited to sequential starts.
**Action:** Enhanced `check_data_integrity.py` with a `--random` flag that allows it to select a random subset of days to verify against the API, increasing testing depth, breadth, and grounding verification strictly in the reality of production data rather than local mocks.

## 2026-03-18 - [Path Traversal bypass in relative path validation]
**Vulnerability:** The `validate_safe_relative_path` function relied purely on checking for the presence of the `..` string. This naive approach allowed bypasses using URL encoding (`%2e%2e`), absolute paths (e.g. `/etc/passwd`), null byte injection (`\x00`), and Windows-specific drive letter absolute paths (e.g. `C:\Windows\System32`), potentially allowing an attacker to read arbitrary files via malicious relative path arguments.
**Learning:** Checking for literal string matches for path traversal is inadequate against attackers. Path validation must encompass decoding (to catch disguised payloads like URL-encoded variants) and leverage robust, standard libraries (like `pathlib`) that are context-aware of the operating system's filesystem rules (e.g., catching absolute paths on both POSIX and NT systems).
**Prevention:** Hardened `validate_safe_relative_path` in `apps/365DBR/bible_common.py`. Added explicit `urllib.parse.unquote()` for decoding, explicit null-byte checks, strict rejection of leading slashes and Windows drive colons, and a comprehensive fallback using `pathlib.Path(decoded_path).is_absolute()`.
