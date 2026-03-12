import os
import urllib.request
import json

base_url = "https://mt-sin.ai/365DBR/data"
days = ["0102", "0307", "0415"]

for day in days:
    os.makedirs(f"data/{day}", exist_ok=True)
    manifest_url = f"{base_url}/{day}/manifest.json"
    manifest_path = f"data/{day}/manifest.json"

    print(f"Downloading {manifest_url}")
    try:
        urllib.request.urlretrieve(manifest_url, manifest_path)

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        for file in manifest.get('files', []):
            file_url = f"{base_url}/{day}/{file}"
            file_path = f"data/{day}/{file}"
            print(f"  Downloading {file_url}")
            urllib.request.urlretrieve(file_url, file_path)
    except Exception as e:
        print(f"Error downloading {day}: {e}")
