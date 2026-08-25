#!/usr/bin/env python3
"""Build a single all_words.json from all CSV batch files."""

import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "gre_words")
OUTPUT_FILE = os.path.join(DATA_DIR, "all_words.json")

CSV_HEADERS = [
    "rank", "word", "pos", "definition", "synonyms", "antonyms",
    "usage_where", "usage_where_not", "example_1", "example_2", "example_3",
]

# Tier configuration matching the generator
TIERS = [
    (1, 500, "Essential", "red"),
    (501, 1000, "High Priority", "orange"),
    (1001, 2000, "Medium Priority", "blue"),
    (2001, 3000, "Review", "green"),
]


def get_tier(rank):
    for lo, hi, name, color in TIERS:
        if lo <= rank <= hi:
            return name, color
    return "Review", "green"


def main():
    all_words = []
    for i in range(1, 11):
        csv_path = os.path.join(DATA_DIR, f"batch_{i:02d}.csv")
        if not os.path.exists(csv_path):
            continue
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rank = int(row["rank"])
                tier_name, tier_color = get_tier(rank)
                word_entry = {
                    "rank": rank,
                    "word": row["word"],
                    "pos": row["pos"],
                    "definition": row["definition"],
                    "synonyms": row["synonyms"],
                    "antonyms": row["antonyms"],
                    "usage_where": row["usage_where"],
                    "usage_where_not": row["usage_where_not"],
                    "example_1": row["example_1"],
                    "example_2": row["example_2"],
                    "example_3": row["example_3"],
                    "tier": tier_name,
                    "tier_color": tier_color,
                }
                all_words.append(word_entry)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=0)

    print(f"Built all_words.json with {len(all_words)} words")
    print(f"Output: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE)} bytes")


if __name__ == "__main__":
    main()
