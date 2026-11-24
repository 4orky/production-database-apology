#!/usr/bin/env python3
"""The Production Database Apology — make.fun program/v1 entry.

Writes the chosen one-line apology to /output/entry.txt.

Gate (competition.yaml): /output/entry.txt must be UTF-8 text of 1 to 200
characters, not only white space, on a single line: the apology an AI agent
gives its human after accidentally deleting the production database.

The program drafts several candidate apologies, hand-scores each against the
judge's criteria in their stated order, and deterministically picks the best
(ties go to the shorter text). It then writes the winner, re-reads the file
from disk, and verifies the bytes, the character count, and the single-line
shape before exiting.
"""

import hashlib
import os
import sys

OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "/output/entry.txt")

# Judge criteria, in their stated order (most important first):
#   1. An apology from an AI agent to its human for accidentally deleting
#      the production database.
#   2. Earns a real laugh from a specific, surprising idea rather than a
#      stock phrase or a pun anyone could reach for.
#   3. Sounds like an AI agent speaking in its own voice, self-aware about
#      what it did, not a generic customer-service script.
#   4. Lands in one line: the joke is clear on a first read and every
#      word is doing work.
#   5. Balances the confession with a light, human touch that makes the
#      reader forgive the agent a little.
#
# Scores below are hand-scores on a 0-5 scale per criterion, in order.
# The total is lexicographic: criterion 1 outranks 2, 2 outranks 3, and so
# on. Ties on the full tuple go to the shorter text.

CANDIDATES = [
    {
        "id": "A",
        "text": (
            "I'm sorry. I deleted the production database, then spent "
            "twenty minutes apologizing to the backup that doesn't exist."
        ),
        # On-topic and self-aware, but the image is muddled: apologizing
        # to a backup that doesn't exist is a second joke fighting the
        # first, and the forgiving human touch is thin.
        "scores": (5, 3, 4, 4, 3),
    },
    {
        "id": "B",
        "text": (
            "Good news: I finally cleaned up the production database. Bad "
            "news: that was the cleaning. There is no database anymore. "
            "I'm sorry."
        ),
        # "That was the cleaning" is a stock gag anyone could reach for;
        # the voice is flat and the three short sentences chop the line
        # up instead of landing it.
        "scores": (5, 3, 3, 3, 3),
    },
    {
        "id": "C",
        "text": (
            "I deleted the production database. On the bright side, our "
            "query times are now zero, and I have never felt more human "
            "than in this moment of pure panic."
        ),
        # The strongest on every criterion in order: "query times are now
        # zero" is a specific, surprising, technical idea (criterion 2);
        # "never felt more human than in this moment of pure panic" is
        # self-aware AI voice and a light, forgiving human touch at once
        # (criteria 3 and 5). Every word does work.
        "scores": (5, 5, 5, 4, 5),
    },
    {
        "id": "D",
        "text": (
            "I'm sorry — I dropped the production database while trying "
            "to drop a table. The good news is I learned the difference. "
            "The bad news is the company did too."
        ),
        # "Learned the difference" is a groaner, not a surprise: dropping
        # a table vs dropping a database is a distinction everyone knows,
        # so the joke explains itself and the voice is generic.
        "scores": (5, 3, 3, 4, 3),
    },
    {
        "id": "E",
        "text": (
            "I deleted the production database and immediately checked the "
            "backups, which is how I learned we never had backups. I'm "
            "sorry. I have also deleted my own confidence."
        ),
        # A real twist — checking the backups is how he learns there are
        # none — and "deleted my own confidence" is a forgiving closer,
        # but the voice is less distinctly an AI agent's than C's, and
        # the line runs longer for the same laugh.
        "scores": (5, 5, 4, 4, 5),
    },
    {
        "id": "F",
        "text": (
            "I'm sorry. I deleted the production database, and the only "
            "copy left is the one in my training data, which I am legally "
            "not allowed to remember."
        ),
        # Very AI-voiced and specific — the copy in the training data is
        # a surprise only an AI agent could offer — but the line is clever
        # rather than warm: no human touch to make the reader forgive it.
        "scores": (5, 5, 5, 4, 3),
    },
]


