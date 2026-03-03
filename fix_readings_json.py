import json
import os

if os.path.exists('data/readings.json'):
    with open('data/readings.json', 'r') as f:
        readings = json.load(f)

    for day in readings:
        if 'api_format' in day:
            day['api_format'] = day['api_format'].replace('SON', 'SNG')
            day['api_format'] = day['api_format'].replace('JOE', 'JOL')
            day['api_format'] = day['api_format'].replace('NAH', 'NAM')

    with open('data/readings.json', 'w') as f:
        json.dump(readings, f, indent=4)
    print("Updated data/readings.json")
else:
    print("data/readings.json not found locally. Skipping.")
