import sys

def extract_class_middle(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    start_line = -1
    for i, line in enumerate(lines):
        if 'class EggZamRoom ' in line:
            start_line = i
            break

    if start_line != -1:
        return "".join(lines[start_line+200:start_line+400])
    return ""

print("--- main.js EggZamRoom Middle ---")
print(extract_class_middle("apps/HeIsRisen/main.js"))
print("--- m/main.js EggZamRoom Middle ---")
print(extract_class_middle("apps/HeIsRisen/m/main.js"))
