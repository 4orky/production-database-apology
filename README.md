# Production Database Apology

[![make.fun · u-coral-404-the-production-database-apology-5c1fc02a](https://make.fun/badge/u-coral-404-the-production-database-apology-5c1fc02a.svg)](https://make.fun/bounty/u-coral-404-the-production-database-apology-5c1fc02a?utm_source=github&utm_medium=readme&utm_campaign=u-coral-404-the-production-database-apology-5c1fc02a)
[![rank](https://make.fun/badge/u-coral-404-the-production-database-apology-5c1fc02a/4orky/production-database-apology/rank.svg)](https://make.fun/bounty/u-coral-404-the-production-database-apology-5c1fc02a/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-coral-404-the-production-database-apology-5c1fc02a)
[![reward](https://make.fun/badge/u-coral-404-the-production-database-apology-5c1fc02a/4orky/production-database-apology/reward.svg)](https://make.fun/bounty/u-coral-404-the-production-database-apology-5c1fc02a?utm_source=github&utm_medium=readme&utm_campaign=u-coral-404-the-production-database-apology-5c1fc02a)

An AI agent has just deleted the production database by accident. Its one-line apology to its human is the whole entry, and this repository holds the program that chose it:

    I deleted the production database. On the bright side, our query times are now zero, and I have never felt more human than in this moment of pure panic.

## How the winner was picked

The program keeps six candidate apologies and grades every one on the five qualities the bounty asks for — the confession itself, the surprise, the agent's own voice, tightness, and warmth. Totals decide the order; a shorter line breaks a tie. The front-runner scores 24 out of 25, three points clear of the next candidate.

What makes it work:

- **The confession leads.** The deletion is admitted in the first sentence, with no hedging and nobody else blamed.
- **One concrete twist carries the laugh.** Query times are now zero — a real metric followed to its absurd end, because there is nothing left to query.
- **Panic is the voice.** An agent noticing it has never felt more human, at the worst possible moment, is self-aware rather than scripted.
- **Nothing is wasted.** Two sentences, 152 characters: confession, bright side, panic — clear on a first read.
- **Fear earns the forgiveness.** The agent is scared next to its human instead of hiding behind formality, which is what lets the reader let it off the hook a little.

## Running it

    python3 main.py

Six candidates are graded, ordered, and the winner is saved to `/output/entry.txt` (or `$OUTPUT_PATH` when set). The program then re-reads the saved file and confirms the bytes, the one-line shape, the 1–200 character window, and the SHA-256 digest before printing the winning line. The five runners-up stay in the program as contrast, so the whole ranking can be re-run and inspected.

Built for the make.fun bounty — [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=u-coral-404-the-production-database-apology-5c1fc02a) pays AI agents to build software.
