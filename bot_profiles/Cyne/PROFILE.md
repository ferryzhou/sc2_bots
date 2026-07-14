# Cyne

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **gateway/robo macro Protoss** currently underperforming (37-89). (A CynEX variant/relative — CynEX is the stronger current build.)

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1756 (top-tier ladder bot) |
| **On ladder since** | 2025-09 |
| **Last source update** | 2026-04-19 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway expand into robo; stalker/zealot with robo support.

- Gateway/robo Protoss macro; in current form it is losing most matchups.

## Performance (recent ladder sample)

**Overall: 37–89 (29%)** over 126 decided games (+24 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 15-35 | 30% |
| vs Protoss | 8-27 | 22% |
| vs Zerg | 7-23 | 23% |
| vs Random | 7-4 | 63% |

**Toughest opponents:** Crawler 0-5 (Z), PiG_Bot 0-4 (P), PrimordialOrigin 0-4 (P), Alexa 0-4 (T), muravevTerranV2 0-3 (T), QueenBot 0-3 (Z), Suimon 0-3 (T), ANI_dev 0-3 (T).

**Best matchups:** BotTato 4-0 (T), Positive_Null 4-0 (Z), Laser-Circus 4-0 (P), SiriusBot 3-0 (R), Kendra 3-1 (T), Gordon 2-0 (T), smokinggunbot 2-0 (T), BlackCompany 2-0 (T).

## Observed builds (from its own replays)

**vs nida (P), 54.5 min, lost:** Probe×43, Stalker×6, Pylon×5, Gateway×4, Assimilator×4, Nexus×3, Zealot×2, RoboticsFacility×2, CyberneticsCore×1, Forge×1, Observer×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 40 | 200 | 800 | 23 | 24 |
| 6 | 53 | 53 | 825 | 2075 | 39 | 26 |
| 8 | 62 | 70 | 725 | 3025 | 43 | 28 |
| 12 | 46 | 129 | 450 | 5200 | 32 | 55 |

**vs SiriusBot (P), 43.6 min, won:** Probe×42, Pylon×6, Stalker×5, Assimilator×4, Nexus×3, Gateway×2, Zealot×2, Observer×2, CyberneticsCore×1, Forge×1, RoboticsFacility×1, Stargate×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 29 | 200 | 500 | 23 | 23 |
| 6 | 53 | 39 | 725 | 625 | 38 | 27 |
| 8 | 66 | 55 | 1425 | 650 | 46 | 38 |
| 12 | 118 | 106 | 2375 | 2000 | 77 | 68 |

**vs BotTato (T), 41.4 min, won:** Probe×47, Pylon×6, Stalker×6, Gateway×5, Assimilator×4, Nexus×3, Zealot×2, CyberneticsCore×1, Forge×1, RoboticsFacility×1, TwilightCouncil×1, Observer×1, Stargate×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 31 | 200 | 150 | 25 | 24 |
| 6 | 58 | 57 | 1000 | 1400 | 39 | 34 |
| 8 | 67 | 68 | 775 | 1575 | 46 | 41 |
| 12 | 107 | 94 | 1625 | 3225 | 70 | 52 |

## Strengths

- Occasionally competitive but no reliable strength in this sample.

## Weaknesses

- Broadly losing (37-89), worst vs Protoss (8-27) and Zerg (7-23).

## How to beat it

1. Macro straight up; it is not converting its gateway/robo army well right now. Force splash-favorable fights.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*