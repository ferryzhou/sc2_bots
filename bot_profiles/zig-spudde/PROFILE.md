# zig-spudde

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio-tank** bot (zig* family): marine + siege tank + liberator. Positional Terran.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~1757 (top-tier ladder bot) |
| **On ladder since** | 2022-08 |
| **Last source update** | 2026-07-08 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio into siege tanks + liberators; standard rax/factory macro.

- Marine/tank/liberator — a splash-heavy, positional Terran that trades with tank support.

## Performance (recent ladder sample)

**Overall: 56–81 (40%)** over 137 decided games (+13 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 21-37 | 36% |
| vs Protoss | 17-19 | 47% |
| vs Zerg | 9-19 | 32% |
| vs Random | 9-6 | 60% |

**Toughest opponents:** TyrT 0-7 (T), 12PoolBot 0-6 (Z), Phobos 0-6 (T), BenBotBC 0-6 (T), Eris 0-5 (Z), theBigBot 1-5 (P), changeling 0-4 (R), Mulebot 0-4 (T).

**Best matchups:** AresRandomExample 4-0 (R), Clicadinha 4-0 (Z), Roro 5-2 (T), ANI_dev 3-0 (T), negativeZero 3-0 (P), Chance 3-0 (R), Deimos 4-2 (P), Apidae 3-1 (P).

## Observed builds (from its own replays)

**vs Roro (T), 48.7 min, won:** SCV×26, Marine×26, SupplyDepot×9, SiegeTank×5, Liberator×3, Refinery×2, Barracks×2, CommandCenter×1, Factory×1, BarracksReactor×1, FactoryTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 44 | 37 | 625 | 300 | 26 | 26 |
| 6 | 63 | 52 | 1900 | 750 | 26 | 37 |
| 8 | 83 | 37 | 3150 | 750 | 26 | 22 |
| 12 | 116 | 18 | 5850 | 0 | 26 | 14 |

**vs Caninana (Z), 43.4 min, lost:** SCV×26, Marine×21, SupplyDepot×8, SiegeTank×4, Liberator×3, Refinery×2, Barracks×2, CommandCenter×1, Factory×1, BarracksReactor×1, FactoryTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 38 | 625 | 650 | 25 | 25 |
| 6 | 64 | 58 | 2125 | 1125 | 25 | 34 |
| 8 | 59 | 74 | 1975 | 1850 | 26 | 32 |
| 12 | 67 | 101 | 2725 | 3325 | 26 | 35 |

**vs buckshot (P), 42.3 min, won:** SCV×26, Marine×21, SupplyDepot×7, SiegeTank×4, Barracks×3, Liberator×3, Refinery×2, CommandCenter×1, Factory×1, BarracksReactor×1, FactoryTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 41 | 625 | 800 | 25 | 19 |
| 6 | 46 | 39 | 1025 | 800 | 25 | 22 |
| 8 | 71 | 58 | 2625 | 1100 | 26 | 32 |
| 12 | 99 | 78 | 4325 | 900 | 26 | 55 |

## Strengths

- Tanks + liberators make frontal attacks costly; splash-resistant.

## Weaknesses

- Losing form (56-81); weak vs Terran (21-37) and Zerg (9-19) — immobility exploited by flanks/drops.

## How to beat it

1. Don't run into sieged tanks/libs — flank, drop, out-position.
2. Multi-prong to exploit mech immobility; win the tank count in the mirror.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*