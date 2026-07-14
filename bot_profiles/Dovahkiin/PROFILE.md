# Dovahkiin

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **macro Zerg**, even-ish form (60-69). (Closed source, build not captured — from race + record.)

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~1697 (top-tier ladder bot) |
| **On ladder since** | 2021-06 |
| **Last source update** | 2022-11-19 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Zerg macro (roach/ling/drone — build not observed; scout it).

## Performance (recent ladder sample)

**Overall: 60–69 (46%)** over 129 decided games (+21 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 12-19 | 38% |
| vs Protoss | 23-26 | 46% |
| vs Zerg | 21-19 | 52% |
| vs Random | 4-5 | 44% |

**Toughest opponents:** BenBotBC 0-8 (T), Zoe 3-8 (Z), SkevidBotP 1-5 (P), SF4G 0-3 (P), Eris 0-2 (Z), spudde 0-2 (T), whalemean 3-4 (R), Monte 1-2 (T).

**Best matchups:** negativeZero 10-6 (P), LucidPJSTest 4-0 (P), smallBly 5-2 (Z), ANI_dev 4-1 (T), Nibbles 2-0 (Z), MFBS 3-2 (P), Chaosbot 2-1 (T), BaronessZuli 2-1 (Z).

## Strengths

- Competitive vs Protoss (23-26) and Zerg (21-19).

## Weaknesses

- Weak vs Terran (12-19) — tanks/mech splash punish it.

## How to beat it

1. As Terran, tanks/mech + splash and hold position; hit a timing before its remax.
2. Deny creep; out-range its army.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*