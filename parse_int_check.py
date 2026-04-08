import re

files_to_check = ['apps/365DBR/index.html', 'apps/365DBR/bible.html']

for file in files_to_check:
    print(f"Checking {file}:")
    with open(file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if 'parseInt(' in line and '10' not in line:
                print(f"Line {i+1}: {line.strip()}")
