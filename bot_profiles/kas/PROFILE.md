# kas

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **hyper-economic drone-macro Zerg**: over-drones massively (90+ drones) with heavy creep and queens, remaxing a big army late. Greedy macro. Strong vs Terran (22-7) but weak vs P/Z.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1638 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-06-05 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Very economic Zerg; drone-heavy with creep spread and queens, minimal early army.

- Drone to a huge economy behind creep + queens, then remax roach/hydra/ling waves.
- Bets everything on out-economying — a wide thin-army window early.

## Performance (recent ladder sample)

**Overall: 58–83 (41%)** over 141 decided games (+9 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 22-7 | 75% |
| vs Protoss | 14-31 | 31% |
| vs Zerg | 17-39 | 30% |
| vs Random | 5-6 | 45% |

**Toughest opponents:** Eris 0-7 (Z), puck 0-4 (P), 49Terrapins 0-3 (P), MindMatrix 0-3 (Z), SiriusBot 1-3 (R), Apidae 0-2 (P), PiG_Bot 0-2 (P), FlowerPrincess 0-2 (Z).

**Best matchups:** Stockfish 4-0 (T), RustyNikolaj 3-0 (T), Forsaken 3-0 (T), muravevTerran 3-0 (T), NecroBot 3-1 (Z), Princess-Mika-Test 2-0 (Z), 27turtles 2-0 (T), onlyfans 2-0 (T).

## Observed builds (from its own replays)

**vs GenesisLotus (P), 82.1 min, won:** Drone×98, CreepTumor×18, Overlord×14, Queen×9, CreepTumorQueen×7, Hatchery×4, Extractor×4, EvolutionChamber×2, SpawningPool×1, InfestationPit×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 46 | 35 | 525 | 500 | 34 | 24 |
| 6 | 86 | 57 | 1225 | 1575 | 64 | 33 |
| 8 | 121 | 78 | 2100 | 2550 | 83 | 40 |
| 12 | 139 | 124 | 4575 | 5400 | 87 | 40 |

**vs PolyMorph (Z), 46.1 min, lost:** Drone×89, CreepTumor×37, CreepTumorQueen×15, Overlord×13, Queen×10, Extractor×6, Hatchery×4, EvolutionChamber×2, SpawningPool×1, InfestationPit×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 54 | 35 | 700 | 450 | 37 | 22 |
| 6 | 83 | 63 | 1600 | 1050 | 61 | 44 |
| 8 | 124 | 88 | 2375 | 1075 | 84 | 71 |
| 12 | 173 | 190 | 7225 | 5225 | 109 | 78 |

**vs QueenBot (Z), 45.7 min, lost:** Drone×100, CreepTumor×25, Overlord×13, Queen×9, CreepTumorQueen×6, Hatchery×4, Extractor×4, EvolutionChamber×2, SpawningPool×1, InfestationPit×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 56 | 43 | 875 | 700 | 34 | 30 |
| 6 | 85 | 69 | 1425 | 1575 | 66 | 46 |
| 8 | 122 | 112 | 2525 | 3000 | 86 | 72 |
| 12 | 197 | 186 | 8925 | 7725 | 105 | 84 |

## Strengths

- Enormous economy and remax; strong vs Terran (22-7) when it survives to macro.

## Weaknesses

- Over-drones with a thin army — very punishable by early aggression (weak vs Protoss 14-31 and Zerg 17-39, which pressure the window).
- Poor early defense; leans on queens/spines.

## How to beat it

1. Punish the over-drone window with early pressure or a timing before it remaxes — aggression beats this greed (its P/Z losses show it).
2. Deny creep and expansions.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*