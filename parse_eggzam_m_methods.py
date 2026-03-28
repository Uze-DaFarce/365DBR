import sys

def extract_methods(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if 'class EggZamRoom ' in line:
            start_line = i
            break

    if start_line != -1:
        return "".join(lines[start_line:start_line+150])
    return ""

print("--- m/main.js EggZamRoom Methods ---")
print(extract_methods("apps/HeIsRisen/m/main.js"))
