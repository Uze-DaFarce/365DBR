with open('./apps/HeIsRisen/m/main.js', 'r') as f:
    lines = f.readlines()

with open('./apps/HeIsRisen/m/main.js', 'w') as f:
    for line in lines:
        if "backgroundColor: '#000000'," in line:
            continue
        f.write(line)
