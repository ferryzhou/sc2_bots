# JimmyBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

The **Random** member of the Jimmy family. In-sample it played Zerg (both a 100-zergling flood and a roach/creep macro), so expect a Zerg-heavy, variable game — but the race is random.

## Identity

| | |
|---|---|
| **Race** | Random |
| **Bot type** | python |
| **AI Arena Elo** | ~1860 (top-tier ladder bot) |
| **On ladder since** | 2026-03 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Random race; observed Zerg lines ranged from a mass-ling all-in (100 lings) to a roach macro with creep.

- Race and build vary — from aggressive ling floods to standard macro.

## Performance (recent ladder sample)

**Overall: 71–74 (48%)** over 145 decided games (+5 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 12-28 | 30% |
| vs Protoss | 21-16 | 56% |
| vs Zerg | 33-27 | 55% |
| vs Random | 3-2 | 60% |
| vs ? | 2-1 | 66% |

**Toughest opponents:** TheLAW 0-4 (T), clone 0-4 (T), norman 0-3 (P), onlyfans 0-3 (T), QueenBot 1-3 (Z), nida 1-3 (P), 27turtles 1-3 (T), 72Tortoises 1-3 (Z).

**Best matchups:** Princess-Mika 3-0 (Z), PiG_Bot 3-1 (P), Crawler 3-1 (Z), 49Terrapins 2-0 (P), MY_SCRIPTING_SON 2-0 (Z), Tyckles 2-0 (P), PrimordialOrigin 2-0 (P), gotest 2-0 (Z).

## Observed builds (from its own replays)

**vs muravev (Z), 65.4 min, lost:** Zergling×100, Drone×15, Overlord×7, Hatchery×2, Queen×2, SpawningPool×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 10 | 850 | 0 | 13 | 9 |
| 6 | 52 | 5 | 1875 | 0 | 13 | 4 |
| 8 | 68 | 14 | 2875 | 0 | 13 | 13 |
| 12 | 104 | 23 | 4375 | 0 | 13 | 21 |

**vs QueenBot (Z), 45.2 min, won:** Drone×55, Roach×13, Overlord×12, CreepTumor×9, Extractor×4, CreepTumorQueen×4, Hatchery×3, Queen×3, Changeling×2, EvolutionChamber×2, SpawningPool×1, RoachWarren×1, HydraliskDen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 44 | 46 | 450 | 700 | 28 | 31 |
| 6 | 68 | 73 | 1250 | 1575 | 45 | 45 |
| 8 | 101 | 109 | 2325 | 2475 | 53 | 74 |
| 12 | 200 | 134 | 6350 | 2300 | 86 | 90 |

**vs RustyNikolaj (T), 39.0 min, lost:** SCV×47, Marine×25, SupplyDepot×6, CommandCenter×5, Barracks×4, Refinery×2, BarracksTechLab×1, Factory×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 34 | 300 | 575 | 25 | 22 |
| 6 | 59 | 56 | 800 | 1425 | 38 | 30 |
| 8 | 65 | 76 | 850 | 2225 | 43 | 42 |
| 12 | 94 | 118 | 1200 | 4600 | 60 | 59 |

## Strengths

- Unpredictable; the ling-flood branch can overwhelm the unprepared.

## Weaknesses

- Losing recent form (71-74); weak vs Terran (12-28) — splash beats the ling branch.

## How to beat it

1. Scout the race and build; if it's the ling flood, wall + splash + hold.
2. As Terran, tanks/hellions dominate its aggressive Zerg branch.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*