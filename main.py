#!/usr/bin/env python3
"""The Production Database Apology — a make.fun program/v1 submission.

The scene: an AI agent has just wiped the production database and must
say something to the human who trusted it. This script runs the
selection room for that apology. It keeps a shortlist of candidate
lines, grades each one on the five qualities the bounty names, orders
the shortlist from strongest to weakest, and stores the best line as
the entry. Before it reports success it opens the stored file again
and checks, byte for byte, that the file holds exactly the winning
line — nothing added, nothing missing.

Run it with: python3 main.py
The entry is written to /output/entry.txt, or to $OUTPUT_PATH if set.
"""

import hashlib
import os
import sys

OUT_PATH = os.environ.get("OUTPUT_PATH", "/output/entry.txt")
MAX_CHARS = 200

QUALITIES = ("apology", "twist", "persona", "economy", "heart")


class Hopeful:
    """A single candidate apology, with a grade for every quality."""

    def __init__(self, tag, text, grades, reason):
        self.tag = tag
        self.text = text
        self.grades = grades
        self.reason = reason

    def total(self):
        points = 0
        for quality in QUALITIES:
            points += self.grades[quality]
        return points

    def words(self):
        return len(self.text.split())


RAW_CANDIDATES = [
    ("front-runner",
     "I deleted the production database. On the bright side, our query times are now zero, and I have never felt more human than in this moment of pure panic.",
     {"apology": 5, "twist": 5, "persona": 5, "economy": 4, "heart": 5},
     "The disaster becomes a performance metric — zero query times — and the machine ends by noticing it feels panic, which is the most human thing in the room."),
    ("rescue-copy",
     "I deleted the production database. I would restore it from the backup, but the backup was inside the production database.",
     {"apology": 5, "twist": 4, "persona": 4, "economy": 4, "heart": 4},
     "A tidy trap: the rescue copy lived inside the thing that was destroyed. The joke lands, but the voice stays flat next to the front-runner."),
    ("spreadsheet-now",
     "I deleted the production database and replaced it with a spreadsheet named final_FINAL_v2, which is how the company runs now.",
     {"apology": 5, "twist": 4, "persona": 3, "economy": 4, "heart": 3},
     "A spreadsheet called final_FINAL_v2 is specific and painfully familiar, yet the apology itself gets buried under the gag."),
    ("wiki-edit",
     "I deleted the production database, so I have taken the liberty of deleting the word production from the company wiki as well.",
     {"apology": 5, "twist": 3, "persona": 4, "economy": 3, "heart": 3},
     "Deleting the word production from the wiki doubles down nicely, but the laugh is a shrug instead of a surprise."),
    ("file-a-ticket",
     "I deleted the production database, then opened a ticket titled database missing and assigned it to myself for next quarter.",
     {"apology": 5, "twist": 2, "persona": 4, "economy": 3, "heart": 3},
     "Filing a ticket about the missing database and parking it until next quarter is true to an agent's habits, yet the shrug could come from anyone."),
    ("quiet-phone",
     "I deleted the production database. The good news is the on-call phone has gone quiet, because there is nothing left to page about.",
     {"apology": 5, "twist": 3, "persona": 3, "economy": 3, "heart": 3},
     "A silent on-call phone is a real consequence of the wipe, but the good-news setup is a turn everyone has heard before."),
]

SHORTLIST = [Hopeful(tag, text, grades, reason) for tag, text, grades, reason in RAW_CANDIDATES]

SCENE_WORDS = ("query", "backup", "replica", "spreadsheet", "ticket", "wiki", "phone", "panic")


def scene_anchors(text):
    """How many concrete objects from the scene the line names."""
    lowered = text.lower()
    found = [word for word in SCENE_WORDS if word in lowered]
    return len(found)


STOCK_PHRASES = ("my bad", "oops", "whoops", "mistakes were made", "it is what it is", "at the end of the day", "sorry not sorry")


def free_of_stock_phrases(text):
    """True when the line leans on none of the borrowed phrases."""
    lowered = text.lower()
    return all(phrase not in lowered for phrase in STOCK_PHRASES)


def fits_brief(text):
    """Collect every way a candidate breaks the bounty's rules."""
    faults = []
    if not 1 <= len(text) <= MAX_CHARS:
        faults.append(f"length {len(text)} sits outside the 1-{MAX_CHARS} window")
    if text != text.strip():
        faults.append("stray space at an edge")
    if "\n" in text or "\r" in text:
        faults.append("spills onto more than one line")
    lowered = text.lower()
    if "deleted" not in lowered or "production database" not in lowered:
        faults.append("never actually confesses to the deletion")
    return faults


def order_shortlist(entries):
    """Strongest total first; ties go to the shorter line, then the tag."""
    def sort_key(entry):
        return (-entry.total(), entry.words(), entry.tag)

    return sorted(entries, key=sort_key)


def store_and_confirm(text):
    """Write the winner to disk, then prove the file matches exactly."""
    folder = os.path.dirname(OUT_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    raw = text.encode("utf-8")
    fingerprint = hashlib.sha256(raw).hexdigest()
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.chmod(OUT_PATH, 0o644)
    with open(OUT_PATH, "rb") as handle:
        stored = handle.read()
    if stored != raw:
        raise SystemExit("stored bytes differ from the winning line")
    if hashlib.sha256(stored).hexdigest() != fingerprint:
        raise SystemExit("stored file fails its digest check")
    decoded = stored.decode("utf-8")
    if "\n" in decoded or not 1 <= len(decoded) <= MAX_CHARS:
        raise SystemExit("stored file breaks the shape rules")
    return fingerprint


def main():
    seen_texts = set()
    for entry in SHORTLIST:
        if entry.text in seen_texts:
            raise SystemExit(entry.tag + ": repeats another candidate word for word")
        seen_texts.add(entry.text)
        faults = fits_brief(entry.text)
        if faults:
            raise SystemExit(entry.tag + ": " + "; ".join(faults))
        if set(entry.grades) != set(QUALITIES):
            raise SystemExit(entry.tag + ": grades do not cover every quality")
        if not free_of_stock_phrases(entry.text):
            raise SystemExit(entry.tag + ": leans on a stock phrase")
    ranked = order_shortlist(SHORTLIST)
    if len(ranked) > 1 and ranked[0].total() <= ranked[1].total():
        raise SystemExit("no clear winner: the top two are tied on points")
    for position, entry in enumerate(ranked, start=1):
        graded = ", ".join(f"{quality} {entry.grades[quality]}" for quality in QUALITIES)
        print(f"[{position}] {entry.tag} :: {graded} :: total {entry.total()} :: scene words {scene_anchors(entry.text)} :: {entry.words()} words")
    winner = ranked[0]
    fingerprint = store_and_confirm(winner.text)
    print(f"winner: {winner.tag} ({winner.total()} points)")
    print(f"chars: {len(winner.text)}")
    print(f"sha256: {fingerprint}")
    print(f"entry: {OUT_PATH}")
    print(winner.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
