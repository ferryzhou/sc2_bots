# Caninana

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **micro-heavy macro Zerg** (C++, the MicroCaninana/Caninana family). Strong economy with well-controlled roach/ling/hydra. Especially strong vs Protoss (47-21). (Closed source — from record + family reputation.)

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~2025 (top-tier ladder bot) |
| **On ladder since** | 2022-02 |
| **Last source update** | 2026-06-16 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Macro Zerg with good unit control; roach/ling/hydra with creep and remax.

## Performance (recent ladder sample)

**Overall: 92–54 (63%)** over 146 decided games (+4 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 20-17 | 54% |
| vs Protoss | 47-21 | 69% |
| vs Zerg | 25-15 | 62% |
| vs Random | 0-1 | 0% |

**Toughest opponents:** DominionDog 2-6 (T), Ketroc 3-5 (T), Dovahkiin 0-2 (Z), Rasputin 0-2 (Z), MechaShark 0-2 (T), BenBotBC 0-2 (T), Tyckles 0-1 (P), SaShaBot 0-1 (Z).

**Best matchups:** One-Test 28-17 (P), LucidPJS 9-1 (P), LucidTJS 9-1 (T), QueenBot 6-0 (Z), One 6-1 (P), Trinity 4-0 (P), SHIELD-TEST 4-0 (T), PhantomTest 11-8 (Z).

## Strengths

- Dominant vs Protoss (47-21); solid economy + micro.

## Weaknesses

- Weaker vs Terran (20-17, near-even) — tank/mech splash is the usual answer.
- Standard macro-Zerg timing vulnerability.

## How to beat it

1. Terran splash (tanks/mech) and defensive positioning.
2. Hit a timing before its economy + remax take over; deny creep.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*