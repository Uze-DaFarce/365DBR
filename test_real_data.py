import json
import traceback
from bible_common import validate_content_integrity

try:
    with open('0723-ACT.json', 'r') as f:
        data = json.load(f)

    print("Running validate_content_integrity against real production data for ACT.19.23-ACT.19.41...")
    validate_content_integrity(data, "ACT.19.23-ACT.19.41", inject_missing=True)
    print("✅ Validation completed successfully on real data.")
except ValueError as e:
    print(f"❌ Validation raised expected ValueError (Data Integrity): {e}")
except Exception as e:
    print(f"❌ Validation crashed with unexpected error: {e}")
    traceback.print_exc()
