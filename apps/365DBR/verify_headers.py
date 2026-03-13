import re
import sys

def verify_headers():
    htaccess_path = ".htaccess"

    try:
        with open(htaccess_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {htaccess_path} not found.")
        sys.exit(1)

    required_headers = [
        (r'Header set Cross-Origin-Opener-Policy "same-origin"', "Cross-Origin-Opener-Policy: same-origin"),
        (r'Header set Content-Security-Policy', "Content-Security-Policy"),
        (r'Header set X-Frame-Options "DENY"', "X-Frame-Options: DENY"),
        (r'Header set Referrer-Policy "strict-origin-when-cross-origin"', "Referrer-Policy: strict-origin-when-cross-origin"),
        (r'Header set Strict-Transport-Security', "Strict-Transport-Security"),
        (r'Header set Permissions-Policy', "Permissions-Policy"),
        (r'Header set X-Content-Type-Options "nosniff"', "X-Content-Type-Options: nosniff"),
        (r'Header set X-XSS-Protection "1; mode=block"', "X-XSS-Protection: 1; mode=block"),
    ]

    missing_headers = []

    for pattern, name in required_headers:
        if not re.search(pattern, content):
            missing_headers.append(name)

    if missing_headers:
        print("❌ Missing required security headers in .htaccess:")
        for header in missing_headers:
            print(f"  - {header}")
        sys.exit(1)
    else:
        print("✅ All required security headers found in .htaccess.")

if __name__ == "__main__":
    verify_headers()
