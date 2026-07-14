# Terranosaur

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran mass-marine bio** bot (.NET): marines off 5-6 barracks with upgrades. Bio-macro that grinds. Solid form (80-50), strong vs Protoss (35-18).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1641 (top-tier ladder bot) |
| **On ladder since** | 2026-07 |
| **Last source update** | 2026-07-03 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio expand; heavy barracks marine production with reactors, ebay upgrades, some medivacs.

- Mass marine bio with +attack upgrades; overwhelms with numbers and stim.
- Macro-oriented — reinforces from many barracks.

## Performance (recent ladder sample)

**Overall: 80–50 (61%)** over 130 decided games (+20 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 18-8 | 69% |
| vs Protoss | 35-18 | 66% |
| vs Zerg | 23-22 | 51% |
| vs Random | 4-2 | 66% |

**Toughest opponents:** OneBaseStalkerBot 0-5 (P), PiG_Bot 0-5 (P), kas 0-5 (Z), KoB 1-4 (Z), QueenBot 0-3 (Z), Princess-Mika 0-3 (Z), muravev 0-2 (Z), Thssprtssbt 0-2 (P).

**Best matchups:** 27turtles 5-0 (T), sharpy_protoss_test1 5-0 (P), Klakinn 5-0 (P), Creepy_duo_canon 5-0 (P), Crawler 4-0 (Z), zig-reapers 4-0 (T), Lissy 4-1 (Z), SharkGull 3-0 (Z).

## Observed builds (from its own replays)

**vs Montka (Z), 55.5 min, lost:** SCV×45, Marine×37, SupplyDepot×11, Barracks×6, Refinery×3, BarracksReactor×3, CommandCenter×2, EngineeringBay×2, BarracksTechLab×1, Factory×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 45 | 41 | 400 | 350 | 32 | 31 |
| 6 | 79 | 74 | 1450 | 500 | 44 | 62 |
| 8 | 84 | 141 | 1850 | 3150 | 45 | 70 |
| 12 | 5 | 200 | 400 | 6900 | 1 | 70 |

**vs QueenBot (Z), 37.9 min, lost:** SCV×45, Marine×37, SupplyDepot×10, Barracks×7, Refinery×3, BarracksReactor×3, CommandCenter×2, EngineeringBay×2, BarracksTechLab×1, Factory×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 46 | 300 | 700 | 30 | 32 |
| 6 | 80 | 76 | 1500 | 1400 | 43 | 48 |
| 8 | 82 | 107 | 1850 | 2650 | 45 | 71 |
| 12 | 191 | 120 | 6200 | 1600 | 63 | 88 |

**vs Visenya (Z), 36.3 min, won:** SCV×28, BarracksReactor×9, Marine×5, Barracks×4, BarracksTechLab×3, CommandCenter×2, SupplyDepot×1, Refinery×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 3 | 32 | 0 | 875 | 2 | 10 |
| 6 | 0 | 48 | 0 | 1925 | 0 | 10 |
| 8 | 2 | 62 | 0 | 2725 | 1 | 10 |
| 12 | 10 | 87 | 0 | 4025 | 9 | 10 |

## Strengths

- Strong vs Protoss (35-18) and in the Terran mirror (18-8); high marine count + upgrades.
- Marines with +attack trade well when microed.

## Weaknesses

- Marine-heavy, light on tanks/splash — banelings, colossus, storm, lurkers punish it.
- Even vs Zerg (23-22) where splash is available.

## How to beat it

1. Bring splash (banelings/lurkers as Z, colossus/storm as P, more tanks as T) and don't fight marines in the open.
2. Defend drops; keep armor upgrades to blunt marine +attack.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*