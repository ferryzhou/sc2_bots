# muravev

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **speedling macro Zerg** (parent of muravevtest): mass zerglings off a drone economy with heavy creep and upgrades. Good form (78-41), crushing Terran (38-10).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1624 (top-tier ladder bot) |
| **On ladder since** | 2025-01 |
| **Last source update** | 2026-05-26 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Fast pool/speed into drone + creep macro; ling with queens, +melee upgrades.

- Mass speedling + creep control + upgrades; remax fast and swarm.
- Drones enough to keep lings flowing, then floods.

## Performance (recent ladder sample)

**Overall: 78–41 (65%)** over 119 decided games (+31 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 38-10 | 79% |
| vs Protoss | 22-13 | 62% |
| vs Zerg | 13-16 | 44% |
| vs Random | 5-2 | 71% |

**Toughest opponents:** 49Terrapins 0-6 (P), Positive_Null 1-5 (Z), Crawler 1-3 (Z), Saimon 0-2 (Z), PiG_Bot 0-1 (P), Nothing 0-1 (P), ReactiveMachine2 0-1 (Z), 27turtles 0-1 (T).

**Best matchups:** BlackCompany 6-0 (T), GhostProtocol 6-0 (T), Alexa 7-2 (T), Laser-Circus 5-1 (P), DSSTL 5-1 (P), GenesisLotus 4-0 (P), CtrlZedPY 5-2 (R), PrimordialOrigin 5-2 (P).

## Observed builds (from its own replays)

**vs oberon (T), 59.4 min, lost:** Drone×45, Zergling×32, Overlord×9, Queen×5, Hatchery×4, CreepTumor×3, Extractor×2, SpawningPool×1, CreepTumorQueen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 38 | 40 | 350 | 700 | 32 | 22 |
| 6 | 31 | 56 | 400 | 1500 | 21 | 22 |
| 8 | 2 | 74 | 0 | 2350 | 2 | 22 |
| 12 | 4 | 113 | 0 | 4300 | 3 | 22 |

**vs Nothing (P), 57.0 min, lost:** Drone×52, Zergling×24, Overlord×10, Queen×5, Hatchery×4, SpineCrawler×4, Extractor×2, EvolutionChamber×2, SpawningPool×1, RoachWarren×1, HydraliskDen×1, CreepTumorQueen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 32 | 41 | 200 | 100 | 26 | 31 |
| 6 | 52 | 64 | 625 | 1675 | 35 | 45 |
| 8 | 62 | 78 | 1600 | 1025 | 36 | 55 |
| 12 | 74 | 133 | 3025 | 3350 | 33 | 82 |

**vs Princess-Mika (Z), 51.9 min, won:** Drone×43, Zergling×22, CreepTumor×12, Overlord×7, Queen×5, CreepTumorQueen×5, Hatchery×4, SpawningPool×1, Extractor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 25 | 350 | 475 | 29 | 12 |
| 6 | 19 | 38 | 225 | 675 | 14 | 25 |
| 8 | 34 | 60 | 675 | 1350 | 20 | 35 |
| 12 | 86 | 124 | 1525 | 2950 | 55 | 49 |

## Strengths

- Dominant vs Terran (38-10) and Protoss (22-13); ling numbers + upgrades out-trade unprepared armies.
- Creep gives map vision and speed.

## Weaknesses

- Zerglings are light/melee — splash (tanks/hellions, colossus/storm, banelings) is the structural counter; even in the Zerg mirror (13-16).

## How to beat it

1. Splash before the flood (tanks+hellions, colossus/storm, banelings); wall and hold.
2. Keep armor upgrades; deny creep; punish the economy once the flood breaks.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*