# LunaxVRR

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **skytoss / tempest** Protoss: photon cannons + stargate into tempests (very similar to ArgoBot). Turtle-to-air.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1883 (top-tier ladder bot) |
| **On ladder since** | 2025-08 |
| **Last source update** | 2026-06-26 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Cannon/forge defensive opening + fast Nexus, into Stargate + Tempests.

- Turtle behind cannons + batteries and tech to tempests that out-range the opponent; win late on economy + air.

## Performance (recent ladder sample)

**Overall: 60–57 (51%)** over 117 decided games (+33 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 12-20 | 37% |
| vs Protoss | 14-22 | 38% |
| vs Zerg | 32-10 | 76% |
| vs Random | 2-5 | 28% |

**Toughest opponents:** TyrT 0-4 (T), Zozo 0-3 (P), GPT 0-3 (T), Sharkling 0-3 (Z), Aeolus 0-3 (P), Xena 0-3 (R), PerilousProtossBot 0-3 (P), sharkbot 0-3 (P).

**Best matchups:** smallBly 4-0 (Z), 12PoolBot 4-0 (Z), SharpenedEdge 4-0 (P), Dodo 4-0 (Z), norman 3-0 (P), SpeedlingBot 3-0 (Z), KerrigansTorment 3-0 (Z), Clicadinha 2-0 (Z).

## Observed builds (from its own replays)

**vs Mulebot (T), 39.4 min, won:** Probe×37, Pylon×5, Assimilator×4, PhotonCannon×3, Nexus×2, Stargate×2, Tempest×2, Gateway×1, Forge×1, CyberneticsCore×1, ShieldBattery×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 24 | 32 | 0 | 150 | 24 | 26 |
| 6 | 40 | 60 | 425 | 350 | 30 | 38 |
| 8 | 65 | 93 | 1275 | 2500 | 43 | 52 |
| 12 | 125 | 119 | 4675 | 1500 | 70 | 83 |

**vs Mulebot (T), 39.3 min, lost:** Probe×39, Pylon×5, Assimilator×4, PhotonCannon×3, Nexus×2, Stargate×2, Tempest×2, Gateway×1, Forge×1, CyberneticsCore×1, ShieldBattery×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 25 | 44 | 0 | 200 | 24 | 35 |
| 6 | 41 | 69 | 425 | 900 | 31 | 48 |
| 8 | 66 | 95 | 1275 | 950 | 45 | 67 |
| 12 | 129 | 146 | 4775 | 3125 | 68 | 98 |

**vs Dysnomia (Z), 34.4 min, lost:** Probe×38, Pylon×5, Assimilator×4, PhotonCannon×3, Nexus×2, Stargate×2, Tempest×2, Forge×1, Gateway×1, CyberneticsCore×1, ShieldBattery×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 25 | 44 | 0 | 550 | 24 | 32 |
| 6 | 40 | 64 | 425 | 1075 | 30 | 48 |
| 8 | 66 | 92 | 1700 | 4225 | 44 | 46 |
| 12 | 81 | 164 | 2550 | 9975 | 51 | 44 |

## Strengths

- Hard to attack head-on; tempests out-range most armies; strong vs Zerg (32-10).

## Weaknesses

- Immobile; weak to early timings before tempests and to mass anti-air; negative vs Terran (12-20) and Protoss (14-22) in-sample.

## How to beat it

1. Punish the tech window before tempests; don't attack into cannons.
2. Bring anti-air (vikings/corruptors) and out-maneuver the static defense.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*