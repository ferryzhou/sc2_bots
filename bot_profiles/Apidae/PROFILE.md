# Apidae

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **cannon-turtle / cannon-rush Protoss** (Java). Forge + photon cannons for defense/aggression, teching behind. Even form (77-68).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | java |
| **AI Arena Elo** | ~1718 (top-tier ladder bot) |
| **On ladder since** | 2022-11 |
| **Last source update** | 2024-09-29 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Forge-first into photon cannons (defensive rings or a cannon rush).

- Static cannon defense + tech; can turn a cannon rush into an opponent's base.
- Wins by shutting down aggression and out-teching behind cannons.

## Performance (recent ladder sample)

**Overall: 77–68 (53%)** over 145 decided games (+5 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 19-14 | 57% |
| vs Protoss | 19-20 | 48% |
| vs Zerg | 29-28 | 50% |
| vs Random | 10-6 | 62% |

**Toughest opponents:** Darkness 0-5 (P), Nikolaj 0-5 (T), DadBotTest 1-5 (Z), Sharkling 1-5 (Z), Dovahkiin 0-4 (Z), Ku6ikRu6ika 0-4 (P), SaShaBot 1-4 (Z), AIX1 1-4 (T).

**Best matchups:** XenaP 6-0 (P), PhantomBot 6-0 (Z), BrazilianLingFloodBot 5-0 (Z), 27turtles 5-0 (T), TyrP 3-0 (P), Tyr 4-2 (R), whalemean 3-1 (R), Chance 3-1 (R).

## Strengths

- Cannons punish frontal attacks and can end games early vs a bot that doesn't scout the rush.

## Weaknesses

- Immobile — cedes map and expansions; beaten by out-expanding.
- A scouted cannon rush that's denied leaves it behind.

## How to beat it

1. Scout early for a cannon rush (probe/pylon near your base) and deny it.
2. Don't attack into cannons — out-expand and out-macro the turtle; siege it from range (tanks/tempest).

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*