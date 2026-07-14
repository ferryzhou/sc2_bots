# Persephone

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **ling/roach macro Zerg**: equal parts zergling and drone into roach, with creep and queens. Even-ish form (64-79).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1632 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Pool into ling + drone (balanced) into roach warren; creep + queens.

- Ling/roach army off a drone economy; pressure with lings, remax roach.

## Performance (recent ladder sample)

**Overall: 64–79 (44%)** over 143 decided games (+7 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 15-18 | 45% |
| vs Protoss | 25-23 | 52% |
| vs Zerg | 22-33 | 40% |
| vs Random | 2-5 | 28% |

**Toughest opponents:** Princess-Mika 0-5 (Z), muravev 0-4 (Z), Hellcannon 0-4 (P), puck 0-4 (P), Crawler 0-4 (Z), Klakinn 0-4 (P), MindMatrix 0-3 (Z), ArtZerg 0-3 (Z).

**Best matchups:** 49Terrapins 5-0 (P), oberon 5-0 (T), PerilousProtossBot 4-0 (P), NecroBot 3-0 (Z), TyrP 3-0 (P), Arpy 3-1 (P), PolyMorph 2-0 (Z), Lissy 2-0 (Z).

## Observed builds (from its own replays)

**vs PerilousProtossBot (P), 54.6 min, won:** Drone×58, Zergling×58, Overlord×7, CreepTumor×7, Queen×5, CreepTumorQueen×4, Hatchery×3, Extractor×2, SpawningPool×1, BanelingNest×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 16 | 350 | 0 | 26 | 15 |
| 6 | 49 | 30 | 675 | 200 | 32 | 22 |
| 8 | 62 | 48 | 850 | 1125 | 41 | 24 |
| 12 | 77 | 54 | 1525 | 2225 | 50 | 24 |

**vs QueenBot (Z), 31.8 min, lost:** Drone×64, Zergling×18, CreepTumor×14, Overlord×10, Hatchery×6, CreepTumorQueen×5, Queen×4, Extractor×2, EvolutionChamber×2, SpawningPool×1, BanelingNest×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 46 | 725 | 700 | 25 | 32 |
| 6 | 72 | 76 | 975 | 1400 | 48 | 49 |
| 8 | 94 | 112 | 2525 | 2650 | 55 | 76 |
| 12 | 98 | 69 | 2550 | 4575 | 54 | 15 |

**vs clone (T), 29.6 min, won:** Drone×59, Zergling×24, Overlord×9, CreepTumor×8, Queen×6, CreepTumorQueen×5, Hatchery×3, Extractor×2, SpawningPool×1, BanelingNest×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 32 | 500 | 600 | 29 | 19 |
| 6 | 54 | 55 | 900 | 1100 | 36 | 25 |
| 8 | 74 | 88 | 1525 | 2425 | 45 | 39 |
| 12 | 124 | 111 | 3600 | 2925 | 64 | 64 |

## Strengths

- Competitive vs Protoss (25-23); ling/roach flexibility.

## Weaknesses

- Weak in the Zerg mirror (22-33); ling/roach lacks splash vs colossus/tanks.
- Melee-heavy front-line.

## How to beat it

1. Out-range roaches and splash the lings (tanks/colossus/storm).
2. Hold aggression at a wall, then out-macro.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*