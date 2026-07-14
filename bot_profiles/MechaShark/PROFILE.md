# MechaShark

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran** bot (the mech-flavored member of the shark* family). Strong vs Zerg (21-10) but struggles vs Protoss (39-60). (Closed source, build not captured — from race + record.)

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1849 (top-tier ladder bot) |
| **On ladder since** | 2021-09 |
| **Last source update** | 2026-03-03 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Terran macro (bio and/or mech — not observed this sample; scout it).

## Performance (recent ladder sample)

**Overall: 65–81 (44%)** over 146 decided games (+4 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 5-11 | 31% |
| vs Protoss | 39-60 | 39% |
| vs Zerg | 21-10 | 67% |

**Toughest opponents:** negativeZero 35-55 (P), Zoe 2-8 (Z), BenBotBC 1-7 (T), FourGateBot 0-3 (P), ZoeDev 0-1 (Z), Ketroc 0-1 (T), DominionDog 0-1 (T), One-Test 0-1 (P).

**Best matchups:** BaronessZuli 7-0 (Z), PhantomTest 5-1 (Z), SharkbotTest 4-1 (P), spudde 4-2 (T), 12PoolBot 2-0 (Z), Caninana 2-0 (Z), RoachRush 1-0 (Z), SunTzuBot 1-0 (Z).

## Strengths

- Good vs Zerg (21-10) — tanks/mech splash punish roach/ling.

## Weaknesses

- Weak vs Protoss (39-60) and in the Terran mirror (5-11) in-sample.

## How to beat it

1. As Protoss, the sample strongly favors you — immortals/colossus + storm; don't run into sieged mech.
2. Exploit any mech immobility with drops/multi-prong.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*