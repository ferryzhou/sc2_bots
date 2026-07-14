# smokinggunbot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio-tank turtle** (Java): marine + siege tank + bunkers. Positional, defensive Terran. Strong form (83-43), esp. vs Terran (36-10) and Protoss (30-13).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | java |
| **AI Arena Elo** | ~1602 (top-tier ladder bot) |
| **On ladder since** | 2025-01 |
| **Last source update** | 2026-07-12 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bunkered bio expand into siege tanks; defensive positioning.

- Marine/tank behind bunkers — a positional turtle that trades with tank splash and defender's advantage.
- Grinds a strong mid-game from a fortified position.

## Performance (recent ladder sample)

**Overall: 83–43 (65%)** over 126 decided games (+24 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 36-10 | 78% |
| vs Protoss | 30-13 | 69% |
| vs Zerg | 12-19 | 38% |
| vs Random | 5-1 | 83% |

**Toughest opponents:** muravevtest 0-7 (Z), muravevProtoss 0-5 (P), muravev 1-4 (Z), muravevTerranV2 0-3 (T), WaterLeak 0-2 (Z), VeTerran_another 0-2 (T), 49Terrapins 3-4 (P), Princess-Mika 1-2 (Z).

**Best matchups:** BlackCompany 7-0 (T), Positive_Null 6-0 (Z), GhostProtocol 6-0 (T), BotTato 7-2 (T), DSSTL 7-2 (P), oberon 6-1 (T), Laser-Circus 5-0 (P), PrimordialOrigin 5-0 (P).

## Observed builds (from its own replays)

**vs BotTato (T), 74.4 min, lost:** SCV×33, Marine×12, SupplyDepot×6, Refinery×4, CommandCenter×2, Barracks×2, Bunker×2, BarracksReactor×2, EngineeringBay×1, Factory×1, FactoryTechLab×1, Reaper×1, MissileTurret×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 30 | 350 | 200 | 20 | 25 |
| 6 | 41 | 46 | 700 | 875 | 27 | 32 |
| 8 | 49 | 70 | 700 | 1925 | 34 | 39 |
| 12 | 93 | 109 | 2575 | 3625 | 51 | 53 |

**vs muravevtest (Z), 67.0 min, lost:** SCV×25, Marine×14, SupplyDepot×5, CommandCenter×2, Barracks×2, Refinery×2, Bunker×2, BarracksReactor×2, Factory×1, FactoryTechLab×1, EngineeringBay×1, Starport×1, SiegeTank×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 28 | 36 | 200 | 525 | 23 | 30 |
| 6 | 32 | 58 | 400 | 925 | 24 | 44 |
| 8 | 51 | 70 | 1300 | 1275 | 27 | 50 |
| 12 | 80 | 173 | 2125 | 3875 | 43 | 97 |

**vs Laser-Circus (P), 46.7 min, won:** SCV×24, Marine×16, SupplyDepot×6, CommandCenter×2, Barracks×2, Refinery×2, Bunker×2, BarracksReactor×2, Factory×1, EngineeringBay×1, FactoryTechLab×1, Starport×1, StarportTechLab×1, MissileTurret×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 34 | 350 | 200 | 23 | 28 |
| 6 | 36 | 62 | 600 | 775 | 24 | 42 |
| 8 | 46 | 62 | 1175 | 1150 | 25 | 46 |
| 12 | 75 | 124 | 1625 | 4500 | 49 | 62 |

## Strengths

- Very hard to attack head-on (bunkers + sieged tanks); dominant vs Terran (36-10) and Protoss (30-13).
- Tank splash punishes mass-light attacks.

## Weaknesses

- Weak vs Zerg (12-19) — mass ling/roach + flanks and multi-prong stretch the immobile defense.
- Immobile — cedes map; slow to punish greed.

## How to beat it

1. Don't attack into sieged tanks/bunkers — flank, drop, multi-prong (as Zerg, mass + runbys work).
2. Out-expand the turtle and take the map; pick off tanks with range/air.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*