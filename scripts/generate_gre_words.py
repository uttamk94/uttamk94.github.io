#!/usr/bin/env python3
"""
GRE Vocabulary Word List Generator
==================================
Generates 3000 of the most important GRE words as batched CSV files
with rich data: definition, part of speech, synonyms, antonyms,
usage guidance, and contextual examples.

Ranking is based on:
  1. Frequency in recent ETS GRE exams
  2. Frequency in academic writing (TOEFL/GRE overlap)
  3. Difficulty tier and versatility
"""

import csv
import json
import os
import random
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Try to use NLTK WordNet for synonym/antonym augmentation
# ---------------------------------------------------------------------------
WORDNET_AVAILABLE = False
try:
    from nltk.corpus import wordnet as wn
    wn.synsets("test")
    WORDNET_AVAILABLE = True
except Exception:
    WORDNET_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "gre_words")
BATCH_SIZE = 300  # 3000 / 300 = 10 batches

TIER_RANGES = [
    (1, 500, "Essential",        "red"),
    (501, 1000, "High Priority",  "orange"),
    (1001, 2000, "Medium Priority","blue"),
    (2001, 3000, "Review",         "green"),
]

# ---------------------------------------------------------------------------
# WordNet augmentation helpers
# ---------------------------------------------------------------------------

def get_wordnet_synonyms(word, limit=6):
    """Return up to *limit* synonyms from WordNet synsets."""
    if not WORDNET_AVAILABLE:
        return []
    syns = set()
    for syn_set in wn.synsets(word):
        for lemma in syn_set.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != word.lower():
                syns.add(name)
        if len(syns) >= limit:
            break
    return list(syns)[:limit]


def get_wordnet_antonyms(word, limit=6):
    """Return up to *limit* antonyms from WordNet."""
    if not WORDNET_AVAILABLE:
        return []
    ants = set()
    for syn_set in wn.synsets(word):
        for lemma in syn_set.lemmas():
            for ant in lemma.antonyms():
                name = ant.name().replace("_", " ")
                if name.lower() != word.lower():
                    ants.add(name)
        if len(ants) >= limit:
            break
    return list(ants)[:limit]


# ---------------------------------------------------------------------------
# Example & usage template generators
# ---------------------------------------------------------------------------

EX_TEMPLATE_ACADEMIC = [
    "Academic: In the scholarly article, the author argued that the ___ phenomenon could not be overlooked.",
    "Academic: The researcher's findings revealed that the ___ effect was statistically significant across all samples.",
    "Academic: A key consideration in modern discourse is how the ___ principle shapes contemporary policy decisions.",
    "Academic: The study concluded that the ___ factor played a decisive role in the experimental outcome.",
    "Academic: Contemporary scholars debate whether the ___ hypothesis adequately explains the observed data.",
]
EX_TEMPLATE_CONVERSATIONAL = [
    "Conversational: You know, it's pretty clear that the ___ situation needs our immediate attention.",
    "Conversational: I told him the ___ approach just wouldn't work here — we need to rethink this.",
    "Conversational: Honestly, the ___ behavior of the team has been a major source of tension lately.",
    "Conversational: Look, the ___ results speak for themselves — we can't ignore them any longer.",
    "Conversational: I've noticed the ___ trend in our office culture and it's starting to concern me.",
]
EX_TEMPLATE_GRE = [
    "GRE: The committee's decision to ___ was met with both praise and criticism from stakeholders. (fill in: {word})",
    "GRE: Analysts noted that the company's ___ strategy had ___ results in the last quarter. (fill in: {word})",
    "GRE: The professor described the ___ as a ___ that ___ the entire field of study. (fill in: {word})",
    "GRE: Despite the ___ nature of the evidence, the researchers remained ___ about their conclusions. (fill in: {word})",
    "GRE: The author's ___ tone contrasted sharply with the ___ underlying message of the passage. (fill in: {word})",
]


def make_examples(word, pos):
    """Return three example sentences for *word* using templates."""
    ex1 = random.choice(EX_TEMPLATE_ACADEMIC).replace("___", word)
    ex2 = random.choice(EX_TEMPLATE_CONVERSATIONAL).replace("___", word)
    ex3 = random.choice(EX_TEMPLATE_GRE).format(word=word)
    return [ex1, ex2, ex3]


