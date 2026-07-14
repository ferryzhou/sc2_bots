# Mulebot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio-mech** bot (Python): marine + siege tank + hellion. Struggling recently (49-83), notably vs Random (1-14).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1697 (top-tier ladder bot) |
| **On ladder since** | 2024-05 |
| **Last source update** | 2026-06-16 |
| **Source public** | yes (Python source publicly downloadable; this profile is from replays + record) |

## Strategy

**Opening:** Bio into siege tank + hellion; standard rax/factory.

- Marine/tank/hellion mix — positional Terran with some mech.

## Performance (recent ladder sample)

**Overall: 49–83 (37%)** over 132 decided games (+18 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 25-22 | 53% |
| vs Protoss | 11-25 | 30% |
| vs Zerg | 12-22 | 35% |
| vs Random | 1-14 | 6% |

**Toughest opponents:** 12PoolBot 0-5 (Z), Eris 0-5 (Z), Xena 0-5 (R), changeling 0-5 (R), Roro 1-5 (T), Aeolus 1-5 (P), Caninana 0-4 (Z), theBigBot 1-4 (P).

**Best matchups:** WickedBot 3-0 (T), nida 3-0 (P), 72Tortoises 3-0 (Z), zig-spudde 3-0 (T), GPT 3-1 (T), Clicadinha 3-1 (Z), Klakinn 2-0 (P), 27turtles 2-0 (T).

## Observed builds (from its own replays)

**vs BenBotBC (T), 52.0 min, won:** SCV×33, Marine×19, SupplyDepot×6, Barracks×3, SiegeTank×3, CommandCenter×2, Refinery×2, Hellion×2, Factory×1, FactoryTechLab×1, Starport×1, Medivac×1, StarportTechLab×1, Liberator×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 30 | 34 | 0 | 350 | 23 | 25 |
| 6 | 49 | 43 | 1225 | 750 | 26 | 29 |
| 8 | 65 | 56 | 1500 | 750 | 35 | 41 |
| 12 | 120 | 68 | 2675 | 2175 | 67 | 40 |

**vs norman (P), 43.5 min, won:** SCV×40, Marauder×6, SupplyDepot×4, Refinery×4, CommandCenter×3, SiegeTank×3, Barracks×1, BarracksTechLab×1, Factory×1, FactoryTechLab×1, Marine×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 38 | 650 | 625 | 22 | 24 |
| 6 | 53 | 57 | 1100 | 2100 | 32 | 26 |
| 8 | 51 | 57 | 1075 | 1700 | 31 | 29 |
| 12 | 14 | 107 | 225 | 3475 | 10 | 58 |

**vs nida (P), 43.0 min, won:** SCV×39, Marine×17, SupplyDepot×7, Barracks×4, Refinery×3, SiegeTank×3, CommandCenter×2, KD8Charge×2, Bunker×1, Factory×1, Reaper×1, BarracksReactor×1, FactoryTechLab×1, Starport×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 40 | 150 | 700 | 24 | 25 |
| 6 | 59 | 57 | 1425 | 2250 | 31 | 26 |
| 8 | 84 | 77 | 1750 | 3675 | 45 | 26 |
| 12 | 50 | 100 | 1425 | 3900 | 25 | 43 |

## Strengths

- Competitive in the Terran mirror (25-22).

## Weaknesses

- Losing form; weak vs Protoss (11-25), Zerg (12-22), Random (1-14).

## How to beat it

1. Bring splash/mass and exploit mech immobility with drops/multi-prong.
2. As Protoss, immortal/colossus; as Zerg, mass + flanks.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*