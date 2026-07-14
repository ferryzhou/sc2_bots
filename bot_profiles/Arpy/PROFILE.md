# Arpy

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **gateway-aggression Protoss**: zealot/adept off many gateways with phoenix support. Aggressive but currently losing (51-71).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1713 (top-tier ladder bot) |
| **On ladder since** | 2026-04 |
| **Last source update** | 2026-06-25 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway-heavy zealot/adept (7 gates, 23 zealots seen) with a phoenix.

- Gateway zealot/adept pressure into a macro game; phoenix for air/harass.

## Performance (recent ladder sample)

**Overall: 51–71 (41%)** over 122 decided games (+28 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 5-21 | 19% |
| vs Protoss | 19-14 | 57% |
| vs Zerg | 18-31 | 36% |
| vs Random | 9-5 | 64% |

**Toughest opponents:** NecroBot 0-5 (Z), ArtZerg 0-4 (Z), oberon 0-4 (T), Princess-Mika 1-4 (Z), TheLAW 0-3 (T), Creepy_canon 0-3 (P), Lissy 1-3 (Z), 27turtles 1-3 (T).

**Best matchups:** FlowerPrincess 3-0 (Z), SiriusBot 3-1 (R), Belzebuth 2-0 (Z), PrimordialOrigin 2-0 (P), BobbyBotV13 2-0 (R), 49Terrapins 2-0 (P), PiG_Bot 2-0 (P), protossinger 2-0 (P).

## Observed builds (from its own replays)

**vs Hannibal_v2 (Z), 46.7 min, won:** Probe×42, Zealot×23, Pylon×12, Gateway×7, Adept×5, Nexus×2, Assimilator×2, CyberneticsCore×1, Sentry×1, Phoenix×1, TwilightCouncil×1, Stalker×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 45 | 26 | 425 | 200 | 34 | 21 |
| 6 | 63 | 50 | 1150 | 400 | 41 | 36 |
| 8 | 121 | 69 | 4250 | 50 | 41 | 62 |
| 12 | 199 | 92 | 8150 | 400 | 41 | 72 |

**vs DownedStar1 (T), 46.3 min, lost:** Probe×43, Zealot×20, AdeptPhaseShift×13, Pylon×9, Gateway×7, Phoenix×3, Nexus×2, Assimilator×2, CyberneticsCore×1, ShieldBattery×1, Forge×1, Adept×1, Sentry×1, Stalker×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 45 | 27 | 450 | 200 | 33 | 22 |
| 6 | 63 | 40 | 1050 | 1000 | 41 | 22 |
| 8 | 103 | 45 | 2975 | 1400 | 41 | 22 |
| 12 | 162 | 44 | 6150 | 2100 | 40 | 16 |

**vs 27turtles (T), 45.3 min, lost:** Probe×24, Stalker×15, Pylon×4, Gateway×2, Assimilator×2, Nexus×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 28 | 525 | 250 | 24 | 20 |
| 6 | 34 | 27 | 525 | 0 | 24 | 25 |
| 8 | 40 | 35 | 1050 | 0 | 24 | 32 |
| 12 | 74 | 96 | 3675 | 2300 | 24 | 52 |

## Strengths

- Best vs Protoss (19-14); the zealot/adept flood can overwhelm the unprepared.

## Weaknesses

- Very weak vs Terran (5-21) — tanks/hellions shred the gateway army; also weak vs Zerg (18-31).
- Melee-heavy, light on splash.

## How to beat it

1. As Terran, wall + tanks/hellions crush the zealot flood.
2. As Zerg, splash (banelings) + mass; hold the aggression then out-macro.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*