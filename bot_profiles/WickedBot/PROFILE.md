# WickedBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio** bot (marine/medivac + engineering-bay upgrades, bunker defense). Standard MMM macro.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1940 (top-tier ladder bot) |
| **On ladder since** | 2024-11 |
| **Last source update** | 2026-07-11 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio expand with early bunker; marine/medivac into upgrades, factory for support.

- Marine + medivac bio with upgrades; bunker-safe expansion into a macro game.

## Performance (recent ladder sample)

**Overall: 59–63 (48%)** over 122 decided games (+28 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 10-25 | 28% |
| vs Protoss | 17-13 | 56% |
| vs Zerg | 28-21 | 57% |
| vs Random | 4-4 | 50% |

**Toughest opponents:** Saimon 0-6 (Z), VeTerran_another 0-5 (T), PhantomTest 2-6 (Z), ANI_dev 1-5 (T), 27turtles 2-4 (T), Klakinn 2-4 (P), clone 1-3 (T), zig-spudde 0-2 (T).

**Best matchups:** 72Tortoises 7-1 (Z), zig-reapers 6-1 (T), QueenBot 6-3 (Z), Dodo 5-2 (Z), nida 5-2 (P), AresRandomExample 4-2 (R), Crawler 2-0 (Z), smallBly 2-0 (Z).

## Observed builds (from its own replays)

**vs QueenBot (Z), 52.1 min, won:** SCV×44, Marine×21, SupplyDepot×7, CommandCenter×3, Barracks×3, Refinery×3, Medivac×3, EngineeringBay×2, Bunker×1, BarracksReactor×1, Factory×1, BarracksTechLab×1, Starport×1, FactoryReactor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 35 | 49 | 200 | 700 | 26 | 35 |
| 6 | 60 | 86 | 1225 | 1575 | 36 | 51 |
| 8 | 85 | 110 | 1750 | 3425 | 46 | 64 |
| 12 | 150 | 66 | 3625 | 775 | 84 | 46 |

**vs QueenBot (Z), 47.6 min, won:** SCV×43, Marine×20, SupplyDepot×7, Medivac×4, CommandCenter×3, Barracks×3, Refinery×3, EngineeringBay×2, Bunker×1, BarracksReactor×1, Factory×1, BarracksTechLab×1, Starport×1, FactoryReactor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 35 | 49 | 250 | 700 | 25 | 36 |
| 6 | 62 | 86 | 1225 | 1575 | 35 | 51 |
| 8 | 79 | 99 | 1475 | 2450 | 47 | 63 |
| 12 | 131 | 101 | 2475 | 2450 | 76 | 57 |

**vs QueenBot (Z), 47.4 min, won:** SCV×44, Marine×20, SupplyDepot×8, Medivac×4, CommandCenter×3, Barracks×3, Refinery×3, EngineeringBay×2, Bunker×1, BarracksReactor×1, Factory×1, BarracksTechLab×1, Starport×1, FactoryReactor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 49 | 250 | 700 | 26 | 36 |
| 6 | 62 | 85 | 1225 | 1575 | 38 | 53 |
| 8 | 84 | 108 | 1825 | 3075 | 46 | 65 |
| 12 | 115 | 116 | 2275 | 2175 | 66 | 66 |

## Strengths

- Competitive vs Zerg (28-21) and Protoss (17-13); safe bunkered openings.

## Weaknesses

- Weak vs Terran (10-25) — loses the mirror on tanks/positioning.
- Bio-heavy — light on splash; melts to colossus/storm/banelings.

## How to beat it

1. As Terran, get more tanks and better position — the mirror favors you.
2. Bring splash (P/Z); defend drops; hold defensive ground.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*