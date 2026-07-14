# clone

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran** bot (reaper opening into starport tech). Even-to-losing form (61-72). (From the opponents pool; reaper/air-leaning.)

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1648 (top-tier ladder bot) |
| **On ladder since** | 2025-07 |
| **Last source update** | 2026-05-19 |
| **Source public** | yes (Python source publicly downloadable; this profile is from replays + record) |

## Strategy

**Opening:** Reaper opening (KD8) into starport tech; bio/air mix.

- Reaper harass early into a starport-based bio/air macro.

## Performance (recent ladder sample)

**Overall: 61–72 (45%)** over 133 decided games (+17 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 24-16 | 60% |
| vs Protoss | 18-18 | 50% |
| vs Zerg | 15-27 | 35% |
| vs Random | 4-11 | 26% |

**Toughest opponents:** Saimon 0-5 (Z), 12PoolBot 0-4 (Z), Phobos 0-3 (T), changeling 0-3 (R), Roro 0-3 (T), Caninana 0-3 (Z), Eris 0-3 (Z), Xena 0-3 (R).

**Best matchups:** Klakinn 4-1 (P), theBigBot 3-0 (P), ANI_dev 3-0 (T), zig-reapers 3-0 (T), Apidae 3-0 (P), Clicadinha 3-1 (Z), Siriusly 2-0 (R), Mulebot 2-0 (T).

## Observed builds (from its own replays)

**vs Roro (T), 79.9 min, lost:** SCV×48, Refinery×6, Marine×6, CommandCenter×5, SupplyDepot×5, Starport×2, Barracks×1, Factory×1, Reaper×1, KD8Charge×1, FactoryTechLab×1, BarracksTechLab×1, SiegeTank×1, FusionCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 35 | 34 | 275 | 300 | 27 | 26 |
| 6 | 54 | 60 | 425 | 1250 | 40 | 36 |
| 8 | 76 | 96 | 1125 | 2400 | 53 | 51 |
| 12 | 29 | 164 | 150 | 6350 | 16 | 73 |

**vs nida (P), 79.6 min, lost:** SCV×43, SupplyDepot×7, Refinery×4, CommandCenter×3, Barracks×3, BarracksTechLab×2, SiegeTank×2, MissileTurret×2, Marine×2, BarracksReactor×2, Factory×1, Reaper×1, FactoryTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 29 | 40 | 0 | 800 | 25 | 23 |
| 6 | 48 | 60 | 850 | 2325 | 36 | 26 |
| 8 | 47 | 48 | 1650 | 3300 | 20 | 8 |
| 12 | 31 | 39 | 50 | 3025 | 24 | 3 |

**vs nida (P), 52.7 min, lost:** SCV×33, Marine×7, SupplyDepot×5, Barracks×4, CommandCenter×3, BarracksReactor×3, Refinery×2, BarracksTechLab×2, SiegeTank×2, Marauder×2, MissileTurret×2, Factory×1, Reaper×1, KD8Charge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 23 | 35 | 0 | 600 | 23 | 26 |
| 6 | 45 | 54 | 1000 | 1550 | 28 | 27 |
| 8 | 75 | 77 | 1875 | 3475 | 37 | 27 |
| 12 | 64 | 113 | 1150 | 4825 | 37 | 46 |

## Strengths

- Competitive in the Terran mirror (24-16).

## Weaknesses

- Weak vs Random (4-11) and Zerg (15-27); light, harass-oriented.

## How to beat it

1. Defend the reaper/air harass (turrets/keep-back units), then out-macro.
2. Bring anti-air if it goes starport; splash its bio.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*