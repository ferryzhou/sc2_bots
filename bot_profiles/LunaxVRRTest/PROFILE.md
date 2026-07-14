# LunaxVRRTest

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A test build of **LunaxVRR** — the same **skytoss** line (stargate into void rays / tempests, fleet beacon) behind cannons. See the LunaxVRR profile.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1836 (top-tier ladder bot) |
| **On ladder since** | 2025-09 |
| **Last source update** | 2026-07-01 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Cannon/stargate into void ray + tempest air.

- Turtle-to-air: cannons + batteries, tech to void ray/tempest and win late on air + economy.

## Performance (recent ladder sample)

**Overall: 85–54 (61%)** over 139 decided games (+11 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 28-12 | 70% |
| vs Protoss | 24-25 | 48% |
| vs Zerg | 26-16 | 61% |
| vs Random | 7-1 | 87% |

**Toughest opponents:** JimmyBotP 0-3 (P), SharpenedEdge 0-2 (P), ArtZerg 0-2 (Z), Creepy_duo_canon 0-2 (P), Aeolus 0-2 (P), Clicadinha 0-2 (Z), Arpy 0-2 (P), 12PoolBot 0-2 (Z).

**Best matchups:** Dodo 4-0 (Z), Hestia 3-0 (T), smokinggunbot 3-0 (T), kas 3-0 (Z), PiG_Bot 3-0 (P), Lissy 3-0 (Z), SharkGull 3-0 (Z), Stark234_PR02 3-1 (T).

## Observed builds (from its own replays)

**vs Stark234_PR02 (T), 64.6 min, lost:** Probe×59, Pylon×8, Assimilator×6, Nexus×3, Stargate×3, Adept×2, VoidRay×2, Gateway×1, CyberneticsCore×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 38 | 250 | 500 | 32 | 25 |
| 6 | 61 | 56 | 650 | 1050 | 47 | 28 |
| 8 | 69 | 73 | 755 | 1600 | 48 | 38 |
| 12 | 1 | 123 | 0 | 4125 | 0 | 56 |

**vs Voltron (T), 38.5 min, won:** Probe×46, Pylon×7, Assimilator×4, Nexus×3, Stargate×2, Adept×2, VoidRay×2, Gateway×1, CyberneticsCore×1, Zealot×1, FleetBeacon×1, Carrier×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 32 | 250 | 150 | 27 | 26 |
| 6 | 52 | 52 | 1050 | 600 | 38 | 39 |
| 8 | 80 | 98 | 1770 | 2125 | 53 | 57 |
| 12 | 149 | 182 | 5065 | 6050 | 83 | 82 |

**vs QueenBot (Z), 34.6 min, won:** Probe×41, Pylon×5, Assimilator×4, Nexus×3, PhotonCannon×3, Stargate×2, Gateway×1, Forge×1, CyberneticsCore×1, Zealot×1, Adept×1, FleetBeacon×1, Carrier×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 28 | 43 | 125 | 700 | 25 | 28 |
| 6 | 43 | 64 | 125 | 1575 | 33 | 41 |
| 8 | 69 | 96 | 1505 | 2650 | 47 | 58 |
| 12 | 140 | 122 | 5205 | 3175 | 73 | 70 |

## Strengths

- Hard to attack head-on; strong vs Terran (28-12) in this sample.

## Weaknesses

- Immobile; weak to early pressure and mass anti-air.

## How to beat it

1. Anti-air (vikings/corruptors) + hit the tech window; don't attack the cannons head-on.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*