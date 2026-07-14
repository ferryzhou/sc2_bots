# SharpenedEdge

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

An established **Protoss** macro bot that dominates Random (27-1) and Protoss (29-7) but has a clear Terran problem. (Closed source — build not captured; from record + reputation.)

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~2042 (top-tier ladder bot) |
| **On ladder since** | 2019-06 |
| **Last source update** | 2025-11-13 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Gateway/robo/templar Protoss macro with upgrades and a deathball mid-game.

## Performance (recent ladder sample)

**Overall: 91–51 (64%)** over 142 decided games (+8 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 35-43 | 44% |
| vs Protoss | 29-7 | 80% |
| vs Random | 27-1 | 96% |

**Toughest opponents:** MicroMachine 3-19 (T), Jensiiibot 3-12 (T), TestBot 7-10 (T), m1ndb0t-P 2-2 (P), TheHarvester 1-1 (P), TyrP 3-2 (P).

**Best matchups:** A.L.E.R.T. 22-0 (R), AdditionalPylons 12-0 (P), ANIbot 11-1 (T), BetterWorkerRush 8-2 (P), A.L.E.R.T.-dev 5-1 (R), Ketroc 5-1 (T), BenBotBC 4-0 (T), Sharpy_MadAI 2-0 (P).

## Strengths

- Excellent vs Protoss and Random; strong, disciplined macro.

## Weaknesses

- Its glaring weakness is Terran (35-43) — bio-tank / mech splash and drops give it trouble.

## How to beat it

1. As Terran, bring tanks + drops and out-position the deathball; the record says Terran is the counter.
2. Force splash-favorable, multi-front fights rather than one big engagement.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*