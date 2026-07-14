# TyrT

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

The Terran variant of the **Tyr** family (.NET). Standard Terran macro. (Closed source — from record + family.)

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1884 (top-tier ladder bot) |
| **On ladder since** | 2020-07 |
| **Last source update** | 2026-05-02 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Terran bio or mech macro (family standard); expands with upgrades.

## Performance (recent ladder sample)

**Overall: 71–73 (49%)** over 144 decided games (+6 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 16-30 | 34% |
| vs Protoss | 20-15 | 57% |
| vs Zerg | 26-23 | 53% |
| vs Random | 9-5 | 64% |

**Toughest opponents:** BenBotBC 9-16 (T), Dysnomia 2-7 (Z), Jensiiibot 1-3 (T), Eris 0-2 (Z), negativeZero 0-2 (P), Xena 0-2 (R), XenaP 0-2 (P), XenaT 0-2 (T).

**Best matchups:** FourGateDev 5-2 (P), Trolly 3-1 (P), Ketroc 2-0 (T), m1ndb0t-P 2-0 (P), Snowbot 2-0 (Z), Noobgam2 2-0 (P), zUnkP 2-0 (T), Caninana 2-0 (Z).

## Strengths

- Competitive across matchups; best vs Protoss (20-15) in-sample.

## Weaknesses

- Weak vs Terran (16-30) — loses the mirror.

## How to beat it

1. In the Terran mirror the sample favors you — tank count + position.
2. Bring splash (P/Z) and exploit any mech immobility.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*