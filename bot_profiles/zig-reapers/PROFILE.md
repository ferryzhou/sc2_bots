# zig-reapers

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **mass-reaper all-in Terran**: floods 20+ reapers off many barracks, using grenades and kiting to overwhelm early. Crushes Zerg (51-18). Aggressive timing.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~1602 (top-tier ladder bot) |
| **On ladder since** | 2023-01 |
| **Last source update** | 2026-06-10 |
| **Source public** | yes (compiled/binary zip publicly downloadable; this profile is from replays + record) |

## Strategy

**Opening:** Barracks-heavy reaper production (few SCVs, no real expansion) — a reaper flood by ~8 min.

- Mass reapers kite and grenade the opponent's army/workers before they have an answer.
- A one-base/two-base all-in — ends the game early or transitions if it did damage.

## Performance (recent ladder sample)

**Overall: 90–56 (61%)** over 146 decided games (+4 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 18-21 | 46% |
| vs Protoss | 21-16 | 56% |
| vs Zerg | 51-18 | 73% |
| vs Random | 0-1 | 0% |

**Toughest opponents:** LucidPJS 1-7 (P), SilverStalkerRush 0-6 (P), Krillin 0-5 (Z), SafeRaven 1-4 (T), RookieBot 1-3 (T), RustyTerran 1-3 (T), PerilousProtossBot 1-2 (P), XenaT 0-1 (T).

**Best matchups:** sc2_ai1 10-0 (Z), LucidZJS 8-0 (Z), Visenya 6-0 (Z), sample_protoss_bot 6-0 (P), BluntMacro 5-0 (Z), AthielBot 5-0 (P), norman 4-0 (P), LucidTJS 4-1 (T).

## Strengths

- Reaper flood shreds slow ground armies and worker lines; dominant vs Zerg (51-18) where early defense is thin.
- Grenades + kiting = strong early trades.

## Weaknesses

- Reapers are fragile — a bunker + a couple of units, or tanks/colossus, hard-counter the flood; even vs Terran (18-21).
- All-in economy — a held flood leaves it behind.

## How to beat it

1. Wall + a bunker/units, or fast splash (tanks/colossus) — hold the reaper flood, don't chase.
2. Survive the timing → its thin economy loses.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*