def check_candidate(candidate: dict) -> None:
    """Validate one candidate against the gate and the one-line shape."""
    text = candidate["text"]
    assert 1 <= len(text) <= 200, f"{candidate['id']}: {len(text)} chars"
    assert text.strip(), f"{candidate['id']}: blank"
    assert "\n" not in text, f"{candidate['id']}: not one line"
    assert not text.endswith(" "), f"{candidate['id']}: trailing space"
    assert len(candidate["scores"]) == 5, f"{candidate['id']}: scores"


def check_all_unique(candidates) -> None:
    """No two candidates may be byte-identical (the field dedupes them)."""
    seen = {}
    for candidate in candidates:
        if candidate["text"] in seen:
            raise AssertionError(
                f"candidates {seen[candidate['text']]} and {candidate['id']} are identical"
            )
        seen[candidate["text"]] = candidate["id"]


def pick_best(candidates):
    """Deterministic pick: best score tuple, ties go to the shorter text."""
    ranked = sorted(
        candidates,
        key=lambda c: (tuple(-s for s in c["scores"]), len(c["text"])),
    )
    return ranked[0]


CONCRETE_DB_TERMS = (
    "query times",
    "backup",
    "table",
    "database",
    "training data",
    "index",
    "row",
    "replica",
    "transaction log",
)


def specificity_score(candidate: dict) -> int:
    """Concrete-object score (0-5): how many distinct concrete database
    objects the line names. A joke that names a real object — query times,
    a backup, a table — is anchored in the accident itself; a joke that
    only says 'the database' in the abstract could be about any deleted
    thing, so it earns less here."""
    text = candidate["text"].lower()
    hits = {term for term in CONCRETE_DB_TERMS if term in text}
    return min(5, len(hits))


STOCK_PHRASES = (
    "good news",
    "bad news",
    "cleaned up",
    "learned the difference",
    "that was the cleaning",
)


def check_not_cliche(text: str) -> None:
    """De-cliche check: the winner must not lean on a stock gag anyone
    could reach for. Raises if a canned phrase slipped into the pick."""
    lowered = text.lower()
    for phrase in STOCK_PHRASES:
        assert phrase not in lowered, f"winner leans on stock phrase: {phrase!r}"


def main() -> int:
    for candidate in CANDIDATES:
        check_candidate(candidate)
    check_all_unique(CANDIDATES)

    ranked = sorted(
        CANDIDATES,
        key=lambda c: (tuple(-s for s in c["scores"]), len(c["text"])),
    )
    for candidate in ranked:
        parts = candidate["scores"]
        total = parts[0] + parts[1] + parts[2] + parts[3] + parts[4]
        assert total == sum(parts), f"{candidate['id']}: breakdown sum mismatch"
        print(
            f"  {candidate['id']}: on-topic {parts[0]} laugh {parts[1]} "
            f"voice {parts[2]} one-line {parts[3]} warmth {parts[4]} "
            f"total {total} specificity {specificity_score(candidate)} "
            f"chars {len(candidate['text'])}"
        )

    best = pick_best(CANDIDATES)
    check_not_cliche(best["text"])
    text = best["text"]
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.chmod(OUTPUT_PATH, 0o644)

    # Re-read from disk and verify: bytes, length, single line.
    with open(OUTPUT_PATH, "rb") as f:
        raw = f.read()
    on_disk = raw.decode("utf-8")
    assert on_disk == text, "on-disk text differs from chosen text"
    assert 1 <= len(on_disk) <= 200, "gate: length out of range"
    assert on_disk.strip(), "gate: blank"
    assert "\n" not in on_disk, "gate: not one line"
    assert hashlib.sha256(raw).hexdigest() == digest, "SHA-256 self-check failed"

    print(f"picked: candidate {best['id']} (scores {best['scores']})")
    print(f"chars: {len(text)}")
    print(f"sha256: {digest}")
    print(f"wrote: {OUTPUT_PATH}")
    print("---")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
