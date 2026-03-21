with open('apps/HeIsRisen/tests/test_collect_eggs.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "page.screenshot(path=f\"verification/{'mobile' if is_mobile else 'desktop'}_collect_success.png\")" in line:
        lines[i] = "                page.screenshot(path=f\"verification/{'mobile' if is_mobile else 'desktop'}_collect_success.png\")\n"
        lines[i+1] = "                print(\"SUCCESS: 'Great Job Detective' message found!\")\n"
    if "page.screenshot(path=f\"verification/{'mobile' if is_mobile else 'desktop'}_collect_fail.png\")" in line:
        lines[i] = "                page.screenshot(path=f\"verification/{'mobile' if is_mobile else 'desktop'}_collect_fail.png\")\n"
        lines[i+1] = "                print(\"FAIL: \" + str(len(eggs)) + \" eggs were not collected!\")\n"

with open('apps/HeIsRisen/tests/test_collect_eggs.py', 'w') as f:
    f.writelines(lines)
