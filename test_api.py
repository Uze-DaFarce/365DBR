import os
import json
import urllib.request
import urllib.parse
from bible_common import NT_GREEK_ID, API_BASE_URL, extract_verse_ids

api_key = os.environ.get("API_BIBLE_KEY")
if not api_key:
    print("Set API_BIBLE_KEY")
    exit(1)

url = f"{API_BASE_URL}/bibles/{NT_GREEK_ID}/passages/ACT.19.23-ACT.19.41?include-verse-spans=true"
req = urllib.request.Request(url, headers={"api-key": api_key})
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode('utf-8'))
vids = extract_verse_ids(data['data']['content'])
print(f"Count: {len(vids)}")
print(f"Verses: {sorted(list(vids))}")
