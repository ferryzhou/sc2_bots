# CynEX

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **skytoss/stalker macro Protoss** (the current, stronger Cyne line): stalkers + Stargate air + cannons behind a good economy. 92-58, strong across the board.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1677 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-05-10 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway/stalker into Stargate (air) with cannon defense and cyber upgrades.

- Stalker core + Stargate air (void/phoenix) with static defense; macro into a mixed deathball.
- Balanced army with air support and upgrades.

## Performance (recent ladder sample)

**Overall: 92–58 (61%)** over 150 decided games.

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 27-12 | 69% |
| vs Protoss | 30-19 | 61% |
| vs Zerg | 30-19 | 61% |
| vs Random | 5-8 | 38% |

**Toughest opponents:** JimmyBot 0-4 (R), JimmyBotT 0-4 (T), JimmyBotZ 0-3 (Z), JimmyBotP 0-3 (P), Apidae 1-3 (P), ZeratulsRevengeTest 1-3 (P), oberon 0-2 (T), Crawler 0-2 (Z).

**Best matchups:** SharkGull 5-0 (Z), smokinggunbot 4-0 (T), PerilousProtossBot 4-0 (P), AvocaDOS 4-0 (T), LordSuperKing 4-0 (P), 72Tortoises 4-0 (Z), nida 3-0 (P), norman 3-0 (P).

## Observed builds (from its own replays)

**vs QueenBot (Z), 55.1 min, won:** Probe×46, Pylon×8, Assimilator×4, Stalker×4, Nexus×3, CyberneticsCore×2, Stargate×2, PhotonCannon×2, Gateway×1, Forge×1, ShieldBattery×1, FleetBeacon×1, Oracle×1, Carrier×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 46 | 175 | 700 | 33 | 33 |
| 6 | 62 | 67 | 1000 | 1400 | 45 | 45 |
| 8 | 71 | 100 | 1420 | 2300 | 45 | 66 |
| 12 | 117 | 141 | 3890 | 3075 | 65 | 93 |

**vs 27turtles (T), 44.4 min, lost:** Probe×46, Pylon×7, Assimilator×4, Stalker×4, Nexus×3, CyberneticsCore×2, Stargate×2, PhotonCannon×2, Gateway×1, Forge×1, ShieldBattery×1, FleetBeacon×1, Oracle×1, Carrier×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 28 | 175 | 0 | 34 | 26 |
| 6 | 62 | 46 | 825 | 875 | 45 | 31 |
| 8 | 68 | 71 | 1720 | 1375 | 44 | 41 |
| 12 | 64 | 74 | 2395 | 1175 | 41 | 46 |

**vs Clicadinha (Z), 37.6 min, won:** Probe×44, Pylon×4, Assimilator×3, Nexus×2, Stalker×2, PhotonCannon×2, Gateway×1, CyberneticsCore×1, Forge×1, ShieldBattery×1, Stargate×1, FleetBeacon×1, Oracle×1, Zealot×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 44 | 44 | 175 | 600 | 35 | 26 |
| 6 | 12 | 46 | 400 | 1150 | 7 | 25 |
| 8 | 12 | 79 | 400 | 1500 | 7 | 58 |
| 12 | 12 | 89 | 400 | 2375 | 7 | 58 |

## Strengths

- Strong all-round (vs P 30-19, Z 30-19, T 27-12); air + stalker flexibility.
- Cannons make it hard to punish early.

## Weaknesses

- Can be out-macroed if it over-invests in static defense; stalker core still light on splash.

## How to beat it

1. Match upgrades and force splash-favorable fights; bring anti-air for the Stargate units.
2. Don't attack into cannons — out-expand and take favorable trades.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*