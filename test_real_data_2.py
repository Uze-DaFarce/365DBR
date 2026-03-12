import json
import traceback
from bible_common import validate_content_integrity

# Let's test the other day 0704 which you mentioned earlier.
# The user's earlier error on 0704 was:
# ValueError: [Data Integrity] Verse Count Mismatch for ACT.8.32-ACT.9.13. Expected 21, Got 22

import urllib.request
import urllib.error

url = 'https://mt-sin.ai/365DBR/data/0704/ACT.8.32-ACT.9.13.json'

try:
    req = urllib.request.Request(url)
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))

    print("Running validate_content_integrity against real production data for ACT.8.32-ACT.9.13...")
    # inject_missing=True because this range contains ACT.8.37
    validate_content_integrity(data, "ACT.8.32-ACT.9.13", inject_missing=True)
    print("✅ Validation completed successfully on real data (Tolerance worked).")
except ValueError as e:
    print(f"❌ Validation raised ValueError: {e}")
except urllib.error.HTTPError as e:
    print(f"Failed to fetch {url}: {e}")
except Exception as e:
    print(f"❌ Validation crashed with unexpected error: {e}")
    traceback.print_exc()
