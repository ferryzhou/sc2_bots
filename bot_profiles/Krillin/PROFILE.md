# Krillin

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A simple **12-pool mass-speedling aggro Zerg** (open source, older python-sc2 bot). It opens 12-pool, gets metabolic boost, injects with queens, and a-moves zerglings at the enemy. Even-ish form (58-67) but very weak vs Terran (3-24).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1600 (top-tier ladder bot) |
| **On ladder since** | 2019-06 |
| **Last source update** | 2019-10-05 |
| **Source public** | yes — Python source read directly for this profile |

## Strategy

**Opening:** 12-pool (drone to 12, Spawning Pool, Extractor) into Metabolic Boost (ling speed); queens for injects.

- Pumps zerglings and sends them to attack the enemy (idle lings a-move the enemy base/structures) — a straightforward speedling aggression bot.
- Queens inject the hatchery for larva; a natural 'rush-wait' position lets it pressure or defend.
- Minimal tech/economy beyond lings + speed — an older, simple design.

## Performance (recent ladder sample)

**Overall: 58–67 (46%)** over 125 decided games (+25 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 3-24 | 11% |
| vs Protoss | 18-13 | 58% |
| vs Zerg | 19-15 | 55% |
| vs Random | 18-15 | 54% |

**Toughest opponents:** TestBot 2-16 (T), Xena 1-9 (R), Tyckles 0-2 (P), negativeZero 0-2 (P), SaShaBot 0-2 (Z), TyrT 0-2 (T), TyrP 1-2 (P), ErisTest 0-1 (Z).

**Best matchups:** A.L.E.R.T. 17-3 (R), Ku6ikRu6ika 10-3 (P), PhantomTest 4-1 (Z), BaronessZuli 3-0 (Z), sharkbot 2-0 (P), LucidZJS 2-0 (Z), DadBot 2-1 (Z), PhantomBot 2-1 (Z).

## Strengths

- Early speedling pressure can overwhelm greedy or un-walled openings; competitive vs Protoss (18-13) and Random (18-15).
- Simple and consistent — always applies ling pressure.

## Weaknesses

- Badly weak vs Terran (3-24) — tanks/hellions/mines splash the a-moving lings apart.
- One-dimensional: little tech or splash, and the a-move lings feed into walls and defensive positions.
- Thin economy behind the aggression.

## How to beat it

1. Wall + splash (tanks/hellions as T, storm/colossus, banelings) and hold — the a-move lings break on static defence.
2. Survive the ling aggression, then out-macro its thin economy.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*