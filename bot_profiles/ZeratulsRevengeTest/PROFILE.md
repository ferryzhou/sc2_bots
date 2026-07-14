# ZeratulsRevengeTest

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Protoss** zealot-based test/dev bot currently performing very poorly (15-105) — it loses almost every game in this sample, so treat it as an unstable work-in-progress rather than a ladder threat.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1794 (top-tier ladder bot) |
| **On ladder since** | 2025-10 |
| **Last source update** | 2025-11-02 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway zealot mass (25 zealots seen) — a zealot all-in/pressure that isn't currently working.

- Zealot-heavy gateway aggression; in its current state it fails to convert or defend.

## Performance (recent ladder sample)

**Overall: 15–105 (12%)** over 120 decided games (+30 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 3-32 | 8% |
| vs Protoss | 7-44 | 13% |
| vs Zerg | 4-22 | 15% |
| vs Random | 1-7 | 12% |

**Toughest opponents:** 27turtles 0-5 (T), Siumon 0-5 (P), LiShiMinV2 0-5 (P), GenesisLotus 1-5 (P), RustyNikolaj 0-4 (T), 49Terrapins 0-4 (P), Han 0-4 (T), SiriusBot 0-4 (R).

**Best matchups:** BotTato 1-1 (T), Chance 1-1 (R), Princess-Mika-Test 2-3 (Z), PrimordialOrigin 2-3 (P), Princess-Mika 2-3 (Z).

## Observed builds (from its own replays)

**vs 49Terrapins (P), 48.2 min, lost:** Zealot×25, Probe×22, Pylon×10, Gateway×3, Assimilator×2, Nexus×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 46 | 35 | 1000 | 525 | 22 | 27 |
| 6 | 66 | 66 | 1900 | 1475 | 22 | 43 |
| 8 | 86 | 94 | 2900 | 2225 | 22 | 57 |
| 12 | 126 | 185 | 4900 | 5425 | 22 | 80 |

**vs 27turtles (T), 46.6 min, lost:** Probe×19, Stalker×16, Pylon×8, Gateway×3, Zealot×3, Assimilator×2, Nexus×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 41 | 30 | 1175 | 300 | 19 | 24 |
| 6 | 53 | 58 | 2400 | 650 | 19 | 36 |
| 8 | 59 | 70 | 3275 | 1575 | 19 | 45 |
| 12 | 59 | 85 | 3275 | 2625 | 19 | 45 |

**vs 27turtles (T), 44.8 min, lost:** Probe×19, Stalker×10, Zealot×5, Pylon×4, Gateway×3, Assimilator×2, Nexus×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 29 | 21 | 575 | 200 | 17 | 17 |
| 6 | 25 | 25 | 350 | 200 | 17 | 19 |
| 8 | 27 | 44 | 525 | 500 | 17 | 32 |
| 12 | 25 | 92 | 350 | 2250 | 17 | 53 |

## Strengths

- None reliable in the current sample — it is losing across all matchups.

## Weaknesses

- Broken/underperforming: 15-105, worst vs Protoss (7-44).

## How to beat it

1. Play straight up and macro — it is not defending or converting its zealot aggression right now.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*