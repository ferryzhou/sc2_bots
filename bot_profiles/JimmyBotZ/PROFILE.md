# JimmyBotZ

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

The **Zerg** member of the Jimmy family: drone economy into roach/ling with creep and spine defense — a standard macro Zerg.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1820 (top-tier ladder bot) |
| **On ladder since** | 2026-03 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Hatch/pool economic opening into roach warren; drones + creep + queens.

- Roach/ling macro off a drone economy with creep spread and remax.

## Performance (recent ladder sample)

**Overall: 73–75 (49%)** over 148 decided games (+2 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 14-26 | 35% |
| vs Protoss | 22-16 | 57% |
| vs Zerg | 29-25 | 53% |
| vs Random | 8-8 | 50% |

**Toughest opponents:** Crawler 0-5 (Z), Clicadinha 0-4 (Z), BigDaddy 0-4 (T), Nothing 0-4 (P), AvocaDOS 0-3 (T), TheLAW 0-3 (T), Princess-Mika-Test 1-3 (Z), MechaShark 0-2 (T).

**Best matchups:** oberon 4-0 (T), titania 4-0 (Z), Starlight 4-0 (P), MY_SCRIPTING_SON 4-0 (Z), puck 4-1 (P), smokinggunbot 4-1 (T), Belzebuth 3-0 (Z), KoB 3-0 (Z).

## Observed builds (from its own replays)

**vs MY_SCRIPTING_SON (Z), 69.1 min, won:** Drone×55, Overlord×10, CreepTumor×9, Roach×8, CreepTumorQueen×4, Queen×3, Hatchery×2, Extractor×2, SpineCrawler×2, SpawningPool×1, RoachWarren×1, EvolutionChamber×1, HydraliskDen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 36 | 450 | 200 | 30 | 26 |
| 6 | 66 | 60 | 950 | 1400 | 43 | 34 |
| 8 | 76 | 74 | 1600 | 1650 | 42 | 39 |
| 12 | 72 | 96 | 1575 | 2500 | 48 | 42 |

**vs QueenBot (Z), 55.5 min, won:** Drone×59, CreepTumor×12, Overlord×11, Roach×9, Extractor×4, CreepTumorQueen×4, Hatchery×3, Queen×3, EvolutionChamber×2, SpawningPool×1, RoachWarren×1, HydraliskDen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 46 | 550 | 700 | 28 | 32 |
| 6 | 67 | 77 | 1250 | 1400 | 41 | 50 |
| 8 | 97 | 113 | 1825 | 3000 | 55 | 73 |
| 12 | 200 | 145 | 6750 | 3775 | 83 | 85 |

**vs 72Tortoises (Z), 45.2 min, lost:** Drone×47, Roach×16, CreepTumor×10, Overlord×8, CreepTumorQueen×5, Extractor×4, Queen×3, Hatchery×2, SpawningPool×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 45 | 550 | 1150 | 28 | 20 |
| 6 | 32 | 51 | 175 | 1450 | 21 | 22 |
| 8 | 40 | 76 | 775 | 2075 | 20 | 36 |
| 12 | 70 | 152 | 1550 | 3000 | 42 | 89 |

## Strengths

- Competitive vs Protoss (22-16); solid macro base.

## Weaknesses

- Losing form (73-75); weak vs Terran (14-26) — tanks/mech out-range roach-ling.

## How to beat it

1. As Terran, tank/mech + splash; hit a timing before its remax.
2. Deny creep to cut vision and speed.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*