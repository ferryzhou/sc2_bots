# JimmyBotT

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

The Terran variant of the **Jimmy** family: bio + siege tanks + starport. Bio-tank-air macro.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1860 (top-tier ladder bot) |
| **On ladder since** | 2026-03 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio into siege tanks and starport (tech-lab) — a mech-flavored bio macro.

- Marine + siege tank + starport tech; positional Terran.

## Performance (recent ladder sample)

**Overall: 68–71 (48%)** over 139 decided games (+11 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 10-26 | 27% |
| vs Protoss | 14-21 | 40% |
| vs Zerg | 38-20 | 65% |
| vs Random | 4-4 | 50% |
| vs ? | 2-0 | 100% |

**Toughest opponents:** TheLAW 0-5 (T), Nothing 0-5 (P), clone 0-5 (T), muravev 0-5 (Z), BigDaddy 0-5 (T), QueenBot 0-4 (Z), LordSuperKing 0-3 (P), WaterLeak 0-3 (Z).

**Best matchups:** Clicadinha 5-0 (Z), Princess-Mika 4-0 (Z), smokinggunbot 4-0 (T), Lissy 4-0 (Z), JimmyBotZ 4-0 (Z), Crawler 4-1 (Z), ArtZerg 4-1 (Z), 27turtles 3-1 (T).

## Observed builds (from its own replays)

**vs muravev (Z), 50.1 min, lost:** SCV×41, Marine×13, SupplyDepot×7, Refinery×4, CommandCenter×3, SiegeTank×3, Starport×2, StarportTechLab×2, Barracks×1, Factory×1, FactoryTechLab×1, Bunker×1, FusionCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 36 | 300 | 200 | 26 | 27 |
| 6 | 53 | 65 | 1050 | 850 | 34 | 45 |
| 8 | 82 | 111 | 1850 | 2100 | 46 | 55 |
| 12 | 103 | 126 | 4350 | 5575 | 48 | 55 |

**vs QueenBot (Z), 45.9 min, lost:** SCV×41, Marine×13, SupplyDepot×7, CommandCenter×3, Refinery×3, SiegeTank×3, Starport×2, StarportTechLab×2, Barracks×1, Factory×1, FactoryTechLab×1, Bunker×1, FusionCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 46 | 300 | 700 | 26 | 32 |
| 6 | 55 | 76 | 1050 | 1400 | 34 | 50 |
| 8 | 76 | 108 | 1850 | 2650 | 46 | 70 |
| 12 | 61 | 120 | 3475 | 4575 | 20 | 70 |

**vs onlyfans (T), 42.2 min, lost:** SCV×40, Marine×13, SupplyDepot×7, CommandCenter×3, Refinery×3, SiegeTank×3, Starport×2, StarportTechLab×2, Barracks×1, Factory×1, FactoryTechLab×1, Bunker×1, FusionCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 30 | 300 | 300 | 26 | 23 |
| 6 | 51 | 53 | 1050 | 850 | 33 | 34 |
| 8 | 67 | 69 | 1250 | 950 | 44 | 46 |
| 12 | 79 | 134 | 2300 | 2450 | 37 | 74 |

## Strengths

- Tank support gives splash; competitive vs Zerg (38-20).

## Weaknesses

- Losing recent form (68-71); weak vs Terran (10-26) and Protoss (14-21).

## How to beat it

1. Exploit tank immobility with drops/air/multi-prong.
2. As Protoss, immortal/colossus + storm; as Terran, win the tank count.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*