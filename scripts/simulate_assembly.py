#!/usr/bin/env python3
"""Simulate the browser's test assembly logic against the real question bank.

Mirrors assembleTest() / pickRcPassages() from assets/js/gre_verbal.js so we can
verify offline (without Node.js) that every mock contains exactly 20 questions:
3 single-blank TC + 2 double + 1 triple + 4 SE + 10 RC questions.
"""

import itertools
import json
import random

BANK = "/home/uttam/uttam/projects/site/uttamk94.github.io/data/gre_verbal/questions.json"

with open(BANK, encoding="utf-8") as f:
    bank = json.load(f)

cfg = bank["test_config"]["composition"]
tc = bank["text_completion"]
se = bank["sentence_equivalence"]
rc = bank["reading_comprehension"]


def pick_n(items, n):
    return random.sample(items, min(n, len(items)))


def pick_rc_passages(passages, target):
    for k in range(min(3, len(passages)), 0, -1):
        for combo in itertools.combinations(passages, k):
            if sum(len(p["questions"]) for p in combo) == target:
                return list(combo)
    chosen, total = [], 0
    for p in sorted(passages, key=lambda x: -len(x["questions"])):
        if total >= target:
            break
        chosen.append(p)
        total += len(p["questions"])
    excess = total - target
    while excess > 0 and chosen:
        last = chosen[-1]
        if len(last["questions"]) > excess:
            last = dict(last)
            last["questions"] = last["questions"][:-excess]
            chosen[-1] = last
            excess = 0
        else:
            excess -= len(last["questions"])
            chosen.pop()
    return chosen


runs = []
ok = True
for trial in range(500):
    singles = pick_n([q for q in tc if q["blanks"] == 1], cfg["text_completion_single"])
    doubles = pick_n([q for q in tc if q["blanks"] == 2], cfg["text_completion_double"])
    triples = pick_n([q for q in tc if q["blanks"] == 3], cfg["text_completion_triple"])
    sel_tc = singles + doubles + triples
    sel_se = pick_n(se, cfg["sentence_equivalence"])
    passages = pick_rc_passages(rc, cfg["reading_comprehension_questions"])
    rc_qs = [q for p in passages for q in p["questions"]]
    total = len(sel_tc) + len(sel_se) + len(rc_qs)

    # uniqueness of ids within the assembled test
    ids = [q["id"] for q in sel_tc] + [q["id"] for q in sel_se] + [q["id"] for q in rc_qs]
    if total != 20 or len(ids) != len(set(ids)):
        ok = False
        print(f"trial {trial}: total={total} unique_ids={len(ids)}")
        break
    runs.append((
        len(singles), len(doubles), len(triples), len(sel_se),
        tuple(sorted(len(p["questions"]) for p in passages)),
    ))

from collections import Counter
print("all 500 trials OK: exactly 20 questions, no duplicate ids" if ok else "FAILED")
print("composition variants seen:", Counter(runs))
