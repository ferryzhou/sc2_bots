# Xena

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **Random** bot (C++). Plays all three races (its XenaP / XenaT / XenaZ variants each specialize), so the race is unknown until you scout. (Closed source — characterization from record + variant family.)

## Identity

| | |
|---|---|
| **Race** | Random |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~2103 (top-tier ladder bot) |
| **On ladder since** | 2022-06 |
| **Last source update** | 2025-09-30 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Race is random each game — must be scouted. Each race plays a solid macro game tuned by its dedicated variant.

## Performance (recent ladder sample)

**Overall: 90–56 (61%)** over 146 decided games (+4 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 18-14 | 56% |
| vs Protoss | 15-14 | 51% |
| vs Zerg | 49-26 | 65% |
| vs Random | 8-2 | 80% |

**Toughest opponents:** EvilZoe 1-8 (Z), negativeZero 1-6 (P), MicroMachine 1-5 (T), BenBotBC 2-5 (T), 12PoolBot 1-4 (Z), Dysnomia 1-4 (Z), Eris 2-4 (Z), sharkbot 1-2 (P).

**Best matchups:** Krillin 8-1 (Z), Zoe 6-0 (Z), XenaT 5-1 (T), Zozo 4-1 (P), DadBotTest 3-0 (Z), whalemean 3-0 (R), TyrT 3-0 (T), XenaZ 4-2 (Z).

## Strengths

- Unpredictable race choice denies pre-game preparation.
- Strong all-around, especially vs Zerg (49-26).

## Weaknesses

- As a generalist, each race line is a notch less specialized than a dedicated single-race bot.

## How to beat it

1. Scout the race immediately and apply the standard counter for that matchup.
2. Play safe early until the race and build are known.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*