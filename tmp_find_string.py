#!/usr/bin/env python3
"""Find unterminated triple-quoted strings in algo_content.py."""
lines = open('scripts/algo_content.py').readlines()
in_string = False
string_start = None
for i, line in enumerate(lines, 1):
    if not in_string:
        if "r'''" in line or 'r"""' in line:
            in_string = True
            string_start = i
    else:
        if "'''" in line or '"""' in line:
            in_string = False
if in_string:
    print(f'Unterminated string starting at line {string_start}')
    print('Context:')
    for j in range(max(0, string_start - 3), min(len(lines), string_start + 5)):
        print(f'  {j + 1}: {lines[j].rstrip()}')
else:
    print('All strings terminated')
