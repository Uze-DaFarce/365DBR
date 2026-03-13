# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities to the maintainers privately. Do not open public issues for security vulnerabilities.

## Content Security Policy (CSP)

This application uses a Content Security Policy to protect against Cross-Site Scripting (XSS) and other code injection attacks.

The policy is defined in the `<meta>` tag in `index.html` and `m/index.html`:

- `default-src 'self'`: Only allow resources from the same origin by default.
- `script-src 'self' https://cdn.jsdelivr.net`: Allow scripts from the application origin and the jsDelivr CDN (for Phaser).
- `style-src 'self' 'unsafe-inline'`: Allow styles from the application origin and inline styles (required for Phaser canvas).
- `img-src 'self' data: blob:`: Allow images from the application origin, data URIs, and blobs (used by Phaser).
- `connect-src 'self'`: Allow XHR/Fetch requests only to the application origin (for loading JSON data).
- `worker-src 'self' blob:`: Allow web workers from the application origin and blobs.
- `object-src 'none'`: Prevents embedding of plugins like Flash or Java.
- `base-uri 'self'`: Restricts the URLs that can be used in a document's `<base>` element to the same origin.
- `form-action 'self'`: Restricts the URLs which can be used as the target of a form submissions.

If you encounter issues running the game, ensure your environment supports these directives.

## Referrer Policy

This application sets the `Referrer-Policy` to `strict-origin-when-cross-origin` via a `<meta>` tag. This ensures that the full URL is not sent as a referrer to other origins, protecting user privacy.

## Subresource Integrity (SRI)

This application uses Subresource Integrity (SRI) to ensure that resources hosted on third-party servers (CDNs) have not been altered. The `integrity` attribute is used on `<script>` tags loading Phaser from jsDelivr.
