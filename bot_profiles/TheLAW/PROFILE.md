# TheLAW

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **Terran bio** macro bot: marine/marauder/medivac with upgrades. Excellent form (85-39), strong across the board (esp. Protoss 32-13).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1619 (top-tier ladder bot) |
| **On ladder since** | 2025-11 |
| **Last source update** | 2026-06-04 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio expand; marine/marauder with medivacs, reactors/tech-labs, ebay upgrades.

- Clean MMM bio macro with stim + upgrades and medivac drops; trades bio efficiently.
- Balanced army/economy — wins on execution.

## Performance (recent ladder sample)

**Overall: 85–39 (68%)** over 124 decided games (+26 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 19-8 | 70% |
| vs Protoss | 32-13 | 71% |
| vs Zerg | 27-16 | 62% |
| vs Random | 7-2 | 77% |

**Toughest opponents:** tito 0-3 (Z), smokinggunbot 0-3 (T), Nothing 0-2 (P), WaterLeak 0-2 (Z), Creepy_canon 0-2 (P), Apidae 0-2 (P), 27turtles 1-2 (T), EPNRoach 1-2 (Z).

**Best matchups:** PrimordialOrigin 5-0 (P), Bubu 4-0 (P), Laser-Circus 4-0 (P), GenesisLotus 4-0 (P), SiriusBot 4-0 (R), MY_SCRIPTING_SON 3-0 (Z), version_1.0 3-0 (T), muravev 3-0 (Z).

## Observed builds (from its own replays)

**vs 27turtles (T), 31.6 min, won:** SCV×44, Marine×23, SupplyDepot×6, Barracks×4, Refinery×3, CommandCenter×2, Medivac×2, BarracksTechLab×1, Factory×1, Starport×1, StarportTechLab×1, FusionCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 32 | 200 | 200 | 24 | 25 |
| 6 | 50 | 52 | 500 | 850 | 35 | 37 |
| 8 | 38 | 69 | 400 | 1100 | 21 | 45 |
| 12 | 36 | 78 | 1650 | 2825 | 16 | 31 |

**vs Creepy_canon (P), 28.0 min, lost:** SCV×22, Barracks×3, SupplyDepot×2, Marine×2, CommandCenter×1, Refinery×1, BarracksTechLab×1, Factory×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 1 | 13 | 0 | 0 | 1 | 12 |
| 6 | 1 | 12 | 0 | 0 | 1 | 11 |
| 8 | 1 | 10 | 0 | 0 | 1 | 9 |
| 12 | 1 | 8 | 0 | 0 | 1 | 7 |

**vs Creepy_canon (P), 27.9 min, lost:** SCV×24, Barracks×3, SupplyDepot×2, Marine×2, CommandCenter×1, Refinery×1, BarracksTechLab×1, Factory×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 2 | 14 | 0 | 0 | 1 | 13 |
| 6 | 1 | 12 | 0 | 0 | 1 | 12 |
| 8 | 1 | 10 | 0 | 0 | 1 | 9 |
| 12 | 1 | 8 | 0 | 0 | 1 | 7 |

## Strengths

- Well-rounded and strong; dominant vs Protoss (32-13) and Zerg (27-16).
- Good macro + drop harass.

## Weaknesses

- Bio-centric — splash (colossus/storm, banelings/lurkers) is the answer; lighter on tanks.

## How to beat it

1. Force splash-favorable fights and defend drops.
2. Don't fight stimmed bio in the open; use position and armor upgrades.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*