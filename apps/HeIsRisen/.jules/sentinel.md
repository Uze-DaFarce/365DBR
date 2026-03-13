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
