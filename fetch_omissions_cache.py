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

def fetch_single_passage(api_key, bible_id, vid):
    url = f"{API_BASE_URL}/bibles/{bible_id}/passages/{vid}"

    params = {
        "content-type": "json",
        "include-notes": "false",
        "include-titles": "false",
        "include-chapter-numbers": "false",
        "include-verse-numbers": "false",
        "include-verse-spans": "false",
        "use-org-id": "false"
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
                raise RuntimeError(f"API returned status {response.status} for {vid}")
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.reason} for {vid}") from e
    except Exception as e:
        raise RuntimeError(f"Network/Parse Error: {str(e)} for {vid}") from e

def build_cache():
    api_key = get_api_key()
    if not api_key:
        print("Skipping cache generation. Provide API key to build it.")
        return

    vids = sorted(list(KNOWN_OMISSIONS))
    print(f"Checking omissions cache for {len(vids)} verses...")

    os.makedirs("data", exist_ok=True)
    cache_path = "data/omissions_cache.json"

    # Load existing cache to prevent redundant API calls
    cache = {
        "KJV": {},
        "LSV": {}
    }
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if "KJV" in loaded: cache["KJV"] = loaded["KJV"]
                if "LSV" in loaded: cache["LSV"] = loaded["LSV"]
            print("Loaded existing cache from disk.")
        except Exception as e:
            print(f"Could not load existing cache: {e}")

    bible_mappings = [
        ("KJV", PARALLEL_IDS[0]),
        ("LSV", PARALLEL_IDS[1])
    ]

    # Map API-missing coordinates (e.g. Greek structure) to where they actually live in KJV/LSV
    api_fetch_map = {
        "ROM.14.24": "ROM.16.25",
        "ROM.14.25": "ROM.16.26",
        "ROM.14.26": "ROM.16.27"
    }

    for version, bible_id in bible_mappings:
        print(f"\nProcessing {version}...")
        for vid in vids:
            if vid in cache[version]:
                print(f"  [Skip] {vid} already cached for {version}.")
                continue

            fetch_vid = api_fetch_map.get(vid, vid)

            print(f"  [Fetch] Requesting {vid} (via {fetch_vid}) for {version}...")
            try:
                data = fetch_single_passage(api_key, bible_id, fetch_vid)
                passage = data.get('data', {})
                fetched_content = passage.get('content', [])

                if fetched_content:
                    cache[version][vid] = fetched_content
                    # Save incrementally
                    atomic_write_json(cache_path, cache)
                    print(f"    -> Saved {vid}")
                else:
                    print(f"    -> Warning: Empty content returned for {vid} (via {fetch_vid})")

            except Exception as e:
                print(f"    -> [Error] Failed to fetch {vid} (via {fetch_vid}): {e}")
                # We do NOT break here. We continue to the next verse.
                continue

    print("\nFinished checking and building data/omissions_cache.json")

if __name__ == "__main__":
    build_cache()
