# Managing Sub-Sites and CSP Overrides

This repository (`mt-sin.ai`) serves as the root site for several sub-applications hosted in subdirectories, such as `/HeIsRisen`, `/m`, and `/365DBR`.

## The Challenge: Inheritance of Strict Security Headers

The root site enforces a strict Content Security Policy (CSP) via its `.htaccess` file to protect the main application. This policy includes:
-   Blocking external scripts (except specific allowances).
-   Blocking inline scripts and styles (mostly).
-   Blocking `eval()` (which many game engines like Phaser use).
-   Blocking external connections (connect-src).

By default, Apache applies these headers to all subdirectories. This often breaks third-party games or legacy apps that rely on CDNs, inline scripts, or looser security models.

## The Solution: Directory-Specific Overrides

To fix this without compromising the root site's security, we place a **relaxed `.htaccess` file** in each sub-site's directory. This file overrides the inherited headers with a permissive configuration suitable for games and static apps.

### Standard Relaxed Configuration

For any new sub-site (e.g., a new game), create a `.htaccess` file in its folder with the following content:

```apache
<IfModule mod_headers.c>
  # 🛡️ Sentinel: Relaxed Sub-site Policy
  # Overrides strict root policies to support 3rd-party games and external assets (CDNs).
  # Required for: Phaser, external APIs, and inline game logic.

  # Reset CSP to be permissive for this subdirectory
  # Allows:
  # - Scripts/Styles/Images/Connect from ANY HTTPS source (needed for CDNs like jsdelivr)
  # - 'unsafe-inline' and 'unsafe-eval' (common in games/legacy apps)
  # - data: and blob: (common for game assets)
  Header set Content-Security-Policy "default-src 'self' https: data: blob: 'unsafe-inline' 'unsafe-eval'; upgrade-insecure-requests;"

  # Relax X-Frame-Options to allow same-origin framing if needed
  Header set X-Frame-Options "SAMEORIGIN"

  # Standard Referrer Policy
  Header set Referrer-Policy "strict-origin-when-cross-origin"

  # Note on Permissions Policy:
  # The root .htaccess sets a strict Permissions-Policy (disabling usb, interest-cohort, etc).
  # If your sub-site needs these features (e.g., WebAuthn, Geolocation), you must override it here:
  # Header set Permissions-Policy "geolocation=(self), publickey-credentials-get=(self), ..."
</IfModule>
```

### Why this works
-   `Header set Content-Security-Policy ...`: The `set` command replaces any existing CSP header inherited from the parent directory.
-   `https:`: Allows loading resources from any HTTPS URL (e.g., `cdn.jsdelivr.net`, `fonts.googleapis.com`, etc.).
-   `'unsafe-inline' 'unsafe-eval'`: Necessary for many HTML5 games (like Phaser) and older scripts.
-   `data: blob:`: Essential for game assets loaded as blobs or data URIs.

## Maintenance

-   **If a sub-site breaks:** Check the browser console for CSP violations (e.g., "Refused to load script...").
-   **If specific domains are blocked:** The permissive policy above allows *all* HTTPS domains, so blocks are unlikely unless the resource is HTTP (insecure).
-   **New Sub-sites:** Simply copy the `.htaccess` from `HeIsRisen/` or `m/` into the new directory.
