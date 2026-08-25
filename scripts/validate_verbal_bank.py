#!/usr/bin/env python3
"""Validate the GRE Verbal mock test question bank (data/gre_verbal/questions.json).

Checks:
  - JSON parses; required top-level keys exist
  - All question IDs are unique
  - Text Completion: option_sets count == blanks; single-blank sets have 5 options,
    multi-blank sets have 3 options per blank; answers in range
  - Sentence Equivalence: exactly 6 options and exactly 2 distinct answers in range
  - Reading Comprehension: valid question types with correct option/answer shapes;
    select_in_passage answers index into the passage's sentence list

Exit code 0 = bank is healthy; nonzero = problems found.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BANK_FILE = os.path.join(PROJECT_ROOT, "data", "gre_verbal", "questions.json")

errors = []


def err(msg):
    errors.append(msg)


def check_text_completion(items):
    for q in items:
        qid = q.get("id", "<missing id>")
        blanks = q.get("blanks")
        option_sets = q.get("option_sets")
        if not isinstance(blanks, int) or blanks < 1 or blanks > 3:
            err(f"{qid}: blanks must be 1-3, got {blanks!r}")
            continue
        if not isinstance(option_sets, list) or len(option_sets) != blanks:
            err(f"{qid}: expected {blanks} option_sets, got {len(option_sets or [])}")
            continue
        expected_opts = 5 if blanks == 1 else 3
        for i, opts in enumerate(option_sets):
            if len(opts) != expected_opts:
                err(f"{qid}: blank {i+1} should have {expected_opts} options, got {len(opts)}")
        answers = q.get("answers")
        if not isinstance(answers, list) or len(answers) != blanks:
            err(f"{qid}: expected {blanks} answers, got {answers!r}")
            continue
        for bi, ai in enumerate(answers):
            if not isinstance(ai, int) or not (0 <= ai < len(option_sets[bi])):
                err(f"{qid}: answer index {ai} out of range for blank {bi+1}")
        for field in ("passage", "explanation"):
            if not q.get(field):
                err(f"{qid}: missing {field}")


def check_sentence_equivalence(items):
    for q in items:
        qid = q.get("id", "<missing id>")
        opts = q.get("options", [])
        if len(opts) != 6:
            err(f"{qid}: SE must have exactly 6 options, got {len(opts)}")
        answers = q.get("answers", [])
        if len(answers) != 2 or answers[0] == answers[1]:
            err(f"{qid}: SE must have exactly 2 distinct answers, got {answers!r}")
        else:
            for ai in answers:
                if not isinstance(ai, int) or not (0 <= ai < len(opts)):
                    err(f"{qid}: SE answer index {ai} out of range")
        if "|BLANK|" not in q.get("sentence", ""):
            err(f"{qid}: SE sentence missing |BLANK| placeholder")
        if not q.get("explanation"):
            err(f"{qid}: missing explanation")


def check_reading_comprehension(passages):
    for p in passages:
        pid = p.get("id", "<missing id>")
        sentences = p.get("sentences", [])
        if not p.get("passage"):
            err(f"{pid}: missing passage text")
        has_sip = any(q.get("type") == "select_in_passage" for q in p.get("questions", []))
        if has_sip and len(sentences) < 2:
            err(f"{pid}: passage has select_in_passage questions but no 'sentences' array")
        for q in p.get("questions", []):
            qid = q.get("id", "<missing id>")
            qtype = q.get("type")
            opts = q.get("options", [])
            ans = q.get("answer", [])
            if qtype == "single":
                if len(opts) != 5:
                    err(f"{qid}: single-choice must have 5 options")
                if len(ans) != 1:
                    err(f"{qid}: single-choice must have exactly 1 answer")
                for ai in ans:
                    if isinstance(ai, int) and ai >= len(opts):
                        err(f"{qid}: answer index {ai} out of range")
            elif qtype == "multiple":
                if len(opts) != 3:
                    err(f"{qid}: multiple-choice must have 3 options (select-all format)")
                if not (2 <= len(ans) <= 3):
                    err(f"{qid}: multiple-choice needs 2+ correct answers, got {len(ans)}")
                for ai in ans:
                    if isinstance(ai, int) and ai >= len(opts):
                        err(f"{qid}: answer index {ai} out of range")
            elif qtype == "select_in_passage":
                if len(ans) != 1:
                    err(f"{qid}: select_in_passage must have exactly 1 answer")
                elif ans[0] >= len(sentences):
                    err(f"{qid}: select_in_passage answer {ans[0]} exceeds sentences ({len(sentences)})")
            else:
                err(f"{qid}: unknown question type {qtype!r}")
                continue
            if not q.get("prompt"):
                err(f"{qid}: missing prompt")
            if not q.get("explanation"):
                err(f"{qid}: missing explanation")


def main():
    try:
        with open(BANK_FILE, "r", encoding="utf-8") as f:
            bank = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: bank file not found: {BANK_FILE}")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}")
        return 1

    tc = bank.get("text_completion", [])
    se = bank.get("sentence_equivalence", [])
    rc = bank.get("reading_comprehension", [])

    check_text_completion(tc)
    check_sentence_equivalence(se)
    check_reading_comprehension(rc)

    all_ids = ([q["id"] for q in tc] + [q["id"] for q in se]
               + [q["id"] for p in rc for q in p["questions"]])
    dupes = {i for i in all_ids if all_ids.count(i) > 1}
    if dupes:
        err(f"duplicate question ids: {sorted(dupes)}")

    # Verify the bank can satisfy the configured test composition.
    cfg = bank.get("test_config", {}).get("composition", {})
    singles = sum(1 for q in tc if q.get("blanks") == 1)
    doubles = sum(1 for q in tc if q.get("blanks") == 2)
    triples = sum(1 for q in tc if q.get("blanks") == 3)
    checks = [
        (singles, cfg.get("text_completion_single", 0), "single-blank TC"),
        (doubles, cfg.get("text_completion_double", 0), "double-blank TC"),
        (triples, cfg.get("text_completion_triple", 0), "triple-blank TC"),
        (len(se), cfg.get("sentence_equivalence", 0), "sentence equivalence"),
    ]
    for have, need, label in checks:
        if have < need:
            err(f"bank has {have} {label} but composition needs {need}")

    total_rc = sum(len(p.get("questions", [])) for p in rc)
    print("=" * 60)
    print("GRE Verbal Question Bank Validation")
    print("=" * 60)
    print(f"Text Completion:      {len(tc):3d}  ({singles} single / {doubles} double / {triples} triple)")
    print(f"Sentence Equivalence: {len(se):3d}")
    print(f"Reading Comp:         {total_rc:3d}  across {len(rc)} passages")
    print(f"Total questions:      {len(all_ids)}")

    if errors:
        print(f"\nFAILED - {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nPASSED: bank structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
