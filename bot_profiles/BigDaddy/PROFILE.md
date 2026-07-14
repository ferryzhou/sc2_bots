# BigDaddy

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio** bot: mass marine/medivac off many barracks with a starport, into upgrades. Solid form (76-54).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1705 (top-tier ladder bot) |
| **On ladder since** | 2025-11 |
| **Last source update** | 2026-02-09 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio expand; marine-heavy with medivacs, factory/starport support.

- Marine/medivac bio ball with stim + upgrades; drops for pressure.

## Performance (recent ladder sample)

**Overall: 76–54 (58%)** over 130 decided games (+20 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 15-20 | 42% |
| vs Protoss | 27-15 | 64% |
| vs Zerg | 28-17 | 62% |
| vs Random | 6-2 | 75% |

**Toughest opponents:** smokinggunbot 0-3 (T), Visenya 1-3 (Z), Creepy_duo_canon 0-2 (P), RustyNikolaj 0-2 (T), BotTato 0-2 (T), nida 0-2 (P), WaterLeak 1-2 (Z), TheLAW 1-2 (T).

**Best matchups:** Bubu 3-0 (P), Princess-Mika 3-0 (Z), PrimordialOrigin 3-0 (P), 27turtles 3-0 (T), PolyMorph 2-0 (Z), Creepy_canon 2-0 (P), Siriusly 2-0 (R), version_1.0 2-0 (T).

## Observed builds (from its own replays)

**vs smokinggunbot (T), 34.0 min, lost:** Marine×47, SCV×26, SupplyDepot×5, Barracks×4, CommandCenter×1, Refinery×1, BarracksTechLab×1, Factory×1, Starport×1, Medivac×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 34 | 450 | 250 | 21 | 25 |
| 6 | 36 | 41 | 500 | 750 | 21 | 27 |
| 8 | 48 | 43 | 950 | 1175 | 28 | 27 |
| 12 | 60 | 81 | 1750 | 2375 | 29 | 46 |

**vs clone (T), 33.5 min, lost:** Marine×27, SCV×24, SupplyDepot×5, Barracks×3, CommandCenter×2, Refinery×1, BarracksTechLab×1, Factory×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 25 | 750 | 100 | 17 | 19 |
| 6 | 35 | 1 | 1300 | 100 | 8 | 0 |
| 8 | 30 | 1 | 1400 | 100 | 2 | 0 |
| 12 | 32 | 2 | 1550 | 100 | 1 | 1 |

**vs QueenBot (Z), 27.5 min, lost:** Marine×56, SCV×20, SupplyDepot×8, Barracks×6, CommandCenter×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 35 | 46 | 600 | 700 | 20 | 32 |
| 6 | 57 | 41 | 1550 | 0 | 20 | 34 |
| 8 | 77 | 48 | 2550 | 525 | 20 | 34 |
| 12 | 105 | 25 | 4100 | 350 | 20 | 17 |

## Strengths

- Good vs Zerg (28-17) and Protoss (27-15); strong marine count.

## Weaknesses

- Weak vs Terran (15-20); bio-heavy, light on tanks/splash.

## How to beat it

1. Bring splash (banelings, colossus/storm) and defend drops.
2. In the mirror, out-tank and out-position it.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*