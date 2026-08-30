import re

with open('scripts/algo_content.py', 'rb') as f:
    raw = f.read()

lines = raw.split(b'\n')

# Check KNAPSACK_PY content (lines 7729-7760) for any ' characters
print("=== Checking KNAPSACK_PY content for single quotes ===")
for i in range(7728, 7761):
    line = lines[i]
    if b"'" in line:
        for m in re.finditer(b"'", line):
            context = line[max(0,m.start()-15):m.end()+15]
            print(f'Line {i+1}, col {m.start()}: {context!r}')

print("\n=== Checking COIN_CHANGE_C content (7877-7915) for single quotes ===")
for i in range(7876, 7916):
    line = lines[i]
    if b"'" in line:
        for m in re.finditer(b"'", line):
            context = line[max(0,m.start()-15):m.end()+15]
            print(f'Line {i+1}, col {m.start()}: {context!r}')

print("\n=== Checking for non-ASCII bytes in region 7728-7916 ===")
for i in range(7727, 7916):
    line = lines[i]
    for j, b in enumerate(line):
        if b > 127:
            print(f'Line {i+1}, col {j}: byte 0x{b:02x}')
