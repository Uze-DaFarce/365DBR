import sys

def extract_class(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    start_line = -1
    end_line = -1
    brace_count = 0
    in_class = False

    for i, line in enumerate(lines):
        if 'class EggZamRoom ' in line:
            start_line = i
            in_class = True
            brace_count = line.count('{') - line.count('}')
            continue

        if in_class:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                end_line = i
                break

    if start_line != -1 and end_line != -1:
        return "".join(lines[start_line:end_line+1])
    return ""

print("--- main.js EggZamRoom ---")
print(extract_class("apps/HeIsRisen/main.js"))
print("--- m/main.js EggZamRoom ---")
print(extract_class("apps/HeIsRisen/m/main.js"))
