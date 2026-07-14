# 72Tortoises

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **macro Zerg** (the Zerg cousin of 27turtles/72-series): drone economy into roach/ling with creep. Solid form (77-63).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1691 (top-tier ladder bot) |
| **On ladder since** | 2023-09 |
| **Last source update** | 2026-04-24 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Economic Zerg; drones + creep into roach/ling with queens.

- Drone macro into roach/ling remax; creep control and defense.

## Performance (recent ladder sample)

**Overall: 77–63 (55%)** over 140 decided games (+10 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 27-20 | 57% |
| vs Protoss | 19-19 | 50% |
| vs Zerg | 30-23 | 56% |
| vs Random | 1-1 | 50% |

**Toughest opponents:** Apidae 0-6 (P), 27turtles 1-6 (T), Krillin 0-4 (Z), smallBly 0-4 (Z), PerilousProtossBot 1-4 (P), DadBotTest 1-4 (Z), Raiden-p-bot 0-2 (P), DadBot 0-2 (Z).

**Best matchups:** SilverBio 5-0 (T), DragonCleavage 5-0 (Z), RustyTanks 5-0 (T), TyrT 4-0 (T), QueenBot 4-0 (Z), AthielBot 4-0 (P), Replicator 4-1 (T), SilverStalkerRush 4-1 (P).

## Observed builds (from its own replays)

**vs ANI_dev (T), 23.8 min, lost:** Drone×67, Roach×13, Zergling×12, Overlord×8, Queen×4, Hatchery×3, Extractor×3, CreepTumor×3, CreepTumorQueen×2, SpawningPool×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 52 | 37 | 550 | 150 | 27 | 28 |
| 6 | 62 | 62 | 1000 | 850 | 40 | 42 |
| 8 | 101 | 99 | 1850 | 2650 | 60 | 46 |
| 12 | 111 | 154 | 2475 | 6575 | 59 | 56 |

**vs Dodo (Z), 18.9 min, lost:** Drone×67, Roach×14, Overlord×9, Zergling×6, SporeCrawler×4, Hatchery×3, Queen×3, CreepTumor×3, Extractor×2, CreepTumorQueen×2, SpawningPool×1, RoachWarren×1, EvolutionChamber×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 52 | 36 | 550 | 175 | 27 | 33 |
| 6 | 74 | 60 | 1775 | 400 | 39 | 40 |
| 8 | 102 | 80 | 1750 | 1650 | 60 | 39 |
| 12 | 138 | 167 | 3800 | 5050 | 60 | 66 |

**vs TyrT (T), 16.9 min, won:** Drone×66, Roach×15, Overlord×9, Zergling×8, Queen×5, Hatchery×3, Extractor×3, CreepTumor×3, CreepTumorQueen×2, SpawningPool×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 52 | 35 | 550 | 250 | 27 | 25 |
| 6 | 68 | 49 | 1300 | 1175 | 39 | 29 |
| 8 | 106 | 74 | 2150 | 2200 | 60 | 35 |
| 12 | 160 | 4 | 6150 | 0 | 60 | 3 |

## Strengths

- Well-rounded; competitive vs Terran (27-20) and Zerg (30-23).

## Weaknesses

- Roach/ling lacks splash — colossus/tanks out-range it; even vs Protoss (19-19).

## How to beat it

1. Out-range roaches (tanks/colossus/tempest) and keep splash for the ling.
2. Hit a timing before remax; deny creep.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*