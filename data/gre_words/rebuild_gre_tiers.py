# -*- coding: utf-8 -*-
"""
Rebuild honest GRE tiers for all_words.json.

Strategy (per user request: "Add missing classic GRE words + fix tiers of
existing ones, keep everything else"):
  1. ESSENTIAL      -> curated canonical core list, in listed order.
                       Existing entries are PROMOTED with their rich fields kept;
                       missing words are ADDED using the dataset's template style.
  2. HIGH_PRIORITY  -> second curated band, treated the same way.
  3. All remaining original words keep their content untouched but are re-tiered
     into Medium Priority (next ~1000) and Review (the rest), preserving their
     previous relative rank order.
Ranks are then renumbered sequentially. A timestamped backup of the original
file is written first.
"""

import json
import shutil
import sys
from collections import Counter

from gre_core_list import ESSENTIAL, HIGH_PRIORITY

SRC = "all_words.json"
BACKUP = "all_words.backup.json"

TIER_COLOR = {
    "Essential": "red",
    "High Priority": "orange",
    "Medium Priority": "blue",
    "Review": "green",
}

REQUIRED_FIELDS = [
    "rank", "word", "pos", "definition", "synonyms", "antonyms",
    "usage_where", "usage_where_not", "example_1", "example_2",
    "example_3", "tier", "tier_color",
]


def make_entry(word, pos, definition, synonyms, antonyms):
    """Create a new entry using the same template style as existing data."""
    defn = definition[0].lower() + definition[1:] if definition else ""
    return {
        "rank": 0,
        "word": word,
        "pos": pos,
        "definition": definition,
        "synonyms": synonyms,
        "antonyms": antonyms,
        "usage_where": (
            f'Use "{word}" ({pos}) when you want to convey {defn}. '
            "Appropriate in formal writing, GRE sentence-equivalence, and "
            "academic contexts where precision matters."
        ),
        "usage_where_not": (
            f'Avoid "{word}" in casual conversation among friends unless you '
            "are certain the listener will understand; it can sound "
            "pretentious. Also avoid when a simpler synonym suffices."
        ),
        "example_1": (
            f"Academic: In the scholarly article, the author argued that the "
            f"{word} phenomenon could not be overlooked."
        ),
        "example_2": (
            f"Conversational: You know, it's pretty clear that the {word} "
            f"situation needs our immediate attention."
        ),
        "example_3": (
            f"GRE: The professor described the ___ as a ___ that ___ the "
            f"entire field of study. (fill in: {word})"
        ),
        "tier": "",
        "tier_color": "",
    }


def main():
    # --- Load & backup ---
    with open(SRC) as fh:
        data = json.load(fh)
    shutil.copyfile(SRC, BACKUP)
    print(f"Loaded {len(data)} words; backup saved to {BACKUP}")

    by_word = {}
    for w in data:
        key = w["word"].strip().lower()
        if key in by_word:
            print(f"WARNING: duplicate word in source data: {w['word']}")
        by_word[key] = w

    final = []
    seen = set()

    def apply_curated(curated, tier):
        added = promoted = 0
        for word, pos, definition, syn, ant in curated:
            key = word.strip().lower()
            if key in seen:
                continue
            if pos not in ("noun", "verb", "adjective", "adverb"):
                sys.exit(f"BAD POS for '{word}': {pos}")
            seen.add(key)
            existing = by_word.get(key)
            if existing is not None:
                entry = dict(existing)          # keep all rich fields
                promoted += 1
            else:
                entry = make_entry(word, pos, definition, syn, ant)
                added += 1
            entry["tier"] = tier
            entry["tier_color"] = TIER_COLOR[tier]
            final.append(entry)
        print(f"{tier}: {len(curated)} curated -> {promoted} promoted, {added} newly added")

    apply_curated(ESSENTIAL, "Essential")
    apply_curated(HIGH_PRIORITY, "High Priority")

    # --- Remaining original words: Medium (~1000), rest Review ---
    rest = [w for w in sorted(data, key=lambda x: x["rank"])
            if w["word"].strip().lower() not in seen]
    medium_n = min(1000, len(rest))
    for w in rest[:medium_n]:
        e = dict(w)
        e["tier"], e["tier_color"] = "Medium Priority", TIER_COLOR["Medium Priority"]
        final.append(e)
    for w in rest[medium_n:]:
        e = dict(w)
        e["tier"], e["tier_color"] = "Review", TIER_COLOR["Review"]
        final.append(e)
    print(f"Remaining originals: {len(rest)} -> Medium {medium_n}, Review {len(rest)-medium_n}")

    # --- Renumber ranks ---
    for i, entry in enumerate(final):
        entry["rank"] = i + 1

    # --- Validate ---
    assert len(final) == len({e["word"].strip().lower() for e in final}), "duplicate words!"
    for e in final:
        missing = [f for f in REQUIRED_FIELDS if f not in e]
        if missing:
            sys.exit(f"'{e['word']}' missing fields: {missing}")
    tiers = Counter(e["tier"] for e in final)
    letters = sorted({e["word"][0].upper() for e in final if e["tier"] == "Essential"})
    print(f"\nTotal: {len(final)} words")
    print("Tier counts:", dict(tiers))
    print(f"Essential covers {len(letters)} letters: {''.join(letters)}")

    # --- Write ---
    with open(SRC, "w") as fh:
        json.dump(final, fh, indent=1)
        fh.write("\n")
    print(f"\nWrote {SRC} ({len(final)} words).")


if __name__ == "__main__":
    main()
