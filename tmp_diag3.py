with open('scripts/algo_content.py', 'rb') as f:
    raw = f.read()

lines = raw.split(b'\n')

# Show raw bytes around the critical delimiters
for lineno in [7728, 7760, 7761, 7762, 7875, 7876, 7877, 7915, 7916, 7917]:
    idx = lineno - 1
    line = lines[idx]
    print(f"Line {lineno}: {line!r}")
    print(f"  bytes: {line.hex(' ')}")
    print()
