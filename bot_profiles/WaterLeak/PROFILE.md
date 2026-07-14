# WaterLeak

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **roach/ling (and baneling) macro Zerg**. Mixes roach-heavy and mass-ling/baneling styles off a drone economy.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1876 (top-tier ladder bot) |
| **On ladder since** | 2026-02 |
| **Last source update** | 2026-04-12 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Economic Zerg; roach warren + spawning pool, baneling nest available — roach-ling-baneling macro.

- Roach/ling core with banelings vs bio; drone economy + remax.

## Performance (recent ladder sample)

**Overall: 65–55 (54%)** over 120 decided games (+30 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 12-20 | 37% |
| vs Protoss | 16-21 | 43% |
| vs Zerg | 32-12 | 72% |
| vs Random | 5-2 | 71% |

**Toughest opponents:** clone 0-2 (T), 27turtles 0-2 (T), muravev 0-2 (Z), BotTato 0-2 (T), Mulebot 0-2 (T), Zozo 0-2 (P), PerilousProtossBot 0-2 (P), Eris 0-2 (Z).

**Best matchups:** Clicadinha 3-0 (Z), Princess-Mika 3-0 (Z), Princess-Mika-Test 2-0 (Z), BigDaddy 2-0 (T), SharkGull 2-0 (Z), Laser-Circus 2-0 (P), WickedBot 2-0 (T), version_2.0 2-0 (T).

## Observed builds (from its own replays)

**vs 27turtles (T), 43.9 min, lost:** Roach×25, Drone×19, Overlord×7, Hatchery×1, SpawningPool×1, Extractor×1, RoachWarren×1, Queen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 44 | 32 | 1275 | 200 | 16 | 25 |
| 6 | 36 | 46 | 875 | 575 | 16 | 29 |
| 8 | 34 | 70 | 775 | 1675 | 16 | 41 |
| 12 | 30 | 121 | 575 | 3525 | 16 | 64 |

**vs 72Tortoises (Z), 42.9 min, lost:** Zergling×64, Drone×44, Overlord×7, Queen×4, Hatchery×2, SpawningPool×1, Extractor×1, BanelingNest×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 41 | 50 | 900 | 1150 | 18 | 26 |
| 6 | 60 | 69 | 1750 | 1050 | 29 | 44 |
| 8 | 43 | 73 | 1575 | 1125 | 19 | 48 |
| 12 | 42 | 128 | 1500 | 3750 | 22 | 72 |

**vs Roro (T), 21.0 min, lost:** Roach×25, Drone×19, Overlord×8, Hatchery×1, SpawningPool×1, Extractor×1, RoachWarren×1, Queen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 37 | 1175 | 300 | 16 | 28 |
| 6 | 58 | 27 | 1975 | 400 | 16 | 15 |
| 8 | 44 | 14 | 1275 | 525 | 16 | 4 |
| 12 | 34 | 59 | 775 | 950 | 16 | 40 |

## Strengths

- Strong vs Zerg (32-12); banelings give it splash vs light armies.

## Weaknesses

- Weak vs Protoss (16-21) and Terran (12-20) in-sample — colossus/tanks out-range roaches.

## How to beat it

1. Out-range roaches (colossus, tanks, tempest) and keep splash for the ling/bane.
2. Hit a timing before its remax; deny creep.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*