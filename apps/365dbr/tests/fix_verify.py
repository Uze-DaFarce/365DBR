with open('/home/jules/verification/verify_breakpoints.py', 'r') as f:
    content = f.read()

# Make the mock manifest valid for loadDailyBread
# It expects `manifest.files` and `json.data` inside the individual files.
mock_data = '''
        mock_manifest = {
            "files": ["GEN.1.1.json"],
            "days": {"0304": {"translations": ["lsv", "kjv"]}}
        }
        mock_file = {
            "data": {
                "GEN.1.1": {
                    "lsv": {"text": ["In the beginning"], "displayVid": "GEN.1.1"},
                    "kjv": {"text": ["In the beginning God created"], "displayVid": "GEN.1.1"},
                    "original": {"text": ["בְּרֵאשִׁ֖ית"], "displayVid": "GEN.1.1"}
                }
            }
        }

        def route_handler(route):
            url = route.request.url
            if "manifest.json" in url:
                route.fulfill(status=200, json=mock_manifest)
            elif "GEN.1.1.json" in url:
                route.fulfill(status=200, json=mock_file)
            else:
                route.continue_()
'''

content = content.replace('''        # Mock data to prevent loading hangs
        mock_data = {
            "0304": {
                "verseMap": {"GEN.1.1": {"lsv": {"text": "In the beginning", "displayVid": "GEN.1.1"}}},
                "readingTime": 1,
                "label": "Day 63",
                "availableTranslations": ["lsv", "kjv"]
            }
        }

        def route_handler(route):
            url = route.request.url
            if "manifest.json" in url:
                route.fulfill(status=200, body='{"days":{"0304":{"translations":["lsv","kjv"]}}}')
            elif "data" in url and "json" in url:
                route.fulfill(status=200, json=mock_data["0304"])
            else:
                route.continue_()''', mock_data)

with open('/home/jules/verification/verify_breakpoints.py', 'w') as f:
    f.write(content)
