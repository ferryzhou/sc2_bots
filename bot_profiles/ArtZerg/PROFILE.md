# ArtZerg

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

An **aggressive ling/roach Zerg**: mass zerglings (60+) with roach support off a modest economy. Aggro-leaning macro; losing recent form (62-71).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1642 (top-tier ladder bot) |
| **On ladder since** | 2026-03 |
| **Last source update** | 2026-03-27 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Fast pool into mass zergling + roach warren; ling pressure into roach.

- Zergling flood with roach backup; pressure early, macro if held.

## Performance (recent ladder sample)

**Overall: 62–71 (46%)** over 133 decided games (+17 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 11-32 | 25% |
| vs Protoss | 12-25 | 32% |
| vs Zerg | 34-12 | 73% |
| vs Random | 5-2 | 71% |

**Toughest opponents:** nida 0-4 (P), PiG_Bot 0-4 (P), onlyfans 0-4 (T), BigDaddy 0-4 (T), norman 1-4 (P), TheLAW 1-4 (T), Nothing 1-4 (P), 27turtles 1-4 (T).

**Best matchups:** QueenBot 4-0 (Z), Lissy 3-0 (Z), clone 3-1 (T), DoopyBot 2-0 (Z), DoopyBot-Test 2-0 (Z), MindMatrix 2-0 (Z), SharkGull 2-0 (Z), muravev 3-2 (Z).

## Observed builds (from its own replays)

**vs Mulebot (T), 79.0 min, lost:** Zergling×66, Drone×23, Overlord×8, Roach×8, Hatchery×2, Extractor×1, SpawningPool×1, RoachWarren×1, Queen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 38 | 38 | 925 | 250 | 19 | 28 |
| 6 | 48 | 13 | 1300 | 550 | 19 | 7 |
| 8 | 39 | 11 | 875 | 200 | 19 | 7 |
| 12 | 82 | 4 | 3125 | 400 | 19 | 0 |

**vs Lissy (Z), 54.2 min, won:** Zergling×42, Drone×15, Overlord×2, Hatchery×1, SpawningPool×1, SpineCrawler×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 14 | 0 | 375 | 0 | 5 | 0 |
| 6 | 18 | 0 | 625 | 0 | 5 | 0 |
| 8 | 22 | 0 | 825 | 0 | 5 | 0 |
| 12 | 30 | 0 | 1225 | 0 | 5 | 0 |

**vs 27turtles (T), 43.9 min, lost:** Zergling×50, Drone×24, Roach×8, Overlord×7, Hatchery×2, Extractor×1, SpawningPool×1, RoachWarren×1, Queen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 39 | 35 | 1025 | 350 | 16 | 23 |
| 6 | 26 | 49 | 750 | 400 | 13 | 35 |
| 8 | 22 | 75 | 550 | 1050 | 13 | 49 |
| 12 | 13 | 124 | 250 | 2075 | 8 | 69 |

## Strengths

- Dominant in the Zerg mirror (34-12); early ling aggression can overwhelm.

## Weaknesses

- Weak vs Terran (11-32) and Protoss (12-25) — splash (tanks/hellions, colossus/storm) shreds ling/roach.
- Melee-heavy, light on tech.

## How to beat it

1. Wall + splash and hold the ling flood; out-range roaches (tanks/colossus).
2. Punish its thin economy once the aggression is spent.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*