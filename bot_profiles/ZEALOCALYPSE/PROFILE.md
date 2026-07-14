# ZEALOCALYPSE

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Protoss zealot-flood** bot: mass zealots (30+) off 4 gateways — a zealot all-in/timing. Crushes Zerg (40-13) but is demolished by Terran (3-21).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1623 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-05-30 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway-heavy zealot mass (little economy); a-move the zealot flood.

- Pump zealots from many gateways and flood — end the game before splash/economy matter.
- Warp-in reinforcements re-flood a broken engagement.

## Performance (recent ladder sample)

**Overall: 75–56 (57%)** over 131 decided games (+19 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 3-21 | 12% |
| vs Protoss | 25-21 | 54% |
| vs Zerg | 40-13 | 75% |
| vs Random | 7-1 | 87% |

**Toughest opponents:** nida 0-6 (P), 27turtles 0-5 (T), smokinggunbot 0-5 (T), BigDaddy 0-4 (T), Dodo 0-3 (Z), Forgefiend 0-3 (P), TheLAW 2-4 (T), KoB 1-3 (Z).

**Best matchups:** Lissy 6-0 (Z), SharkGull 6-0 (Z), Montka 6-0 (R), muravev 6-0 (Z), Lighter 5-0 (P), Crawler 5-0 (Z), PiG_Bot 5-1 (P), QueenBot 4-0 (Z).

## Observed builds (from its own replays)

**vs PiG_Bot (P), 73.9 min, won:** Zealot×32, Probe×18, Pylon×8, Gateway×4, Nexus×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 31 | 700 | 325 | 18 | 26 |
| 6 | 58 | 32 | 1600 | 450 | 18 | 24 |
| 8 | 82 | 26 | 2800 | 450 | 18 | 18 |
| 12 | 110 | 33 | 4500 | 300 | 18 | 27 |

**vs 27turtles (T), 44.4 min, lost:** Probe×32, Zealot×22, Pylon×7, Gateway×4, Nexus×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 41 | 32 | 1100 | 250 | 14 | 24 |
| 6 | 54 | 60 | 1800 | 700 | 18 | 35 |
| 8 | 33 | 60 | 1200 | 1425 | 4 | 33 |
| 12 | 4 | 124 | 200 | 3100 | 0 | 61 |

**vs 27turtles (T), 43.8 min, lost:** Probe×34, Zealot×13, Pylon×4, Gateway×4, Nexus×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 15 | 34 | 0 | 350 | 14 | 24 |
| 6 | 26 | 56 | 600 | 700 | 5 | 38 |
| 8 | 38 | 89 | 1600 | 1700 | 5 | 50 |
| 12 | 40 | 156 | 800 | 4325 | 18 | 73 |

## Strengths

- Zealot flood overwhelms mass-light Zerg and the unprepared (40-13 vs Zerg).
- Overwhelming melee numbers at its timing.

## Weaknesses

- Hard-countered by Terran splash (3-21) — tanks/hellions/mines melt zealots; melee stalls at a wall.
- Thin economy — a held flood loses.

## How to beat it

1. Wall + splash (tanks/hellions as T, storm/colossus, banelings) and hold — never fight zealots in the open.
2. Survive the timing, then punish the dead economy.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*