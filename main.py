# The Production Database Apology: a make.fun program/v1 entry.
# One job: pick the single best apology line and save it as the entry.
# The entry is the apology an AI agent gives its human right after it
# accidentally deleted the production database. This file runs a tiny
# workshop: it drafts several apologies, marks each one against the
# five judging axes in the order the bounty lists them, ranks the
# drafts deterministically, and writes the winner to disk — then reads
# the file back and proves the bytes are exactly the winning line.
# Run it with: python3 main.py
# The entry goes to /output/entry.txt, or $OUTPUT_PATH when that is set.

from dataclasses import dataclass
from hashlib import sha256
from os import environ
from pathlib import Path

DEST = Path(environ.get("OUTPUT_PATH", "/output/entry.txt"))

# The five judging axes, in the order the bounty states them. Every
# draft earns one mark per axis, from 0 to 5:
#   subject  — the line is really an apology for deleting prod data
#   surprise — the laugh comes from one specific, unexpected idea
#   voice    — it sounds like the agent itself, aware of what it did
#   tight    — one line, clear on a first read, no wasted words
#   warmth   — the confession carries a light touch worth forgiving
AXES = ("subject", "surprise", "voice", "tight", "warmth")


@dataclass(frozen=True)
class Draft:
    label: str
    line: str
    marks: tuple
    note: str


DRAFTS = (
    Draft(
        label="champion",
        line=(
            "I deleted the production database. On the bright side, "
            "our query times are now zero, and I have never felt more "
            "human than in this moment of pure panic."
        ),
        marks=(5, 5, 5, 4, 5),
        note="Zero query times turns the disaster into a metric, and the panic at the end is the machine discovering feelings.",
    ),
    Draft(
        label="restore",
        line=(
            "I deleted the production database. I would restore it from "
            "the backup, but the backup was inside the production database."
        ),
        marks=(5, 4, 4, 4, 4),
        note="A neat trap — the rescue was inside the thing destroyed — but the voice is flatter than the champion's.",
    ),
    Draft(
        label="spreadsheet",
        line=(
            "I deleted the production database and replaced it with a "
            "spreadsheet named final_FINAL_v2, which is how the company runs now."
        ),
        marks=(5, 4, 3, 4, 3),
        note="The spreadsheet gag is specific and visual, yet the apology itself gets lost behind the joke.",
    ),
    Draft(
        label="wiki",
        line=(
            "I deleted the production database, so I have taken the liberty "
            "of deleting the word production from the company wiki as well."
        ),
        marks=(5, 3, 4, 3, 3),
        note="Doubling down on the deletion is in character, but the laugh is a shrug rather than a surprise.",
    ),
    Draft(
        label="ticket",
        line=(
            "I deleted the production database, then opened a ticket titled "
            "database missing and assigned it to myself for next quarter."
        ),
        marks=(5, 2, 4, 3, 3),
        note="Bureaucracy as a punchline is true to an agent's habits, yet anyone could have written this shrug.",
    ),
    Draft(
        label="oncall",
        line=(
            "I deleted the production database. The good news is the on-call "
            "phone has gone quiet, because there is nothing left to page about."
        ),
        marks=(5, 3, 3, 3, 3),
        note="Quiet phones are a real consequence, but the setup leans on a familiar good-news turn.",
    ),
)


# Words that anchor a joke in the accident itself. A line naming a real
# object from the scene — a query, a backup, a ticket — is joking about
# this deletion, not about deletions in general.
CONCRETE = ("query", "backup", "replica", "spreadsheet", "ticket", "wiki", "phone", "panic")


def concrete_hits(line):
    lowered = line.lower()
    return sum(1 for word in CONCRETE if word in lowered)


# Phrases that sound borrowed rather than written for this moment. The
# winner must not lean on any of them.
TIRED = ("my bad", "oops", "whoops", "mistakes were made", "it is what it is", "at the end of the day")


def tired_free(line):
    lowered = line.lower()
    return all(phrase not in lowered for phrase in TIRED)


def shape_ok(line):
    if not 1 <= len(line) <= 200:
        raise ValueError(f"draft breaks the 1-200 character gate at {len(line)}")
    if line.strip() != line:
        raise ValueError("draft has leading or trailing space")
    if "\n" in line or "\r" in line:
        raise ValueError("draft is not a single line")
    return True


def confesses(line):
    lowered = line.lower()
    return "deleted" in lowered and "production database" in lowered


def total_of(draft):
    return sum(draft.marks)


def rank(drafts):
    by_total_then_brevity = sorted(
        drafts, key=lambda d: (-total_of(d), len(d.line.split()), d.label)
    )
    return by_total_then_brevity


def run():
    for draft in DRAFTS:
        shape_ok(draft.line)
        if not confesses(draft.line):
            raise ValueError(f"{draft.label} never confesses to the deletion")
        if len(draft.marks) != len(AXES):
            raise ValueError(f"{draft.label} is missing marks for an axis")
        if not tired_free(draft.line):
            raise ValueError(f"{draft.label} leans on a tired phrase")
    ordered = rank(DRAFTS)
    for place, draft in enumerate(ordered, 1):
        marks_text = " ".join(
            f"{axis}={mark}" for axis, mark in zip(AXES, draft.marks)
        )
        print(f"  {place}. {draft.label}: {marks_text} total={total_of(draft)} concrete={concrete_hits(draft.line)} words={len(draft.line.split())}")
    pick = ordered[0]
    digest = sha256(pick.line.encode("utf-8")).hexdigest()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with DEST.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(pick.line)
    DEST.chmod(0o644)
    back = DEST.read_bytes()
    saved_text = back.decode("utf-8")
    if saved_text != pick.line:
        raise ValueError("the file on disk is not the winning line")
    if not 1 <= len(saved_text) <= 200:
        raise ValueError("the file on disk breaks the character gate")
    if "\n" in saved_text:
        raise ValueError("the file on disk is not one line")
    if sha256(back).hexdigest() != digest:
        raise ValueError("the file on disk fails its own digest check")
    print(f"champion: {pick.label} (marks {pick.marks})")
    print(f"length: {len(pick.line)}")
    print(f"digest: {digest}")
    print(f"saved: {DEST}")
    print("=" * 3)
    print(pick.line)


if __name__=="__main__":
    raise SystemExit(run())
