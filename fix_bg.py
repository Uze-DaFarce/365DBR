with open('./apps/HeIsRisen/m/main.js', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "backgroundColor: '#000000'," in line:
        continue
    new_lines.append(line)

with open('./apps/HeIsRisen/m/main.js', 'w') as f:
    f.writelines(new_lines)