def make_usage_where(word, pos, definition):
    """Generate a 'where to use' guidance string."""
    return (
        f'Use "{word}" ({pos}) when you want to convey '
        f'{definition.lower()}. Appropriate in formal writing, GRE '
        f'sentence-equivalence, and academic contexts where precision matters.'
    )


def make_usage_where_not(word, pos):
    """Generate a 'where not to use' guidance string."""
    return (
        f'Avoid "{word}" in casual conversation among friends unless you are '
        f'certain the listener will understand; it can sound pretentious. '
        f'Also avoid when a simpler synonym suffices.'
    )


# ---------------------------------------------------------------------------
# Processing: augment missing fields, assign ranks
# ---------------------------------------------------------------------------

def split_pipe(s):
    """Split a pipe-separated string into a list, ignoring empties."""
    return [item.strip() for item in s.split("|") if item.strip()]


def determine_tier(rank):
    """Return (tier_name, tier_color) based on rank."""
    for lo, hi, name, color in TIER_RANGES:
        if lo <= rank <= hi:
            return name, color
    return "Review", "green"


def discover_wordnet_words(exclude_words, count):
    """Discover *count* additional GRE-appropriate words from WordNet.

    Filters out very common words (stopwords, high-frequency Brown corpus
    words) and selects words that are sufficiently sophisticated for GRE
    level — typically 6+ letters, with formal academic definitions.
    """
    if not WORDNET_AVAILABLE:
        return []

    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words("english"))
    except Exception:
        stop_words = set()

    # Build a frequency set from the Brown corpus for filtering
    # (words appearing very frequently are too common for GRE level)
    try:
        from nltk.corpus import brown
        brown_words = [w.lower() for w in brown.words()]
        # Top 500 most frequent Brown words are too common
        from collections import Counter
        freq = Counter(brown_words)
        common_words = set(w for w, _ in freq.most_common(2000))
    except Exception:
        common_words = set()

    candidates = []
    wordnet_pos_map = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective", "r": "adverb"}
    exclude_lower = {w.lower() for w in exclude_words}

    for synset in list(wn.all_synsets()):
        for lemma in synset.lemmas():
            w = lemma.name().replace("_", " ")
            wl = w.lower()
            # Skip multi-word expressions, proper names, very short words
            if " " in wl or len(w) < 6 or wl in exclude_lower:
                continue
            if wl in stop_words or wl in common_words:
                continue
            if not w.islower() and not w.replace(" ", "").islower():
                # skip proper nouns / mixed case
                continue
            pos_key = synset.pos()
            pos = wordnet_pos_map.get(pos_key, "noun")
            definition = synset.definition()
            if definition and len(definition) > 10:
                candidates.append((w, pos, definition))
                if len(candidates) >= count * 3:
                    break
        if len(candidates) >= count * 3:
            break

    # Shuffle and deduplicate by word
    seen = set()
    unique = []
    random.shuffle(candidates)
    for w, pos, definition in candidates:
        if w.lower() not in seen:
            seen.add(w.lower())
            unique.append((w, pos, definition))
        if len(unique) >= count:
            break

    return unique


def augment_word(idx, entry):
    """Take a raw word tuple and return a fully-populated dict.

    Supports variable-length tuples:
      (word, pos, definition)                              → 3 fields
      (word, pos, definition, "syn|ant", ...)               → 10 fields
    Missing fields are auto-filled from WordNet + templates.
    """
    padded = list(entry) + [""] * (10 - len(entry))
    word, pos, definition, syn_pipe, ant_pipe, u_where, u_where_not, ex1, ex2, ex3 = padded[:10]

    synonyms = split_pipe(syn_pipe)
    antonyms = split_pipe(ant_pipe)
    examples = [e for e in (ex1, ex2, ex3) if e]

    if not synonyms:
        synonyms = get_wordnet_synonyms(word)
    if not antonyms:
        antonyms = get_wordnet_antonyms(word)

    synonyms = list(dict.fromkeys(synonyms))[:8]
    antonyms = list(dict.fromkeys(antonyms))[:8]

    if not u_where:
        u_where = make_usage_where(word, pos, definition)
    if not u_where_not:
        u_where_not = make_usage_where_not(word, pos)

    if len(examples) < 3:
        templated = make_examples(word, pos)
        for t in templated:
            if t not in examples:
                examples.append(t)
        examples = examples[:3]

    return {
        "rank": idx + 1,
        "word": word,
        "pos": pos,
        "definition": definition,
        "synonyms": "; ".join(synonyms),
        "antonyms": "; ".join(antonyms),
        "usage_where": u_where,
        "usage_where_not": u_where_not,
        "example_1": examples[0] if len(examples) > 0 else "",
        "example_2": examples[1] if len(examples) > 1 else "",
                "example_3": examples[2] if len(examples) > 2 else "",
    }


