# AvocaDEV

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A development build of the **Avocado / AvocaDOS** Terran bio line — marine/marauder bio. Even form (64-69). See AvocaDOS.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1700 (top-tier ladder bot) |
| **On ladder since** | 2025-11 |
| **Last source update** | 2026-03-31 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio (marine/marauder) macro — dev variant.

- Standard MMM bio; a work-in-progress version of the Avocado bots.

## Performance (recent ladder sample)

**Overall: 64–69 (48%)** over 133 decided games (+17 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 23-25 | 47% |
| vs Protoss | 14-19 | 42% |
| vs Zerg | 22-20 | 52% |
| vs Random | 5-5 | 50% |

**Toughest opponents:** Han 1-3 (T), SpeedlingBot 0-2 (Z), Mijik 0-2 (Z), QueenBot 0-2 (Z), Nikolaj 0-2 (T), Clicadinha 0-2 (Z), norman 0-2 (P), Thessaloniki 0-2 (Z).

**Best matchups:** BlackCompany 5-0 (T), SacripantaBot 4-0 (T), Positive_Null 3-0 (Z), Princess-Mika-Test 3-1 (Z), PrimordialOrigin 3-1 (P), LingBaneBot 3-1 (Z), Princess-Mika 3-1 (Z), titania 3-1 (Z).

## Observed builds (from its own replays)

**vs PrimordialOrigin (P), 28.0 min, lost:** Marine×22, SCV×20, SupplyDepot×4, Barracks×2, CommandCenter×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 28 | 36 | 300 | 125 | 20 | 29 |
| 6 | 32 | 60 | 500 | 975 | 20 | 41 |
| 8 | 28 | 86 | 300 | 3150 | 20 | 43 |
| 12 | 1 | 121 | 50 | 7650 | 0 | 34 |

**vs 27turtles (T), 28.0 min, lost:** Marine×27, SCV×20, Barracks×6, SupplyDepot×4, CommandCenter×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 18 | 31 | 300 | 300 | 10 | 24 |
| 6 | 17 | 29 | 500 | 625 | 5 | 17 |
| 8 | 5 | 29 | 250 | 600 | 0 | 15 |
| 12 | 7 | 84 | 300 | 1325 | 0 | 52 |

**vs 49Terrapins (P), 28.0 min, lost:** Marine×53, SCV×20, Barracks×6, SupplyDepot×5, CommandCenter×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 35 | 500 | 350 | 20 | 27 |
| 6 | 44 | 64 | 900 | 1300 | 20 | 43 |
| 8 | 44 | 81 | 900 | 1450 | 20 | 51 |
| 12 | 26 | 167 | 200 | 4475 | 20 | 80 |

## Strengths

- Roughly even across matchups.

## Weaknesses

- Bio-heavy, light on splash; no standout matchup.

## How to beat it

1. Splash + defend drops; out-tank in the mirror.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*