# TyrP

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Protoss** bot (the Tyr family, .NET). Gateway-based macro. Weak vs Terran in-sample (32-48). (Closed source — from record + family.)

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1933 (top-tier ladder bot) |
| **On ladder since** | 2019-07 |
| **Last source update** | 2026-07-12 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Gateway/robo Protoss macro (typical for the family); expands into a mixed army with upgrades.

## Performance (recent ladder sample)

**Overall: 77–67 (53%)** over 144 decided games (+6 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 32-48 | 40% |
| vs Protoss | 14-7 | 66% |
| vs Zerg | 13-12 | 52% |
| vs Random | 18-0 | 100% |

**Toughest opponents:** TestBot 5-23 (T), Jensiiibot 13-21 (T), SharpenedEdge 1-3 (P), Spiny 4-5 (Z), Blunty 1-2 (Z), Kagamine 3-3 (Z), Rusty 2-2 (T), RoachRush 1-1 (Z).

**Best matchups:** A.L.E.R.T. 18-0 (R), ThreeWayLover 6-2 (P), dantheman 4-0 (T), Strelok 4-1 (T), Sharpy_MadAI 3-1 (P), MicroMachine 2-0 (T), BetterWorkerRush 2-1 (P), TheCinderBlock 1-0 (Z).

## Strengths

- Undefeated vs Random (18-0) and favorable vs Protoss (14-7) in-sample.

## Weaknesses

- Clear Terran weakness (32-48) — bio-tank + drops out-trade it.

## How to beat it

1. As Terran, the record says you're favored — tanks, drops, splash, position.
2. Scout its tech and prepare the specific answer (immortal vs your armored, etc.).

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*