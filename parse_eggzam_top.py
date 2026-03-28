import sys

def extract_class_top(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    start_line = -1
    for i, line in enumerate(lines):
        if 'class EggZamRoom ' in line:
            start_line = i
            break

    if start_line != -1:
        return "".join(lines[start_line:start_line+200])
    return ""

print("--- main.js EggZamRoom Top ---")
print(extract_class_top("apps/HeIsRisen/main.js"))
print("--- m/main.js EggZamRoom Top ---")
print(extract_class_top("apps/HeIsRisen/m/main.js"))
