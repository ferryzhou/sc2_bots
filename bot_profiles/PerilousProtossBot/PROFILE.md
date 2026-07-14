# PerilousProtossBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Protoss** bot (zealot/cannon pressure) currently **badly underperforming** (15-121) — losing nearly every game, especially vs Zerg (2-60). Not a functional threat in its current state.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1666 (top-tier ladder bot) |
| **On ladder since** | 2022-09 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway zealot + photon cannon pressure (from prior observation).

- Zealot/cannon aggression that is not currently converting.

## Performance (recent ladder sample)

**Overall: 15–121 (11%)** over 136 decided games (+14 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 7-33 | 17% |
| vs Protoss | 6-17 | 26% |
| vs Zerg | 2-60 | 3% |
| vs Random | 0-11 | 0% |

**Toughest opponents:** Roro 0-7 (T), BenBotBC 0-7 (T), JaProBot 2-8 (P), BaronessZuli 0-6 (Z), PhantomBot 0-6 (Z), QueenBot 0-6 (Z), LucidZJS 0-6 (Z), SharkyRandomExampleBot 0-5 (R).

**Best matchups:** LucidPJS 4-1 (P), supabot 3-1 (T), Nikolaj 3-2 (T), Dovahkiin 1-0 (Z), AlienAsh 1-1 (Z).

## Strengths

- None reliable in the current sample.

## Weaknesses

- Broadly losing (15-121); collapses vs Zerg mass army (2-60).

## How to beat it

1. Macro straight up; it is not defending or converting right now — a free win with basic safety.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*