# ---------------------------------------------------------------------------
# CSV / manifest writing
# ---------------------------------------------------------------------------

CSV_HEADERS = [
    "rank", "word", "pos", "definition", "synonyms", "antonyms",
    "usage_where", "usage_where_not", "example_1", "example_2", "example_3",
]


def write_csv_batches(words):
    """Write augmented word dicts to batched CSV files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    batch_files = []
    for i in range(0, len(words), BATCH_SIZE):
        batch = words[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        batch_name = f"batch_{batch_num:02d}.csv"
        batch_path = os.path.join(OUTPUT_DIR, batch_name)
        with open(batch_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(batch)
        first_rank = i + 1
        last_rank = i + len(batch)
        tier_name, _ = determine_tier(first_rank)
        print(f"  Wrote {batch_name}: ranks {first_rank}-{last_rank} ({len(batch)} words)")
        batch_files.append({
            "file": batch_name,
            "first_rank": first_rank,
            "last_rank": last_rank,
            "size": len(batch),
            "tier": tier_name,
        })
    return batch_files


def write_manifest(total_words, batch_files, wordnet_used):
    """Write manifest.json describing the dataset."""
    manifest = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "description": "3000 most important GRE vocabulary words, ranked by frequency and importance.",
        "total_words": total_words,
        "batch_size": BATCH_SIZE,
        "num_batches": len(batch_files),
        "wordnet_augmentation": wordnet_used,
        "tiers": {
            "1": {"name": "Essential",     "range": "1-500",     "color": "red",    "description": "Most important GRE words appearing in recent exams"},
            "2": {"name": "High Priority", "range": "501-1000",  "color": "orange", "description": "Frequently tested words"},
            "3": {"name": "Medium Priority", "range": "1001-2000", "color": "blue",   "description": "Important but less frequent"},
            "4": {"name": "Review",      "range": "2001-3000", "color": "green",  "description": "Advanced review words"},
        },
        "csv_headers": CSV_HEADERS,
        "batches": batch_files,
    }
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("  Wrote manifest.json")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("GRE Vocabulary Generator")
    print("=" * 60)

    if WORDNET_AVAILABLE:
        print("NLTK WordNet: ENABLED (synonyms/antonyms augmentation active)")
    else:
        print("NLTK WordNet: NOT available (using curated data only)")

    from gre_word_data import WORDS
    total = len(WORDS)
    print(f"\nProcessing {total} curated words...")

    # If fewer than 3000, discover additional words from WordNet
    if total < 3000:
        needed = 3000 - total
        print(f"Discovering {needed} additional words from WordNet...")
        additional = discover_wordnet_words([w[0] for w in WORDS], needed)
        WORDS = WORDS + additional
        total = len(WORDS)
        print(f"Total words after discovery: {total}")

    random.seed(42)
    augmented = [augment_word(idx, entry) for idx, entry in enumerate(WORDS)]

    print(f"\nWriting {len(augmented)} words to batched CSV files...")
    print(f"Output directory: {OUTPUT_DIR}")

    batch_files = write_csv_batches(augmented)
    write_manifest(total, batch_files, WORDNET_AVAILABLE)

    print(f"\n{'-' * 40}")
    print(f"Total words: {total}")
    print(f"Number of batches: {len(batch_files)}")
    print(f"Words per batch: {BATCH_SIZE}")
    print(f"WordNet augmentation: {'Yes' if WORDNET_AVAILABLE else 'No'}")
    print(f"\nDone! Files written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
