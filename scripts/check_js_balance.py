#!/usr/bin/env python3
"""Rough structural sanity check for gre_verbal.js (no Node.js available).

Strips comments and string/template literals, then verifies that braces,
parentheses and brackets are balanced. Not a full parser, but catches gross
structural breakage.
"""

import re

JS_PATH = "/home/uttam/uttam/projects/site/uttamk94.github.io/assets/js/gre_verbal.js"

src = open(JS_PATH, encoding="utf-8").read()
s = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
s = re.sub(r"//[^\n]*", "", s)
s = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", s)
s = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', s)
s = re.sub(r"`(?:\\.|[^`])*`", "``", s, flags=re.S)

counts = {c: s.count(c) for c in "{}()[]"}
balanced = (
    counts["{"] == counts["}"]
    and counts["("] == counts[")"]
    and counts["["] == counts["]"]
)
print(counts)
print("BALANCED" if balanced else "IMBALANCED")
print("lines:", src.count("\n") + 1)
