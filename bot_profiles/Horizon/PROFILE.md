# Horizon

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio/air macro** bot: marine bio off many bases with a Starport (medivacs/liberators/banshees). Macro-oriented. Best vs Protoss (28-16).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1625 (top-tier ladder bot) |
| **On ladder since** | 2026-06 |
| **Last source update** | 2026-06-27 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio expand to 3-4 command centers; barracks marine + starport tech.

- Bio backed by starport units (medivac/liberator/banshee); expands hard and teches to air support.
- Macro-first — out-produces from many bases.

## Performance (recent ladder sample)

**Overall: 63–50 (55%)** over 113 decided games (+37 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 11-8 | 57% |
| vs Protoss | 28-16 | 63% |
| vs Zerg | 23-24 | 48% |
| vs Random | 1-2 | 33% |

**Toughest opponents:** Persephone 0-5 (Z), kas 0-5 (Z), Creepy_duo_canon 0-4 (P), Klakinn 1-4 (P), PiG_Bot 1-3 (P), sharpy_protoss_test1 0-2 (P), zig-reapers 2-3 (T), smokinggunbot 2-3 (T).

**Best matchups:** SharkGull 4-0 (Z), Forgefiend 4-1 (P), Dodo 3-0 (Z), PerilousProtossBot 3-0 (P), OneBaseStalkerBot 3-0 (P), ZEALOCALYPSE 3-1 (P), Apidae 2-0 (P), nida 2-0 (P).

## Observed builds (from its own replays)

**vs GLM_Bot (Z), 73.9 min, won:** SCV×51, SupplyDepot×7, Marine×7, Refinery×5, CommandCenter×4, Barracks×4, Starport×2, BarracksTechLab×2, EngineeringBay×2, Bunker×1, Reaper×1, Factory×1, FactoryTechLab×1, Medivac×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 43 | 250 | 800 | 27 | 28 |
| 6 | 56 | 64 | 850 | 1075 | 41 | 49 |
| 8 | 97 | 113 | 1925 | 1250 | 59 | 84 |
| 12 | 178 | 186 | 6275 | 4850 | 69 | 81 |

**vs PiG_Bot (P), 66.7 min, won:** SCV×50, Marine×6, SupplyDepot×5, Refinery×5, CommandCenter×4, Barracks×4, BarracksTechLab×3, Starport×2, EngineeringBay×2, Bunker×1, Reaper×1, Factory×1, FactoryTechLab×1, Medivac×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 32 | 42 | 250 | 350 | 26 | 34 |
| 6 | 54 | 70 | 850 | 1250 | 39 | 48 |
| 8 | 89 | 100 | 1300 | 2050 | 58 | 66 |
| 12 | 146 | 103 | 3525 | 2550 | 81 | 72 |

**vs QueenBot (Z), 62.9 min, lost:** SCV×51, Marine×8, SupplyDepot×6, Refinery×5, CommandCenter×4, Barracks×3, Starport×2, BarracksTechLab×2, Marauder×2, EngineeringBay×2, Bunker×1, Reaper×1, Factory×1, FactoryTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 45 | 250 | 700 | 27 | 31 |
| 6 | 54 | 69 | 750 | 1575 | 41 | 45 |
| 8 | 93 | 111 | 2125 | 2825 | 59 | 75 |
| 12 | 185 | 147 | 6325 | 4225 | 81 | 83 |

## Strengths

- Strong economy + air support; good vs Protoss (28-16).
- Liberators/banshees add range and harass.

## Weaknesses

- Bio-heavy — splash punishes it; even vs Zerg (23-24).
- Air tech is thin if rushed before it's online.

## How to beat it

1. Splash + anti-air (if it goes banshee/liberator); defend the air harass.
2. Hit an economic timing before its many-base macro snowballs.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*