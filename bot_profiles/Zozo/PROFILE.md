# Zozo

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **Protoss** macro bot. (Closed source and no build captured this sample — characterization from race + record.)

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~2109 (top-tier ladder bot) |
| **On ladder since** | 2022-08 |
| **Last source update** | 2026-04-22 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Gateway-based Protoss macro; expands and builds a mixed gateway/robo army with upgrades (typical of a bot at this rating).

## Performance (recent ladder sample)

**Overall: 96–53 (64%)** over 149 decided games (+1 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 40-19 | 67% |
| vs Protoss | 12-13 | 48% |
| vs Zerg | 35-17 | 67% |
| vs Random | 9-4 | 69% |

**Toughest opponents:** negativeZero 0-5 (P), Eris 0-4 (Z), Dysnomia 0-4 (Z), Zoe 0-4 (Z), Xena 1-4 (R), XenaP 1-4 (P), TyrP 0-3 (P), QueenBot 0-2 (Z).

**Best matchups:** BenBotBC 25-17 (T), SharkbotTest 7-1 (P), XenaT 6-1 (T), 12PoolBot 4-0 (Z), XenaZ 4-1 (Z), MicroMachine 4-1 (T), DadBotTest 3-0 (Z), DadBot 3-0 (Z).

## Strengths

- Well-rounded record; strong vs Zerg (35-17) and Terran (40-19) in-sample.

## Weaknesses

- Roughly even vs Protoss (12-13) — the mirror comes down to execution.
- Build not observed here; scout it directly before committing.

## How to beat it

1. Standard anti-Protoss: match upgrades, force splash-favorable fights, don't attack into a defended position.
2. Scout its tech (robo vs stargate vs templar) and prepare the specific answer.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*