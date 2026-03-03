import re
import os

files_to_check = ['bible_common.py', 'generate_readings.py', 'fetch_readings.py', 'check_data_integrity.py', 'generate_january.py']

for file in files_to_check:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()

        # Update references in python lists/dicts
        content = content.replace('"SON"', '"SNG"')
        content = content.replace("'SON'", "'SNG'")

        content = content.replace('"JOE"', '"JOL"')
        content = content.replace("'JOE'", "'JOL'")

        content = content.replace('"NAH"', '"NAM"')
        content = content.replace("'NAH'", "'NAM'")

        with open(file, 'w') as f:
            f.write(content)
        print(f"Updated {file}")
