# MicroMachine

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A famous **marine-micro specialist** (Terran, C++). Its whole identity is *unit control*: it splits, kites, and focus-fires marines to win fights it should lose on paper. Dominant vs Terran in-sample (135-1).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~2094 (top-tier ladder bot) |
| **On ladder since** | 2019-06 |
| **Last source update** | 2022-05-11 |
| **Source public** | yes (public zip, but compiled/binary — profiled from replays + record) |

## Strategy

**Opening:** Marine-heavy bio; prioritizes army control over economy/tech.

- Elite marine micro — stutter-step kiting and splits that beat larger or splashier armies through control alone (the micro-multiplies-army principle).
- Leans on winning engagements rather than out-macroing.

## Performance (recent ladder sample)

**Overall: 138–8 (94%)** over 146 decided games (+4 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 135-1 | 99% |
| vs Protoss | 2-5 | 28% |
| vs Zerg | 1-2 | 33% |

**Toughest opponents:** TyrP 0-2 (P), TyrZ 1-2 (Z), AdditionalPylons 0-1 (P), ThreeWayLover 0-1 (P), SharpenedEdge 1-1 (P), dantheman 4-1 (T).

**Best matchups:** TestBot 128-0 (T), dantheman 4-1 (T), BetterWorkerRush 1-0 (P), dantheman_3 1-0 (T), Jensiiibot 1-0 (T), AllBot 1-0 (T), SharpenedEdge 1-1 (P), TyrZ 1-2 (Z).

## Strengths

- Best marine control on the ladder — wins fights massively outnumbered.
- Crushes other bio/Terran bots that can't match its control.

## Weaknesses

- Economy/macro is secondary — a greedy macro opponent can out-produce it.
- Struggles vs Protoss (2-5) — colossus/storm/immortal splash and gateway mass blunt marine micro.
- Heavy splash (banelings, tanks, storm, colossus) is the hard counter.

## How to beat it

1. Never fight marines head-on in the open. Bring splash — banelings (Z), storm/colossus (P), tanks/mines (T).
2. Out-macro it: it under-invests in economy, so a bigger army eventually overwhelms even perfect micro.
3. Use air / cliff harass it can't micro against efficiently.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*