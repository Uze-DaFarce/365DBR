import sys

def extract_bottom(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    start_line = -1
    for i, line in enumerate(lines):
        if 'showExplanation =' in line:
            start_line = i
            break

    if start_line != -1:
        return "".join(lines[start_line:start_line+200])
    return ""

print("--- m/main.js showExplanation ---")
print(extract_bottom("apps/HeIsRisen/m/main.js"))
