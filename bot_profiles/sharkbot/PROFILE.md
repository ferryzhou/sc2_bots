# sharkbot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Protoss** bot (.NET) that is strong vs Protoss (22-5) and Zerg. (Closed source — from record + reputation.)

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1903 (top-tier ladder bot) |
| **On ladder since** | 2020-07 |
| **Last source update** | 2026-07-09 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Gateway/robo Protoss macro with upgrades and a solid deathball.

## Performance (recent ladder sample)

**Overall: 76–49 (60%)** over 125 decided games (+25 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 41-39 | 51% |
| vs Protoss | 22-5 | 81% |
| vs Zerg | 11-4 | 73% |
| vs Random | 2-1 | 66% |

**Toughest opponents:** BugFinder 0-5 (T), TestBot 2-6 (T), MicroMachine 0-4 (T), spudde 3-5 (T), WorthlessBot 0-2 (Z), Ketroc 1-2 (T), BlinkerBot 0-1 (P), Jensiiibot 0-1 (T).

**Best matchups:** BenBotBC 26-7 (T), m1ndb0t-P 14-2 (P), Trolly 3-0 (P), Snowbot 3-0 (Z), BaronessZuli 2-0 (Z), KAI 2-0 (T), sharpy_PVP_EZ 2-0 (P), ANI_dev 4-3 (T).

## Strengths

- Dominant in the Protoss mirror (22-5); strong vs Zerg (11-4).

## Weaknesses

- Even vs Terran (41-39) — the tank/drop matchup is its closest.

## How to beat it

1. As Terran, bio-tank + drops; don't attack the deathball head-on.
2. Match upgrades and force splash-favorable, multi-front fights.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*