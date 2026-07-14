# JimmyBotP

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

The Protoss variant of the **Jimmy** family: gateway/robo with stalker/immortal and oracle harass.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1887 (top-tier ladder bot) |
| **On ladder since** | 2026-03 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway expand into cyber/robo; stalker/immortal army with oracle harass off 2-3 bases.

- Stalker/immortal core (immortals vs armored) with oracle worker harass.

## Performance (recent ladder sample)

**Overall: 60–78 (43%)** over 138 decided games (+12 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 14-17 | 45% |
| vs Protoss | 17-19 | 47% |
| vs Zerg | 27-37 | 42% |
| vs Random | 2-5 | 28% |

**Toughest opponents:** QueenBot 0-5 (Z), Crawler 0-5 (Z), Apidae 0-4 (P), BigDaddy 0-4 (T), norman 0-4 (P), nida 0-4 (P), TheLAW 0-4 (T), WaterLeak 0-3 (Z).

**Best matchups:** PolyMorph 4-0 (Z), onlyfans 4-1 (T), 49Terrapins 3-0 (P), KoB 3-1 (Z), DoopyBot 3-1 (Z), JimmyBotZ 3-1 (Z), smokinggunbot 3-1 (T), titania 2-0 (Z).

## Observed builds (from its own replays)

**vs 72Tortoises (Z), 48.9 min, lost:** Probe×41, Stalker×9, Pylon×7, Assimilator×4, Nexus×2, Immortal×2, Gateway×1, CyberneticsCore×1, RoboticsFacility×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 46 | 350 | 1350 | 34 | 22 |
| 6 | 33 | 68 | 525 | 1225 | 21 | 36 |
| 8 | 51 | 104 | 1900 | 1950 | 23 | 57 |
| 12 | 92 | 200 | 3400 | 7550 | 47 | 79 |

**vs 27turtles (T), 44.3 min, lost:** Probe×51, Pylon×6, Stalker×6, Nexus×3, Assimilator×3, Gateway×3, Oracle×3, Sentry×2, CyberneticsCore×1, RoboticsFacility×1, Immortal×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 32 | 35 | 175 | 300 | 26 | 24 |
| 6 | 53 | 62 | 1175 | 1050 | 39 | 35 |
| 8 | 83 | 94 | 2575 | 2225 | 51 | 49 |
| 12 | 42 | 153 | 0 | 4350 | 34 | 78 |

**vs 27turtles (T), 43.2 min, lost:** Probe×55, Stalker×8, Pylon×7, Nexus×3, Gateway×3, Assimilator×3, CyberneticsCore×1, RoboticsFacility×1, Immortal×1, Forge×1, TwilightCouncil×1, Sentry×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 29 | 350 | 150 | 29 | 24 |
| 6 | 61 | 59 | 1225 | 1150 | 43 | 36 |
| 8 | 86 | 85 | 2250 | 2200 | 57 | 49 |
| 12 | 65 | 130 | 175 | 3050 | 57 | 76 |

## Strengths

- Immortals hard-counter armored units; oracle pressures economies.

## Weaknesses

- Losing recent form (60-78); vulnerable vs Zerg (27-37) — mass army swarms gateway/robo.
- Oracle/stalker army is light on splash.

## How to beat it

1. Anti-air for the oracle (don't feed it workers); then out-macro the gateway/robo army.
2. As Zerg, mass army + splash; as Terran, tanks + position.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*