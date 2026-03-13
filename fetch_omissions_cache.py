import os
import json
import urllib.request
import urllib.error
import urllib.parse
from bible_common import KNOWN_OMISSIONS, PARALLEL_IDS, API_BASE_URL, atomic_write_json

def get_api_key():
    key = os.environ.get("API_BIBLE_KEY")
    if not key:
        print("Error: API_BIBLE_KEY environment variable not set.")
        return None
    return key.strip()

def fetch_bulk_passages(api_key, bible_id, vids):
    passage_str = ",".join(vids)
    url = f"{API_BASE_URL}/bibles/{bible_id}/passages/{passage_str}"

    params = {
        "content-type": "json",
        "include-notes": "false",
        "include-titles": "false",
        "include-chapter-numbers": "false",
        "include-verse-numbers": "false",
        "include-verse-spans": "false",
        "use-org-id": "false" # CRITICAL: We want the standard translation mapping to fetch KJV/LSV properly
    }

    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    headers = {
        "api-key": api_key,
        "accept": "application/json",
        "User-Agent": "curl/8.5.0"
    }

    req = urllib.request.Request(full_url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise RuntimeError(f"API returned status {response.status} for {passage_str}")
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.reason} for {passage_str}") from e
    except Exception as e:
        raise RuntimeError(f"Network/Parse Error: {str(e)} for {passage_str}") from e

def build_cache():
    api_key = get_api_key()
    if not api_key:
        print("Skipping cache generation. Provide API key to build it.")
        return

    vids = sorted(list(KNOWN_OMISSIONS))
    print(f"Building omissions cache for {len(vids)} verses...")

    cache = {
        "KJV": {},
        "LSV": {}
    }

    # PARALLEL_IDS[0] is KJV, [1] is LSV
    bible_mappings = [
        ("KJV", PARALLEL_IDS[0]),
        ("LSV", PARALLEL_IDS[1])
    ]

    for version, bible_id in bible_mappings:
        print(f"Fetching bulk passages for {version}...")
        try:
            passages = []
            # API documentation implies comma separation, but the server actively rejects it with 400.
            # We will make individual verse queries. It costs 20 credits per translation, which is minimal for a one-time script.
            for vid in vids:
                print(f"    Fetching {vid}...")
                data = fetch_bulk_passages(api_key, bible_id, [vid])

                chunk_passages = data.get('data', [])
                if isinstance(chunk_passages, dict):
                    chunk_passages = [chunk_passages]
                passages.extend(chunk_passages)

            for passage in passages:
                ref = passage.get('reference')
                content = passage.get('content')

                # We need to map the content back to the specific verseId.
                # The API usually returns `reference` like "Acts 8:37", which is hard to map perfectly back to "ACT.8.37".
                # It's better to extract the `verseId` from the content itself.
                verse_id = None

                # Search the content tree for the verseId
                def find_vid(items):
                    for item in items:
                        if isinstance(item, dict):
                            if 'attrs' in item and 'verseId' in item['attrs']:
                                return item['attrs']['verseId']
                            if 'items' in item:
                                res = find_vid(item['items'])
                                if res: return res
                    return None

                verse_id = find_vid(content)
                if verse_id and verse_id in vids:
                    cache[version][verse_id] = content
                    print(f"  Mapped {verse_id} for {version}")
                else:
                    print(f"  Warning: Could not parse exact verseId for passage block. Ref: {ref}")

        except Exception as e:
            print(f"Failed to fetch {version}: {e}")
            return

    os.makedirs("data", exist_ok=True)
    atomic_write_json("data/omissions_cache.json", cache)
    print("Successfully built data/omissions_cache.json")

if __name__ == "__main__":
    build_cache()
