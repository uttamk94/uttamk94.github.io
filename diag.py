#!/usr/bin/env python3
import sys
path = sys.argv[1] if len(sys.argv) > 1 else 'scripts/algo_content.py'
lines = open(path).readlines()
b = 0
for i, l in enumerate(lines):
    c = l.count("'''") + l.count('"""')
    if c:
        b += c
    if b % 2:
        print("ODD", i+1, l.rstrip()[:100])
print("final balance:", b)
