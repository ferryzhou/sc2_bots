# tito

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **macro Zerg** (C++): heavy drone economy, creep spread, into roach/ling with queens. Economy-first Zerg.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~2036 (top-tier ladder bot) |
| **On ladder since** | 2026-02 |
| **Last source update** | 2026-07-13 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Hatch-first economic Zerg; fast drones + creep, roach warren, queens for injects/defense.

- Drone hard, spread creep, remax roach/ling; play the long macro game.

## Performance (recent ladder sample)

**Overall: 72–44 (62%)** over 116 decided games (+34 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 19-3 | 86% |
| vs Protoss | 32-15 | 68% |
| vs Zerg | 15-26 | 36% |
| vs Random | 6-0 | 100% |

**Toughest opponents:** negativeZero 0-6 (P), WaterLeak 0-4 (Z), 72Tortoises 0-3 (Z), EPNRoach 1-3 (Z), Princess-Mika 1-3 (Z), SharkGull 0-2 (Z), Clicadinha 0-2 (Z), Princess-Mika-Test 1-2 (Z).

**Best matchups:** TheLAW 3-0 (T), QueenBot 3-0 (Z), puck 3-0 (P), SiriusBot 3-0 (R), DoopyBot 3-0 (Z), Siriusly 3-0 (R), 27turtles 3-0 (T), WildLupo 3-0 (P).

## Observed builds (from its own replays)

**vs PolyMorph (Z), 54.1 min, won:** Drone×59, CreepTumor×15, Overlord×10, CreepTumorQueen×8, Extractor×6, Queen×6, Roach×5, Zergling×4, Hatchery×3, EvolutionChamber×2, SpawningPool×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 45 | 39 | 525 | 850 | 36 | 24 |
| 6 | 62 | 56 | 1025 | 925 | 44 | 38 |
| 8 | 97 | 51 | 1825 | 500 | 69 | 41 |
| 12 | 115 | 36 | 2575 | 475 | 80 | 26 |

**vs 72Tortoises (Z), 43.1 min, lost:** Drone×60, Overlord×8, Zergling×4, Queen×4, Hatchery×3, Extractor×3, SpawningPool×1, CreepTumorQueen×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 47 | 48 | 525 | 1250 | 35 | 23 |
| 6 | 29 | 73 | 175 | 1650 | 27 | 39 |
| 8 | 29 | 114 | 175 | 3150 | 27 | 57 |
| 12 | 29 | 167 | 175 | 5550 | 27 | 90 |

**vs PolyMorph (Z), 37.3 min, lost:** Drone×51, Zergling×26, Overlord×10, CreepTumor×8, CreepTumorQueen×6, Queen×5, Hatchery×3, Extractor×3, SpawningPool×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 32 | 675 | 875 | 22 | 15 |
| 6 | 62 | 34 | 825 | 850 | 46 | 16 |
| 8 | 68 | 46 | 1500 | 800 | 49 | 28 |
| 12 | 112 | 88 | 1725 | 875 | 81 | 63 |

## Strengths

- Strong economy; good vs Protoss (32-15) and Terran (19-3) in-sample.

## Weaknesses

- Surprisingly weak in the Zerg mirror (15-26) — loses to more aggressive speedling/roach timings.
- Standard macro-Zerg vulnerability to splash and to sharp timings pre-remax.

## How to beat it

1. As Zerg, out-aggress it — speedling/roach pressure before its economy snowballs (the mirror record shows aggression works).
2. As T/P, bring splash and hit a timing before it remaxes.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*