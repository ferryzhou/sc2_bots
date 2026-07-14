# PhantomTest

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Zerg** dev/test bot currently performing poorly (31-109), collapsing vs Protoss (10-74). A work-in-progress, not a current threat. (Build not captured.)

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1600 (top-tier ladder bot) |
| **On ladder since** | 2021-11 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Zerg macro/aggression that isn't currently converting.

## Performance (recent ladder sample)

**Overall: 31–109 (22%)** over 140 decided games (+10 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 5-12 | 29% |
| vs Protoss | 10-74 | 11% |
| vs Zerg | 16-22 | 42% |
| vs Random | 0-1 | 0% |

**Toughest opponents:** negativeZero 1-24 (P), 4GateAllin 2-15 (P), SF4G 1-10 (P), BenBotBC 0-7 (T), sharkbot 3-9 (P), buckshot 0-6 (P), SharkbotTest 1-6 (P), Zoe 2-6 (Z).

**Best matchups:** BluntMacro 3-0 (Z), 12PoolBot 3-1 (Z), BenBotv3 2-0 (T), Rusty 2-0 (T), SaShaBot 2-0 (Z), sludge-revived 1-0 (Z), DumbBot 1-0 (P), Six 1-0 (Z).

## Strengths

- Most competitive in the Zerg mirror (16-22).

## Weaknesses

- Broadly losing, especially vs Protoss (10-74).

## How to beat it

1. Macro straight up; it isn't defending or converting well right now.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*