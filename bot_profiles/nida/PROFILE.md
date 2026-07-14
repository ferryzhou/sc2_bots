# nida

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **gateway macro Protoss**: stalker/sentry with phoenix support and robo tech. Even-ish form (65-72).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | nodejs |
| **AI Arena Elo** | ~1653 (top-tier ladder bot) |
| **On ladder since** | 2023-05 |
| **Last source update** | 2026-07-13 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway expand into cyber; stalker/sentry with phoenix, robo support.

- Stalker/sentry army (forcefields) with phoenix harass; macro into a mixed deathball.

## Performance (recent ladder sample)

**Overall: 65–72 (47%)** over 137 decided games (+13 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 12-21 | 36% |
| vs Protoss | 26-21 | 55% |
| vs Zerg | 22-27 | 44% |
| vs Random | 5-3 | 62% |

**Toughest opponents:** QueenBot 0-4 (Z), Mulebot 0-3 (T), Nothing 1-3 (P), norman 1-3 (P), GPT 0-2 (T), negativeZero 0-2 (P), BenBotBC 0-2 (T), TyrT 0-2 (T).

**Best matchups:** PrimordialOrigin 4-0 (P), GenesisLotus 4-0 (P), puck 4-0 (P), Princess-Mika-Test 4-1 (Z), Juggerbot 4-1 (Z), TheLAW 3-0 (T), SiriusBot 3-0 (R), BigDaddy 3-0 (T).

## Observed builds (from its own replays)

**vs Creepy_macro (Z), 64.2 min, lost:** Probe×40, Pylon×8, Stalker×7, Gateway×3, Sentry×3, Nexus×2, Assimilator×2, Zealot×2, Phoenix×2, CyberneticsCore×1, ShieldBattery×1, Forge×1, RoboticsFacility×1, Observer×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 42 | 625 | 550 | 25 | 27 |
| 6 | 52 | 66 | 1075 | 1275 | 32 | 51 |
| 8 | 82 | 124 | 2325 | 2425 | 47 | 71 |
| 12 | 167 | 200 | 5975 | 8200 | 78 | 77 |

**vs LordSuperKing (P), 28.8 min, lost:** Probe×54, Pylon×9, Stalker×4, Nexus×3, Gateway×3, Assimilator×3, Zealot×2, Immortal×2, CyberneticsCore×1, RoboticsFacility×1, Observer×1, Sentry×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 34 | 200 | 175 | 29 | 29 |
| 6 | 65 | 49 | 1150 | 1125 | 40 | 36 |
| 8 | 98 | 53 | 2525 | 825 | 55 | 43 |
| 12 | 116 | 81 | 5225 | 2200 | 42 | 57 |

**vs Clicadinha (Z), 28.3 min, won:** Probe×43, Pylon×8, Stalker×5, Nexus×3, Gateway×3, Zealot×3, Assimilator×2, CyberneticsCore×1, ShieldBattery×1, Forge×1, RoboticsFacility×1, Sentry×1, Observer×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 32 | 40 | 525 | 525 | 25 | 29 |
| 6 | 50 | 67 | 975 | 2000 | 33 | 33 |
| 8 | 86 | 67 | 2100 | 2000 | 49 | 33 |
| 12 | 100 | 103 | 3350 | 3525 | 50 | 33 |

## Strengths

- Competitive vs Protoss (26-21); sentries + phoenix give control and harass.

## Weaknesses

- Weak vs Terran (12-21); stalker/sentry light on splash.

## How to beat it

1. As Terran, tanks/drops + splash; dodge/bait forcefields.
2. Bring anti-air for phoenix; match upgrades.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*