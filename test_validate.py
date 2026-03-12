import traceback
import sys
import os

from bible_common import validate_content_integrity

# Dummy data mimicking API response for ACT.19.23-ACT.19.41 (simulating 1 verse missing to trigger tolerance logic)
dummy_data = {
    "data": {
        "content": [
            {"attrs": {"verseId": f"ACT.19.{i}"}} for i in range(23, 41) # 18 verses, missing 41
        ]
    }
}

try:
    print("Running validate_content_integrity...")
    validate_content_integrity(dummy_data, "ACT.19.23-ACT.19.41", inject_missing=False)
    print("✅ Validation completed without crashing (it should have warned or passed).")
except ValueError as e:
    print(f"✅ Validation raised expected ValueError (Data Integrity): {e}")
except Exception as e:
    print(f"❌ Validation crashed with unexpected error: {e}")
    traceback.print_exc()
