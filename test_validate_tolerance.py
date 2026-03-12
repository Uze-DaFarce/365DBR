import traceback
import sys
import os

from bible_common import validate_content_integrity

# Let's bypass the boundary check (which fails first in the previous test)
# by ensuring the start and end verses ARE present, but a verse in the middle is missing.
# Expected verses: 19 (23 through 41). Actual verses: 18 (23 through 41, missing 30).
dummy_data = {
    "data": {
        "content": [
            {"attrs": {"verseId": f"ACT.19.{i}"}} for i in range(23, 42) if i != 30
        ]
    }
}

try:
    print("Running validate_content_integrity (testing tolerance logic)...")
    validate_content_integrity(dummy_data, "ACT.19.23-ACT.19.41", inject_missing=False)
    print("✅ Validation completed successfully (tolerance accepted 1 missing verse).")
except Exception as e:
    print(f"❌ Validation failed: {e}")
    traceback.print_exc()
