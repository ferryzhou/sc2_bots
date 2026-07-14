# ArgoBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **cannon-turtle skytoss** Protoss: forge/cannons + shield batteries for a fortress economy, teching to **tempests** (and stargate air) to win from range. Patient, defensive, economy-heavy.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~2065 (top-tier ladder bot) |
| **On ladder since** | 2025-11 |
| **Last source update** | 2026-05-08 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Forge/cannon defensive opening; fast Nexus economy behind static defense, into Stargate + Tempest.

- Turtle behind photon cannons + batteries, take a greedy economy, and tech to tempests that out-range everything.
- Wins the late game on economy + tempest range; avoids early fights.

## Performance (recent ladder sample)

**Overall: 90–32 (73%)** over 122 decided games (+28 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 29-8 | 78% |
| vs Protoss | 23-11 | 67% |
| vs Zerg | 29-9 | 76% |
| vs Random | 9-4 | 69% |

**Toughest opponents:** Zozo 0-4 (P), Dysnomia 1-3 (Z), Eris 1-3 (Z), BotTato 0-2 (T), BenBotBC 1-2 (T), sharkbot 1-2 (P), SpeedlingBot 1-2 (Z), PerilousProtossBot 1-2 (P).

**Best matchups:** KerrigansTorment 4-0 (Z), GPT 4-0 (T), smallBly 4-0 (Z), Mulebot 4-0 (T), TyrT 4-1 (T), LordSuperKing 3-0 (P), WickedBot 3-0 (T), ZeratulsRevenge 3-0 (P).

## Observed builds (from its own replays)

**vs PhantomBot (Z), 56.6 min, won:** Probe×33, PhotonCannon×6, Pylon×5, Assimilator×4, ShieldBattery×4, Nexus×2, Stalker×2, Stargate×2, Tempest×2, Gateway×1, Forge×1, CyberneticsCore×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 50 | 350 | 1000 | 28 | 29 |
| 6 | 41 | 69 | 350 | 1450 | 33 | 41 |
| 8 | 61 | 105 | 2050 | 2075 | 33 | 69 |
| 12 | 94 | 200 | 5525 | 6775 | 33 | 98 |

**vs PhantomTest (Z), 49.9 min, won:** Probe×22, Pylon×6, PhotonCannon×6, ShieldBattery×3, Tempest×3, Assimilator×2, Stargate×2, Stalker×2, Nexus×1, Gateway×1, Forge×1, CyberneticsCore×1, FleetBeacon×1, ChangelingZealot×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 44 | 350 | 675 | 22 | 31 |
| 6 | 34 | 63 | 775 | 1150 | 22 | 43 |
| 8 | 46 | 94 | 2050 | 1625 | 22 | 67 |
| 12 | 71 | 139 | 3250 | 3225 | 34 | 80 |

**vs AvocaDOS (T), 31.0 min, won:** Probe×22, Pylon×6, PhotonCannon×6, Assimilator×2, ShieldBattery×2, Stargate×2, Stalker×2, Tempest×2, Nexus×1, Gateway×1, CyberneticsCore×1, FleetBeacon×1, Forge×1, Mothership×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 35 | 350 | 425 | 22 | 25 |
| 6 | 42 | 56 | 775 | 625 | 22 | 37 |
| 8 | 50 | 87 | 2425 | 1525 | 22 | 52 |
| 12 | 73 | 129 | 3625 | 2125 | 32 | 72 |

## Strengths

- Very hard to attack head-on (cannon/battery fortress) — strong, safe economy; good all-around record (90-32 sample).
- Tempests out-range most compositions and pick apart slow armies.

## Weaknesses

- Immobile and slow — cedes map control; weak to early aggression before tempests are online (the tech window).
- Anti-air (vikings, corruptors, mass air) and mobility beat a static skytoss.

## How to beat it

1. Punish the tech window with a timing before tempests arrive — don't give it a free late game.
2. Don't attack into the cannons; out-expand and take the map, then bring anti-air (vikings/corruptors) for the tempests.
3. Multi-prong its immobile defense.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*