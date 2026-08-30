#!/usr/bin/env python3
"""Check brace/paren/bracket balance in a JS file (no Node.js available).
Usage: python3 scripts/check_js_balance_single.py <path>"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "assets/js/algo_sim.js"
src = open(path, encoding="utf-8").read()
s = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
s = re.sub(r"//[^\n]*", "", s)
s = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", s)
s = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', s)
s = re.sub(r"`(?:\\.|[^`])*`", "``", s, flags=re.S)
counts = {c: s.count(c) for c in "{}()[]"}
ok = counts["{"] == counts["}"] and counts["("] == counts[")"] and counts["["] == counts["]"]
print(path, counts, "BALANCED" if ok else "IMBALANCED")
sys.exit(0 if ok else 1)
