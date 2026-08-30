#!/usr/bin/env python3
"""Simulate Python's tokenizer to find where string state goes wrong."""

with open('scripts/algo_content.py', 'r') as f:
    lines = f.readlines()

# State: are we inside a triple-quoted string? If so, which delimiter?
in_triple = None  # None, "'''", '"""'

for i, line in enumerate(lines):
    lineno = i + 1
    if lineno < 7720 or lineno > 7920:
        continue
    
    # Process character by character
    j = 0
    while j < len(line):
        ch = line[j]
        if in_triple is None:
            # Check for triple quote openers (with optional prefix)
            if line[j:j+3] in ("'''", '"""'):
                in_triple = line[j:j+3]
                print(f"L{lineno}: OPEN {in_triple!r} at col {j}")
                j += 3
                continue
            # Check for single/double quote start (non-triple)
            elif ch in ("'", '"'):
                quote = ch
                j += 1
                # Read until closing quote or end of line
                found_close = False
                while j < len(line):
                    if line[j] == '\\':
                        j += 2
                        continue
                    if line[j] == quote:
                        j += 1
                        found_close = True
                        break
                    j += 1
                if not found_close:
                    print(f"L{lineno}: ERROR - unterminated string starting at col {j-1}")
                    print(f"    Line: {line.rstrip()[:100]}")
                    raise SystemExit(1)
                continue
        else:
            # We're inside a triple-quoted string
            if line[j:j+3] == in_triple:
                print(f"L{lineno}: CLOSE {in_triple!r} at col {j}")
                in_triple = None
                j += 3
                continue
        j += 1

print(f"\nAt line 7920: in_triple = {in_triple!r}")
