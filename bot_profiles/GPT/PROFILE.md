# GPT

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio-tank** macro bot (marine/marauder + siege tanks). Solid mech-flavored bio that grinds positional games.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~2056 (top-tier ladder bot) |
| **On ladder since** | 2024-07 |
| **Last source update** | 2026-07-01 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio into tanks off 2-3 bases; reactor/tech-lab barracks, factory for tanks, engineering-bay upgrades.

- Marine/marauder backed by siege tanks — a positional, splash-heavy Terran.
- Macro-oriented, trades with tank support and upgrades.

## Performance (recent ladder sample)

**Overall: 75–69 (52%)** over 144 decided games (+6 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 18-34 | 34% |
| vs Protoss | 23-14 | 62% |
| vs Zerg | 24-10 | 70% |
| vs Random | 10-11 | 47% |

**Toughest opponents:** BenBotBC 0-9 (T), ANIbot 0-8 (T), Eris 0-6 (Z), Roro 2-6 (T), Aeolus 1-5 (P), Xena 2-5 (R), changeling 2-4 (R), Deimos 2-4 (P).

**Best matchups:** 12PoolBot 9-1 (Z), Caninana 7-1 (Z), theBigBot 6-0 (P), TyrT 5-1 (T), norman 4-0 (P), Clicadinha 4-0 (Z), buckshot 3-0 (P), PhantomTest 3-0 (Z).

## Observed builds (from its own replays)

**vs negativeZero (P), 64.0 min, lost:** SCV×47, Marine×19, SupplyDepot×11, Refinery×4, Barracks×3, SiegeTank×3, CommandCenter×2, Marauder×2, EngineeringBay×2, BarracksReactor×1, Factory×1, FactoryTechLab×1, BarracksTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 38 | 300 | 300 | 23 | 31 |
| 6 | 65 | 66 | 1275 | 2100 | 36 | 41 |
| 8 | 97 | 105 | 2800 | 4325 | 46 | 52 |
| 12 | 113 | 81 | 3250 | 3150 | 46 | 40 |

**vs zig-spudde (T), 34.2 min, lost:** Marine×40, SCV×20, SupplyDepot×7, Barracks×5, Marauder×5, CommandCenter×1, Refinery×1, EngineeringBay×1, BarracksReactor×1, BarracksTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 43 | 775 | 625 | 20 | 25 |
| 6 | 47 | 41 | 1200 | 750 | 20 | 25 |
| 8 | 40 | 46 | 725 | 900 | 20 | 25 |
| 12 | 47 | 44 | 1250 | 1100 | 20 | 25 |

**vs Roro (T), 27.5 min, lost:** SCV×47, Marine×23, SupplyDepot×11, Barracks×4, Refinery×4, SiegeTank×3, CommandCenter×2, Medivac×2, EngineeringBay×2, Factory×1, BarracksReactor×1, FactoryTechLab×1, BarracksTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 37 | 200 | 300 | 25 | 26 |
| 6 | 69 | 65 | 1350 | 1500 | 39 | 37 |
| 8 | 75 | 83 | 1525 | 1900 | 46 | 50 |
| 12 | 99 | 154 | 3550 | 5150 | 40 | 78 |

## Strengths

- Tank support makes it splash-resistant vs mass light; strong vs Zerg (24-10).

## Weaknesses

- Weak vs Terran in-sample (18-34) — loses the mech/tank mirror on positioning.
- Tanks are immobile; multi-pronged pressure and drops stretch it.

## How to beat it

1. Don't run mass light into sieged tanks — flank, drop, or out-position.
2. In the Terran mirror, win the tank count and high ground.
3. Air (that it can't easily answer) and multi-prong exploit tank immobility.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*