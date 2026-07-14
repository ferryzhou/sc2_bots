# FlowerPrincess

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **ling-flood Zerg**: mass zerglings (60+) off a drone economy. Aggressive but currently losing (56-88).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1682 (top-tier ladder bot) |
| **On ladder since** | 2025-08 |
| **Last source update** | 2026-06-02 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Fast pool into mass zergling + drones; ling flood with creep.

- Zergling flood to overwhelm early, drone economy behind if held.

## Performance (recent ladder sample)

**Overall: 56–88 (38%)** over 144 decided games (+6 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 36-26 | 58% |
| vs Protoss | 7-25 | 21% |
| vs Zerg | 13-26 | 33% |
| vs Random | 0-11 | 0% |

**Toughest opponents:** Chance 0-7 (R), Apidae 0-7 (P), nida 0-7 (P), WickedBot 2-8 (T), zig-spudde 1-6 (T), norman 0-4 (P), Klakinn 3-6 (P), 72Tortoises 2-5 (Z).

**Best matchups:** VeTerran_another 6-0 (T), zig-reapers 5-2 (T), ANI_dev 5-2 (T), muravevTerranV2 5-2 (T), 27turtles 4-1 (T), Win___ter 3-0 (P), Suimon 2-0 (T), Gordon 1-0 (T).

## Observed builds (from its own replays)

**vs QueenBot (Z), 48.4 min, won:** Drone×63, Zergling×62, CreepTumor×13, Overlord×10, CreepTumorQueen×5, Extractor×4, Queen×4, Hatchery×3, SpawningPool×1, EvolutionChamber×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 45 | 49 | 525 | 700 | 29 | 34 |
| 6 | 65 | 87 | 1350 | 1925 | 39 | 54 |
| 8 | 97 | 104 | 2100 | 3000 | 53 | 65 |
| 12 | 148 | 33 | 3975 | 2300 | 64 | 1 |

**vs PhantomTest (Z), 45.0 min, won:** Zergling×62, Drone×53, CreepTumor×18, Overlord×12, CreepTumorQueen×9, Queen×6, Extractor×4, Hatchery×3, SpawningPool×1, EvolutionChamber×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 38 | 48 | 625 | 750 | 30 | 35 |
| 6 | 59 | 76 | 1250 | 1100 | 40 | 46 |
| 8 | 84 | 96 | 1575 | 1700 | 52 | 62 |
| 12 | 37 | 190 | 475 | 6425 | 31 | 79 |

**vs QueenBot (Z), 36.1 min, lost:** Drone×64, Zergling×34, Overlord×13, CreepTumor×11, Roach×7, CreepTumorQueen×5, Extractor×4, Queen×4, Hatchery×3, SpawningPool×1, EvolutionChamber×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 46 | 49 | 725 | 700 | 30 | 35 |
| 6 | 68 | 87 | 1250 | 1925 | 44 | 52 |
| 8 | 108 | 100 | 2200 | 2825 | 53 | 64 |
| 12 | 128 | 114 | 2700 | 3000 | 71 | 64 |

## Strengths

- Best vs Terran (36-26) — the ling flood punishes un-walled bio.
- Early army value can overwhelm the unprepared.

## Weaknesses

- Weak vs Protoss (7-25) and Zerg (13-26) — splash (colossus/storm, banelings) shreds the flood.
- Melee into a wall stalls; thin tech.

## How to beat it

1. Wall + splash (tanks/hellions, colossus/storm, banelings) and hold — don't fight lings in the open.
2. Then punish its thin economy once the flood is spent.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*