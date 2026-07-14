# Hellcannon

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **cannon + gateway Protoss**: photon cannons for defense with a zealot/gateway army and forge upgrades. Semi-turtle into gateway aggression. Strong vs Zerg (35-17).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1609 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-05-13 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway + Forge with photon cannons; zealots behind cannon defense.

- Cannons secure the base/natural, then push out with an upgraded zealot/gateway army.
- Uses static defense to enable aggression or greed.

## Performance (recent ladder sample)

**Overall: 76–62 (55%)** over 138 decided games (+12 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 12-18 | 40% |
| vs Protoss | 25-23 | 52% |
| vs Zerg | 35-17 | 67% |
| vs Random | 4-4 | 50% |

**Toughest opponents:** LordSuperKing 0-3 (P), JimmyBot 0-3 (R), BigDaddy 0-3 (T), ZeratulsRevengeTest 0-3 (P), JimmyBotT 0-3 (T), norman 0-3 (P), 27turtles 0-2 (T), smokinggunbot 0-2 (T).

**Best matchups:** Persephone 4-0 (Z), clone 3-0 (T), 72Tortoises 3-0 (Z), Clicadinha 3-0 (Z), CynEX 3-0 (P), 49Terrapins 2-0 (P), MindMatrix 2-0 (Z), Stockfish 2-0 (T).

## Observed builds (from its own replays)

**vs MindMatrix (Z), 56.0 min, won:** Probe×25, Zealot×9, PhotonCannon×6, Pylon×5, Gateway×5, Forge×2, CyberneticsCore×2, Nexus×1, Assimilator×1, ShieldBattery×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 34 | 200 | 775 | 22 | 20 |
| 6 | 34 | 46 | 400 | 1950 | 22 | 19 |
| 8 | 19 | 46 | 800 | 1475 | 2 | 19 |
| 12 | 1 | 28 | 0 | 325 | 1 | 19 |

**vs 27turtles (T), 45.2 min, lost:** Probe×30, Zealot×7, PhotonCannon×5, ShieldBattery×5, Pylon×3, Gateway×3, Nexus×1, Forge×1, Assimilator×1, CyberneticsCore×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 23 | 34 | 200 | 200 | 18 | 25 |
| 6 | 30 | 52 | 400 | 1275 | 22 | 30 |
| 8 | 28 | 58 | 100 | 1825 | 22 | 30 |
| 12 | 22 | 42 | 0 | 525 | 22 | 30 |

**vs Apidae (P), 39.6 min, lost:** Probe×25, Zealot×10, PhotonCannon×6, ShieldBattery×5, Gateway×4, Pylon×3, Nexus×1, Forge×1, Assimilator×1, CyberneticsCore×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 24 | 23 | 0 | 0 | 22 | 22 |
| 6 | 26 | 32 | 100 | 200 | 21 | 24 |
| 8 | 38 | 35 | 700 | 500 | 22 | 24 |
| 12 | 42 | 46 | 900 | 1600 | 22 | 24 |

## Strengths

- Cannon defense + zealot aggression is hard for mass-light to crack (strong vs Zerg 35-17).
- Forge upgrades compound the gateway army.

## Weaknesses

- Weak vs Terran (12-18) — tanks out-range cannons/zealots; cannons cede map mobility.
- Melee zealots stall vs splash + a wall.

## How to beat it

1. As Terran, tanks out-range the cannon line; don't melee into cannons.
2. Out-expand the semi-turtle; splash the zealots.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*