import requests
import datetime
from zoneinfo import ZoneInfo
import sys

def test_production_data_future():
    """
    Test that the 365DBR production data for Today + 2 Days exists and is well-formed JSON.
    This ensures that we are testing real data and catching issues before they hit production.
    """
    # Calculate Today + 2 days in MST/MDT
    tz = ZoneInfo("America/Denver")
    today = datetime.datetime.now(tz)
    target_date = today + datetime.timedelta(days=2)

    # Format as MMDD (e.g., 0321)
    day_id = target_date.strftime("%m%d")

    base_url = f"https://mt-sin.ai/365DBR/data/{day_id}/manifest.json"
    print(f"Testing production data for: {day_id} (URL: {base_url})")

    try:
        response = requests.get(base_url, timeout=10)

        # 1. Verify the manifest exists
        if response.status_code != 200:
            print(f"ERROR: Production manifest for {day_id} returned status {response.status_code}")
            sys.exit(1)

        # 2. Verify it is valid JSON
        try:
            manifest_data = response.json()
        except ValueError:
            print(f"ERROR: Production manifest for {day_id} is not valid JSON.")
            sys.exit(1)

        # 3. Verify it contains a list of files
        files = manifest_data.get('files', [])
        if not files:
            print(f"ERROR: Production manifest for {day_id} contains no files. Data is missing/corrupted.")
            sys.exit(1)

        print(f"SUCCESS: Manifest for {day_id} is valid and lists {len(files)} files.")

        # 4. Briefly verify the first file exists and is valid JSON to ensure deep integrity
        first_file = files[0]
        file_url = f"https://mt-sin.ai/365DBR/data/{day_id}/{first_file}"
        print(f"Testing deep integrity on first file: {file_url}")

        file_response = requests.get(file_url, timeout=10)
        if file_response.status_code != 200:
            print(f"ERROR: Production data file {first_file} for {day_id} returned status {file_response.status_code}")
            sys.exit(1)

        try:
            file_data = file_response.json()
            if 'data' not in file_data or 'content' not in file_data['data']:
                print(f"ERROR: Production data file {first_file} lacks 'data.content' structure.")
                sys.exit(1)
            print(f"SUCCESS: Production data file {first_file} is valid.")
        except ValueError:
            print(f"ERROR: Production data file {first_file} for {day_id} is not valid JSON.")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network failure when accessing production data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_production_data_future()
