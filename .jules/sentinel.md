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

## 2026-03-18 - [Preventing Reverse Tabnabbing on Ecosystem Links]
**Vulnerability:** The application contained links pointing to the parent domain (`mt-sin.ai`) opening in a new tab via `window.open(link, '_blank')`. Opening links without `noopener` leaves the window open to reverse tabnabbing via the `window.opener` object.
**Learning:** While `noopener,noreferrer` is the gold standard for truly external links, applying `noreferrer` to links pointing to another application within the same ecosystem (like `mt-sin.ai/365DBR`) can break internal analytics and routing that rely on the `Referer` header.
**Prevention:** Use `noopener` alone when linking to trusted internal/ecosystem sites via `window.open(link, '_blank', 'noopener')` to prevent reverse tabnabbing while preserving necessary referer headers. Reserve `noopener,noreferrer` strictly for untrusted or third-party outgoing links.

## 2026-03-18 - [Frontend Verification Media Scoping]
**Learning:** The `frontend_verification_complete` tool silently fails to post images/media to the user chat if the file paths point outside the repository's root workspace directory (e.g., `/home/jules/verification/`). Additionally, using `read_media_file` only injects the image into the agent's context and does NOT show it to the user.
**Action:** Always save or move verification media into the repository root (or a relative folder inside the repo) before calling `frontend_verification_complete`. Ensure to clean up these artifacts afterward to avoid workspace pollution.

## 2026-03-20 - Game State Vulnerabilities

**Learning:** The live frontend applications (`HeIsRisen/main.js` and `m/main.js`) successfully handle corrupted `localStorage` inputs (such as `NaN`, `undefined`, or out-of-bounds volume values) without crashing. They use bounds-checking and `isNaN` fallbacks, parsing strings with `parseInt` and `parseFloat`, gracefully falling back to safe default values.

**Action:** Built `test_state_corruption.py` and `test_game_state.py` in `apps/HeIsRisen/tests/` using Playwright to dynamically inject corrupted and valid `localStorage` objects before Phaser initialization to ensure data resilience is continuously verified.

## 2026-03-21 - [HeIsRisen localStorage State Corruption Resilience]
**Learning:** The HeIsRisen game `localStorage` state parsers (`getSafeVol` and `parseInt(highScore)`) gracefully handle malicious and malformed edge cases including `-Infinity`, `NaN`, `"{}"`, and empty string injection. The Phaser registry defaults appropriately back to 0.5 for volumes and 0 for scores without crashing the Web Audio API or game state loop.
**Action:** Expanded the test suite `apps/HeIsRisen/tests/test_state_corruption.py` to assert edge-case boundaries actively instead of simple out-of-bounds inputs, confirming the logic correctly defaults to 0.5. Also verified `test_production_future_data.py` exists and successfully validates production API data.

## 2026-03-23 - [Sentinel] Resiliency against Corrupted JSON in Game State
**Learning:** JSON.parse throws exceptions on malformed local storage data, causing the whole game state loading sequence to crash and blocking the fallback to default states, and potentially soft-locking the game entirely if left unchecked.
**Action:** Wrapped JSON.parse in a try-catch block for the `heIsRisenGameState` and added corrupted JSON testing into the `test_state_corruption.py` test suite.

## 2026-03-25 - [Missing Network Data Fallbacks]
Dynamically loaded external JSON files accessed via `cache.json.get('key')` (like `map_sections.json` or `symbols.json`) will return `undefined` or `null` if the network request fails or is blocked. To prevent fatal frontend crashes, always validate the result (e.g., `Array.isArray(data)`) and provide a safe fallback (e.g., `[]` or `{{}}`) before iterating or accessing properties like `.length`.
## 2026-03-26 - [Robust Game State Validation]
*   Identified that game state loaded from `localStorage` in `HeIsRisen` and `m` apps was vulnerable to type/NaN corruption.
*   Added strict type checks (`Array.isArray`) for array structures like `eggData`, `sections`, `foundEggs`, and `stampedSections`.
*   Added bounds checking and `isNaN` parsing for `correctCategorizations` and `currentScore`.
*   Strengthened `test_state_corruption.py` to aggressively simulate corrupted states and assert successful fallback to defaults.
## 2026-03-26 - [Robust Test Suite Dependencies and Execution]
*   Updated `test_helpers.py` to auto-install missing packages (`pillow`, `playwright`, `pytest`) at runtime using `subprocess.check_call`, completely preventing agent sandbox initialization errors and pipeline halts.
*   Fixed mobile `pointer.x` click simulation math in Playwright tests by explicitly applying `lensOffsetX` and `lensOffsetY` mapping, and triggering native `scene.input.emit('pointerdown')` instead of brittle DOM bounding box intercepts.
*   Ensured fallback simulated collection correctly updates the `foundEggs` registry to include full `symbolData` so the `EggZamRoom` sorting dialog can process testing states accurately.
*   Consolidated and removed redundant low-value screenshots in `test_ui_interactions.py` (e.g. intermediate pressed states, closing menus) to reduce test noise.

## 2026-03-28 - Strict Validation for External Game State (localStorage)
**Learning:** `parseInt()` can lead to silent failures by partially parsing invalid strings (e.g., `parseInt('5a')` returns `5`). This violates the "fail fast on corruption" principle and could allow corrupted game state from `localStorage` to bypass initialization checks.
**Action:** Replaced all instances of `parseInt()` with `Number()` when reading `localStorage` data (`currentScore`, `correctCategorizations`, `highScore`) in `apps/HeIsRisen/main.js` and `apps/HeIsRisen/m/main.js`. Added strict `!isFinite()` and `isNaN()` validation to ensure corrupted or malformed inputs correctly reset the game state safely.
## 2026-03-30 - Prevent DOM Exceptions from blocked localStorage
**Learning:** Browser privacy settings or restrictive iframe contexts can forcefully deny access to the `localStorage` API. Directly accessing it (e.g., `localStorage.getItem('key')`) without wrapping it in a `try-catch` block will immediately throw an uncaught `DOMException: Access denied for this document`, fatally crashing the entire application script.
**Action:** Always wrap `localStorage.getItem`, `localStorage.setItem`, and `localStorage.removeItem` operations in robust `try-catch` blocks and implement safe fallback defaults (e.g., in-memory state or safe numbers) to ensure the game functions seamlessly even when storage persistence is disabled.
## 2024-04-02 - Strict localStorage Parsing

Replaced `Number()` and `parseFloat()` in `apps/HeIsRisen/main.js` and `apps/HeIsRisen/m/main.js` with a strict type-checking parsing pattern: `(val !== null && String(val).trim() !== '' && typeof val !== 'object') ? Number(val) : NaN`. This ensures arrays and whitespaces do not bypass the `isNaN` checks and cause data corruption.
