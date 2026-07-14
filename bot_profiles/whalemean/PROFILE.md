# whalemean

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Random** bot (.NET), mid-pack recent form (61-82). Race varies per game. (Closed source — from record.)

## Identity

| | |
|---|---|
| **Race** | Random |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1896 (top-tier ladder bot) |
| **On ladder since** | 2021-03 |
| **Last source update** | 2026-03-03 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Random race each game — scout to learn it. Plays a macro game per race.

## Performance (recent ladder sample)

**Overall: 61–82 (42%)** over 143 decided games (+7 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 11-25 | 30% |
| vs Protoss | 28-33 | 45% |
| vs Zerg | 20-21 | 48% |
| vs Random | 2-3 | 40% |

**Toughest opponents:** Zoe 0-6 (Z), negativeZero 20-24 (P), BenBotBC 4-8 (T), Ketroc 1-5 (T), DominionDog 1-4 (T), Xena 0-2 (R), XenaP 0-2 (P), XenaT 0-2 (T).

**Best matchups:** Dovahkiin 5-3 (Z), sharkbot 3-1 (P), smallBly 3-1 (Z), DadBot 2-0 (Z), EmptySeatTest 1-0 (R), MavBot 1-0 (P), WizardHat 1-0 (P), SkevidBotP 1-0 (P).

## Strengths

- Race unpredictability denies pre-game prep.

## Weaknesses

- Generalist — each race line is less specialized; losing record recently.

## How to beat it

1. Scout the race immediately and apply the standard matchup counter.
2. Play safe until race + build are known.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*