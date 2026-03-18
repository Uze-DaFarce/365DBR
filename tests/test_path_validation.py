import sys
import os

# Add apps/365DBR to path so we can import bible_common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'apps', '365DBR')))

from bible_common import validate_safe_relative_path

paths = {
    "..": False,
    "%2e%2e/etc/passwd": False,
    "/etc/passwd": False,
    "C:\\Windows\\System32": False,
    "data/foo.json": True,
    "C:foo": False,
    "foo/bar/baz.txt": True,
    "\x00/etc/passwd": False,
}

for path, expected in paths.items():
    result = validate_safe_relative_path(path)
    if result != expected:
        print(f"FAIL: {path} -> Expected {expected}, got {result}")
    else:
        print(f"PASS: {path} -> {result}")
