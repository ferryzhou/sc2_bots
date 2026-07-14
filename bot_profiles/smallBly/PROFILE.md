# smallBly

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Zerg** bot, mid-pack recent form (63-77 sample). (Closed source, no build captured — characterization from race + record.)

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1996 (top-tier ladder bot) |
| **On ladder since** | 2021-08 |
| **Last source update** | 2026-04-26 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

- Zerg macro/aggression (exact build not observed this sample — scout it).

## Performance (recent ladder sample)

**Overall: 63–77 (45%)** over 140 decided games (+10 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 23-32 | 41% |
| vs Protoss | 13-25 | 34% |
| vs Zerg | 27-19 | 58% |
| vs Random | 0-1 | 0% |

**Toughest opponents:** negativeZero 0-12 (P), spudde 1-8 (T), ZoeDev 0-7 (Z), BenBotBC 8-14 (T), RStrelok 0-3 (T), VeTerran 0-3 (T), TheGoldenArmada 0-2 (P), FourGateBot 0-2 (P).

**Best matchups:** SunTzuBot 6-0 (Z), BaronessZuli 6-0 (Z), ANI_dev 9-4 (T), MLP 3-1 (P), WizardHat 3-1 (P), Strelok 2-0 (T), SluggerBot-alpha 2-0 (T), PhantomTest 2-0 (Z).

## Strengths

- Competitive vs Zerg (27-19) in-sample.

## Weaknesses

- Struggles vs Protoss (13-25) in the recent sample.

## How to beat it

1. As Protoss, the sample says you're favored — standard anti-Zerg splash + macro.
2. Scout the build directly; treat as a standard macro/aggro Zerg until seen.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*