# Forgefiend

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **cannon-turtle / cannon-rush Protoss**: forge + mass photon cannons (8+). Static, defensive/aggressive cannons. Losing form (53-81).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1657 (top-tier ladder bot) |
| **On ladder since** | 2026-04 |
| **Last source update** | 2026-05-20 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Forge-first into mass photon cannons (turtle or cannon rush).

- Static cannon walls + tech; shuts down aggression, or rushes cannons into the opponent.

## Performance (recent ladder sample)

**Overall: 53–81 (39%)** over 134 decided games (+16 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 14-16 | 46% |
| vs Protoss | 14-30 | 31% |
| vs Zerg | 23-31 | 42% |
| vs Random | 2-4 | 33% |

**Toughest opponents:** oberon 0-5 (T), Princess-Mika-Test 0-5 (Z), Crawler 0-5 (Z), OBODT 0-5 (P), smokinggunbot 0-5 (T), PerilousProtossBot 1-5 (P), Lissy 0-4 (Z), LordSuperKing 0-3 (P).

**Best matchups:** Stockfish 6-1 (T), onlyfans 4-0 (T), PiG_Bot 4-1 (P), muravevTerran 3-0 (T), MindMatrix 3-1 (Z), Necrobot-micro-test 2-0 (Z), ArtZerg 3-2 (Z), NecroBot 2-1 (Z).

## Observed builds (from its own replays)

**vs MindMatrix (Z), 56.0 min, won:** Probe×26, Pylon×12, PhotonCannon×8, Nexus×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 22 | 32 | 0 | 575 | 22 | 20 |
| 6 | 22 | 32 | 0 | 1125 | 21 | 19 |
| 8 | 22 | 24 | 0 | 550 | 22 | 19 |
| 12 | 22 | 26 | 0 | 400 | 22 | 19 |

**vs puck (P), 50.5 min, won:** Probe×49, Pylon×8, Stalker×7, Assimilator×4, Nexus×3, Observer×3, VoidRay×2, Gateway×1, CyberneticsCore×1, Stargate×1, RoboticsFacility×1, FleetBeacon×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 38 | 38 | 175 | 525 | 29 | 28 |
| 6 | 62 | 53 | 1575 | 975 | 43 | 38 |
| 8 | 83 | 65 | 2325 | 1100 | 56 | 52 |
| 12 | 145 | 93 | 3965 | 2325 | 88 | 63 |

**vs Princess-Mika (Z), 45.0 min, lost:** Probe×24, Pylon×13, PhotonCannon×4, Nexus×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 1 | 36 | 0 | 575 | 1 | 21 |
| 6 | 1 | 44 | 0 | 750 | 1 | 31 |
| 8 | 1 | 52 | 0 | 525 | 1 | 42 |
| 12 | 1 | 53 | 0 | 950 | 1 | 42 |

## Strengths

- Cannons punish frontal attacks; can end games early vs the unprepared.

## Weaknesses

- Immobile — cedes the map; weak vs Protoss (14-30) and Zerg (23-31).
- A denied cannon rush leaves it far behind.

## How to beat it

1. Scout for a cannon rush and deny it; don't attack into cannons.
2. Out-expand and siege from range (tanks/tempest); take the map.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*