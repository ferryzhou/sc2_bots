# ur_moms_a_ho

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Zerg** bot with only a small recent sample (12-7). In the one replay captured it barely developed (a very short game), so its full plan isn't well characterized yet — scout it directly.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1600 (top-tier ladder bot) |
| **On ladder since** | 2025-11 |
| **Last source update** | 2025-11-02 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Zerg (macro or rush unclear from the small sample — treat as unknown until scouted).

## Performance (recent ladder sample)

**Overall: 12–7 (63%)** over 19 decided games (+9 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 4-2 | 66% |
| vs Protoss | 6-4 | 60% |
| vs Zerg | 2-1 | 66% |

**Toughest opponents:** 27turtles 0-1 (T), LiShiMinV2 0-1 (P), 49Terrapins 0-1 (P), nida 0-1 (P), Alexa 0-1 (T), QueenBot 0-1 (Z), negativeZero 1-1 (P).

**Best matchups:** Lighter 1-0 (P), BigDaddy 1-0 (T), GenesisLotus 1-0 (P), PiG_Bot 1-0 (P), SacripantaBot 1-0 (T), Siumon 1-0 (P), zig-reapers 1-0 (T), PrimordialOrigin 1-0 (P).

## Observed builds (from its own replays)

**vs Alexa (T), 19.5 min, lost:** Drone×12, Hatchery×1, Overlord×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 0 | 19 | 0 | 100 | 0 | 15 |
| 6 | 0 | 21 | 0 | 200 | 0 | 16 |
| 8 | 0 | 28 | 0 | 200 | 0 | 23 |
| 12 | 0 | 53 | 0 | 200 | 0 | 46 |

**vs LiShiMinV2 (P), 14.5 min, lost:** Drone×12, Hatchery×1, Overlord×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 12 | 15 | 0 | 0 | 12 | 14 |
| 6 | 12 | 16 | 0 | 0 | 12 | 16 |
| 8 | 12 | 2 | 0 | 0 | 12 | 2 |
| 12 | 12 | 2 | 0 | 0 | 12 | 2 |

**vs QueenBot (Z), 13.9 min, lost:** Drone×12, Hatchery×1, Overlord×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 0 | 29 | 0 | 350 | 0 | 23 |
| 6 | 0 | 28 | 0 | 700 | 0 | 17 |
| 8 | 0 | 39 | 0 | 1400 | 0 | 19 |
| 12 | 0 | 60 | 0 | 3700 | 0 | 18 |

## Strengths

- Slightly winning overall (12-7), best vs Protoss (6-4).

## Weaknesses

- Small, noisy sample — no reliable read yet.

## How to beat it

1. Scout early and play standard-safe vs Zerg until its build is seen (wall vs a possible rush, splash vs mass light).

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*