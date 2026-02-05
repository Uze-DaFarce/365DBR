# Sentinel's Security Journal

## 2024-05-23 - Referrer Policy for Static Sites
**Vulnerability:** Default browser referrer behavior can leak full URL paths (potentially containing sensitive query parameters) to third-party sites.
**Learning:** Static sites hosted without server configuration access (like .htaccess or _headers) cannot easily set HTTP security headers.
**Prevention:** Use `<meta name="referrer" content="strict-origin-when-cross-origin">` in the HTML `<head>` to enforce privacy at the document level.

## 2026-02-05 - Vulnerability Disclosure Policy
**Vulnerability:** Lack of a clear channel for security researchers to report vulnerabilities can lead to irresponsible disclosure or unpatched issues.
**Learning:** Even static sites benefit from a formal security policy.
**Prevention:** Added `.well-known/security.txt` following RFC 9116 to define contact methods and policy expiration.
