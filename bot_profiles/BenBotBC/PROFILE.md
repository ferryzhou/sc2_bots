# BenBotBC

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A veteran **Terran** bot (Java, on the ladder since 2019) known for aggressive marine-based bio and micro. (Closed source — characterization from record + long-standing reputation.)

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | java |
| **AI Arena Elo** | ~2143 (top-tier ladder bot) |
| **On ladder since** | 2019-12 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio-oriented Terran; marine/marauder pressure with strong unit control.

- Marine-centric bio with tight micro (splits, focus fire).
- Applies bio pressure and macros behind it.

## Performance (recent ladder sample)

**Overall: 43–89 (32%)** over 132 decided games (+18 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 7-9 | 43% |
| vs Protoss | 12-53 | 18% |
| vs Zerg | 2-24 | 7% |
| vs Random | 22-3 | 88% |

**Toughest opponents:** TheGoldenArmada 3-17 (P), CreepyBot 0-7 (Z), TyrP 4-10 (P), AdditionalPylons 0-6 (P), MavBot3 0-6 (P), TyrZ 0-5 (Z), Paul 0-5 (Z), Sharpy_MadAI 0-4 (P).

**Best matchups:** A.L.E.R.T. 14-2 (R), A.L.E.R.T.-dev 8-1 (R), BenBotv2 1-0 (T), TheUnseenz 1-0 (P), Rusty 1-0 (T), BetterWorkerRush 1-0 (P), BCMACHINE 1-0 (T), Fire 1-0 (T).

## Strengths

- Strong marine micro; punishes poor defensive positioning.
- Very strong vs Random (22-3) in-sample.

## Weaknesses

- In the recent sample it struggles badly vs Protoss (12-53) and Zerg (2-24) — splash/colossus/storm and mass army out-trade its bio.
- Bio-heavy with limited splash of its own.

## How to beat it

1. Bring splash: colossus/storm (P), banelings/lurkers (Z) — the sample shows these dominate it right now.
2. Hold defensive positions; don't get caught out of position by marine micro.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*