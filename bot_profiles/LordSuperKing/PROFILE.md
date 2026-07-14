# LordSuperKing

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Protoss** bot mixing stalkers with a Stargate/Fleet-Beacon tempest tech. Underperforming recently (47-71).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1752 (top-tier ladder bot) |
| **On ladder since** | 2026-01 |
| **Last source update** | 2026-07-06 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway/stalker into Stargate + tempest.

- Stalker army teching to tempests for range; a lighter skytoss.

## Performance (recent ladder sample)

**Overall: 47–71 (39%)** over 118 decided games (+32 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 16-19 | 45% |
| vs Protoss | 13-23 | 36% |
| vs Zerg | 15-23 | 39% |
| vs Random | 3-6 | 33% |

**Toughest opponents:** TyrT 3-6 (T), who 0-3 (R), Dysnomia 0-3 (Z), smallBly 0-3 (Z), MechaShark 0-3 (T), Zozo 0-3 (P), 12PoolBot 0-3 (Z), ArgoBot 0-2 (P).

**Best matchups:** Roro 3-0 (T), Mulebot 2-0 (T), Dodo 2-0 (Z), 72Tortoises 2-0 (Z), BotTato 2-1 (T), PhantomTest 2-1 (Z), WildLupo 1-0 (P), PolyMorph 1-0 (Z).

## Observed builds (from its own replays)

**vs HelioShard (P), 40.8 min, lost:** Probe×40, Stalker×6, Pylon×5, Assimilator×4, Nexus×3, Gateway×2, CyberneticsCore×1, Stargate×1, FleetBeacon×1, Tempest×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 36 | 0 | 600 | 28 | 27 |
| 6 | 43 | 52 | 350 | 700 | 34 | 37 |
| 8 | 66 | 84 | 1650 | 1800 | 41 | 58 |
| 12 | 72 | 136 | 2400 | 5450 | 43 | 66 |

**vs 72Tortoises (Z), 37.4 min, won:** Probe×34, Stalker×12, Pylon×7, Nexus×3, Assimilator×2, Gateway×2, Zealot×2, CyberneticsCore×1, RoboticsFacility×1, Observer×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 49 | 725 | 1250 | 24 | 25 |
| 6 | 54 | 62 | 1950 | 850 | 30 | 40 |
| 8 | 72 | 81 | 3025 | 1600 | 35 | 40 |
| 12 | 80 | 96 | 2500 | 2550 | 48 | 39 |

**vs QueenBot (Z), 32.1 min, won:** Probe×39, Stalker×14, Pylon×6, Assimilator×4, Nexus×3, Gateway×3, Zealot×2, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 45 | 375 | 700 | 26 | 30 |
| 6 | 56 | 70 | 1775 | 1575 | 33 | 46 |
| 8 | 80 | 99 | 3000 | 1950 | 41 | 71 |
| 12 | 136 | 96 | 6675 | 975 | 55 | 74 |

## Strengths

- Tempest range if it survives to tech.

## Weaknesses

- Losing form; thin during the tempest tech window; stalker army lacks splash.

## How to beat it

1. Pressure the tech window; bring anti-air for the tempests and splash for the stalkers.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*