# ArgoTest

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A development/test build of **ArgoBot** — same **cannon-turtle skytoss** (forge/cannons into stargate + tempests). Strong record (100-42), crushing Zerg (43-9). See the ArgoBot profile; play it the same way.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1842 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-06-20 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Forge/cannon defensive opening + fast Nexus, into Stargate + Tempests.

- Turtle behind cannons/batteries, greedy economy, tech to tempests that out-range everything — identical plan to ArgoBot.

## Performance (recent ladder sample)

**Overall: 100–42 (70%)** over 142 decided games (+8 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 23-12 | 65% |
| vs Protoss | 26-15 | 63% |
| vs Zerg | 43-9 | 82% |
| vs Random | 8-6 | 57% |

**Toughest opponents:** BotTato 0-3 (T), Forsaken 0-2 (T), Aeolus 0-2 (P), whalemean 0-2 (R), LunaxVRR 1-2 (P), LordSuperKing 1-2 (P), BobbyBotV13 0-1 (R), protossinger 0-1 (P).

**Best matchups:** Princess-Mika-Test 3-0 (Z), AvocaDOS 3-0 (T), JimmyBot 3-0 (R), Clicadinha 3-0 (Z), Mulebot 3-0 (T), 12PoolBot 3-0 (Z), Hannibal_v2 2-0 (Z), Persephone 2-0 (Z).

## Observed builds (from its own replays)

**vs WorkingAsIntended (P), 58.7 min, lost:** Probe×17, Nexus×2, Pylon×1, Forge×1, PhotonCannon×1, Gateway×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 17 | 39 | 0 | 350 | 17 | 29 |
| 6 | 17 | 65 | 0 | 1750 | 17 | 44 |
| 8 | 17 | 97 | 0 | 2600 | 17 | 60 |
| 12 | 17 | 197 | 0 | 8500 | 17 | 82 |

**vs Forsaken (T), 51.2 min, lost:** Probe×17, Nexus×2, Pylon×1, Forge×1, PhotonCannon×1, Gateway×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 17 | 26 | 0 | 200 | 17 | 20 |
| 6 | 17 | 47 | 0 | 875 | 17 | 27 |
| 8 | 17 | 62 | 0 | 1750 | 17 | 36 |
| 12 | 17 | 109 | 0 | 3825 | 17 | 44 |

**vs 72Tortoises (Z), 43.7 min, won:** Probe×22, Pylon×6, Tempest×4, ShieldBattery×3, Assimilator×2, Stargate×2, Stalker×2, PhotonCannon×2, Nexus×1, Gateway×1, CyberneticsCore×1, FleetBeacon×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 52 | 350 | 1150 | 22 | 27 |
| 6 | 42 | 64 | 1200 | 1025 | 22 | 41 |
| 8 | 50 | 92 | 2475 | 1975 | 22 | 53 |
| 12 | 72 | 134 | 3550 | 2900 | 31 | 78 |

## Strengths

- Fortress defense + tempest range; dominant vs Zerg (43-9).

## Weaknesses

- Immobile; weak to timings before tempests and to mass anti-air.

## How to beat it

1. Punish the tech window before tempests; don't attack into cannons.
2. Out-expand, then bring anti-air (vikings/corruptors) for the tempests.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*