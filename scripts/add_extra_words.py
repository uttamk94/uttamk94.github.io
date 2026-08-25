"""Append additional GRE words from a text data file into gre_word_data.py.

Text file format (one per line): word|pos|definition
"""
import ast
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "gre_word_data.py")
EXTRA_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "gre_words", "extra_words.txt")


def load_existing(content):
    existing = set()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "WORDS":
                    for elt in node.value.elts:
                        existing.add(str(elt.elts[0].value).lower())
    return existing


with open(DATA_FILE, "r", encoding="utf-8") as f:
    content = f.read()

existing = load_existing(content)
print(f"Existing unique words: {len(existing)}")

# Insertion point: just before the closing ']' of the WORDS list
insert_at = content.rfind("]")
if insert_at == -1:
    raise SystemExit("ERROR: could not find closing ']'")

new_entries = []
dupes = malformed = 0

with open(EXTRA_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3 or not parts[0]:
            malformed += 1
            continue
        word = parts[0].strip('"')
        pos = parts[1].strip('"') or "noun"
        definition = "|".join(parts[2:]).strip().strip('"').replace('"', "'")
        key = word.lower()
        if not word or not definition:
            malformed += 1
            continue
        if key in existing:
            dupes += 1
            continue
        existing.add(key)
        new_entries.append(f'    ("{word}", "{pos}", "{definition}"),')

if new_entries:
    block = "\n".join(new_entries) + "\n"
    content = content[:insert_at].rstrip() + "\n" + block + content[insert_at:]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Added {len(new_entries)} new words")
print(f"Skipped {dupes} duplicates, {malformed} malformed lines")
print(f"Total unique words now: {len(existing)}")

# Verify the module still parses/imports cleanly
import importlib.util
spec = importlib.util.spec_from_file_location("gre_word_data", DATA_FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(f"VERIFIED: WORDS has {len(mod.WORDS)} entries")

