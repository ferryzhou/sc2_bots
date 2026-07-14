# QueenBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **queen/creep macro Zerg**: heavy queen count with mass creep spread and a big drone economy, into roach/ling. Defensive macro. Strong vs Terran in a large sample (51-41).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1611 (top-tier ladder bot) |
| **On ladder since** | 2020-10 |
| **Last source update** | 2026-03-06 |
| **Source public** | yes (Python source publicly downloadable; this profile is from replays + record) |

## Strategy

**Opening:** Economic Zerg; many queens + spore/spine, mass creep tumors, drone-heavy.

- Queens + static defense + creep to defend, drone hard, remax roach/ling late.
- Very defensive early — leans on queens/creep to survive to a macro game.

## Performance (recent ladder sample)

**Overall: 76–61 (55%)** over 137 decided games (+13 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 51-41 | 55% |
| vs Protoss | 15-8 | 65% |
| vs Zerg | 9-7 | 56% |
| vs Random | 1-5 | 16% |

**Toughest opponents:** ANI_dev 2-8 (T), TestBot 0-6 (T), MicroMachine 0-2 (T), Chance 0-2 (R), TheGoldenArmada 0-2 (P), BenBotv3 0-1 (T), Fidolina 0-1 (T), Ketroc 0-1 (T).

**Best matchups:** BenBotBC 34-14 (T), Chaosbot 12-5 (T), MavBot 5-1 (P), Excess1972 5-2 (Z), Noobgam2 3-0 (P), BraxBot 2-0 (P), Paul 1-0 (Z), NewBy 1-0 (T).

## Strengths

- Strong defensive economy; good vs Terran (51-41) and Protoss (15-8).

## Weaknesses

- Queen-heavy is slow/immobile early — punishable by fast pressure; roach/ling lacks splash.
- Cedes map control while turtling on creep.

## How to beat it

1. Pressure before its economy snowballs; out-range roaches (tanks/colossus).
2. Take the map — it turtles; deny creep spread.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*