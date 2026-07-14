# AvocaDOS

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio** bot (Avocado family): marine/marauder off many barracks. Even-ish form.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1741 (top-tier ladder bot) |
| **On ladder since** | 2025-11 |
| **Last source update** | 2026-06-07 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio expand; marine/marauder with reactor/tech-lab barracks.

- Standard MMM bio macro with upgrades.

## Performance (recent ladder sample)

**Overall: 58–63 (47%)** over 121 decided games (+29 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 7-30 | 18% |
| vs Protoss | 23-11 | 67% |
| vs Zerg | 23-18 | 56% |
| vs Random | 5-4 | 55% |

**Toughest opponents:** MicroMachine 0-5 (T), WickedBot 0-4 (T), 12PoolBot 0-4 (Z), Roro 0-4 (T), GPT 0-4 (T), TyrT 0-4 (T), PhantomTest 0-3 (Z), SharpenedEdge 0-3 (P).

**Best matchups:** PerilousProtossBot 3-0 (P), LordSuperKing 3-0 (P), LunaxVRR 3-0 (P), KerrigansTorment 3-0 (Z), Sharkling 3-0 (Z), Dodo 3-0 (Z), Zozo 3-1 (P), whalemean 3-1 (R).

## Observed builds (from its own replays)

**vs WickedBot (T), 58.1 min, lost:** SCV×52, Marine×23, SupplyDepot×8, Marauder×8, CommandCenter×4, Barracks×4, Refinery×2, BarracksTechLab×2, BarracksReactor×1, EngineeringBay×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 38 | 32 | 400 | 100 | 25 | 26 |
| 6 | 68 | 58 | 1225 | 950 | 37 | 36 |
| 8 | 89 | 93 | 1400 | 2025 | 56 | 47 |
| 12 | 100 | 140 | 3350 | 2600 | 25 | 83 |

**vs sharkbot (P), 51.8 min, lost:** SCV×38, Marine×27, SupplyDepot×6, Marauder×6, Barracks×4, CommandCenter×2, Refinery×2, BarracksTechLab×2, EngineeringBay×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 44 | 42 | 775 | 975 | 25 | 25 |
| 6 | 54 | 52 | 1025 | 1725 | 31 | 30 |
| 8 | 55 | 51 | 350 | 1300 | 40 | 33 |
| 12 | 120 | 85 | 1750 | 2725 | 73 | 48 |

**vs KerrigansTorment (Z), 35.3 min, won:** SCV×24, SupplyDepot×5, Marine×4, Barracks×2, BarracksTechLab×2, Marauder×2, CommandCenter×1, Refinery×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 8 | 36 | 450 | 925 | 0 | 12 |
| 6 | 2 | 36 | 125 | 1075 | 0 | 12 |
| 8 | 5 | 50 | 100 | 1850 | 1 | 11 |
| 12 | 6 | 70 | 100 | 2800 | 2 | 10 |

## Strengths

- Strong vs Protoss (23-11) in-sample.

## Weaknesses

- Weak vs Terran (7-30) — loses the mirror on tanks/position.
- Bio-heavy, light on splash.

## How to beat it

1. In the Terran mirror, out-tank and out-position it (sample favors you).
2. Bring splash (P/Z); defend drops.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*