#!/usr/bin/env python3
"""Cross-check that every element id referenced via $('...') in gre_verbal.js
exists as an id= attribute in gre_verbal_test.html."""

import re

JS = "/home/uttam/uttam/projects/site/uttamk94.github.io/assets/js/gre_verbal.js"
HTML = "/home/uttam/uttam/projects/site/uttamk94.github.io/pages/gre_verbal_test.html"

js = open(JS, encoding="utf-8").read()
html = open(HTML, encoding="utf-8").read()

used = set(re.findall(r"\$\('([^']+)'\)", js))
defined = set(re.findall(r'id="([^"]+)"', html))

# ids created dynamically by JS at runtime are fine too
dynamic = set(re.findall(r"\.id\s*=\s*`?([A-Za-z-]+)", js))

missing = sorted(u for u in used if u not in defined)
print("ids referenced in JS:", len(used))
print("missing from HTML:", missing if missing else "NONE - all present")

# reverse check: ids defined but never referenced (informational)
unused = sorted(d for d in defined if d not in used)
print("ids defined but not referenced:", unused if unused else "none")
