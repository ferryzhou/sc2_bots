# BotTato

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran mech/reaper** bot: reaper + KD8-charge harass into siege tanks and factory tech. Positional mech.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1909 (top-tier ladder bot) |
| **On ladder since** | 2024-09 |
| **Last source update** | 2026-07-04 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Reaper opening with KD8 charges (worker harass), into command centers + factory/siege tanks — a mech-leaning macro.

- Reaper harass early (KD8 charges snipe workers), then siege tanks + mech for a positional mid-game.

## Performance (recent ladder sample)

**Overall: 38–75 (33%)** over 113 decided games (+37 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 15-28 | 34% |
| vs Protoss | 15-22 | 40% |
| vs Zerg | 4-23 | 14% |
| vs Random | 4-2 | 66% |

**Toughest opponents:** smokinggunbot 0-8 (T), Positive_Null 0-7 (Z), muravev 0-5 (Z), muravevProtoss 0-5 (P), Gordon 1-5 (T), Crawler 0-4 (Z), GenesisLotus 1-4 (P), Alexa 3-5 (T).

**Best matchups:** BlackCompany 4-0 (T), GhostProtocol 4-0 (T), DSSTL 3-0 (P), PrimordialOrigin 4-2 (P), CtrlZedPY 3-1 (R), Laser-Circus 3-2 (P), miniTestikZ 1-0 (Z), AvocaDOS 1-0 (T).

## Observed builds (from its own replays)

**vs Laser-Circus (P), 66.2 min, won:** SCV×35, KD8Charge×6, SupplyDepot×4, Refinery×4, Marine×4, Reaper×3, CommandCenter×2, Barracks×2, Factory×2, SiegeTank×2, BarracksReactor×1, FactoryTechLab×1, Starport×1, EngineeringBay×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 28 | 39 | 100 | 400 | 25 | 27 |
| 6 | 35 | 56 | 675 | 850 | 24 | 38 |
| 8 | 46 | 83 | 1000 | 1650 | 28 | 51 |
| 12 | 63 | 149 | 1725 | 5425 | 40 | 59 |

**vs DSSTL (P), 59.9 min, won:** SCV×35, Marine×8, SupplyDepot×7, Refinery×5, Reaper×4, CommandCenter×3, Barracks×3, KD8Charge×3, BarracksReactor×2, SiegeTank×2, Factory×1, FactoryTechLab×1, Starport×1, Medivac×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 30 | 29 | 200 | 0 | 25 | 27 |
| 6 | 49 | 44 | 925 | 0 | 32 | 41 |
| 8 | 66 | 69 | 1925 | 0 | 38 | 56 |
| 12 | 104 | 124 | 3675 | 3200 | 52 | 80 |

**vs PrimordialOrigin (P), 43.3 min, won:** SCV×35, SupplyDepot×5, Refinery×5, KD8Charge×4, Marine×4, CommandCenter×3, Barracks×3, Reaper×3, Factory×2, BarracksReactor×2, FactoryTechLab×2, Starport×1, SiegeTank×1, Medivac×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 29 | 36 | 200 | 125 | 25 | 29 |
| 6 | 41 | 62 | 725 | 1100 | 31 | 41 |
| 8 | 68 | 83 | 1450 | 2225 | 38 | 44 |
| 12 | 42 | 107 | 2225 | 4875 | 16 | 44 |

## Strengths

- Reaper harass pressures economies; tanks give splash and hold ground.

## Weaknesses

- Rough recent form (38-75) — weak vs Zerg (4-23): mass ling/roach + flanks beat slow mech.
- Mech immobility — drops and multi-prong stretch it.

## How to beat it

1. As Zerg, swarm and flank the immobile mech (sample: 23-4 for Zerg).
2. Defend the reaper harass (keep-back units), then exploit tank immobility.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*