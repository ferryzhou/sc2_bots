# Battler

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A solid **Terran** bot with a reaper opening into bio/mech. Good record (83-54), strong vs Zerg (32-16) and Terran (14-8).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | dotnetcore |
| **AI Arena Elo** | ~1718 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-06-05 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Reaper opening (scout/harass) into a bio or mech macro with tanks.

- Reaper harass early, then a positional bio/tank macro.
- Trades efficiently with tank support and upgrades.

## Performance (recent ladder sample)

**Overall: 83–54 (60%)** over 137 decided games (+13 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 14-8 | 63% |
| vs Protoss | 30-25 | 54% |
| vs Zerg | 32-16 | 66% |
| vs Random | 7-5 | 58% |

**Toughest opponents:** Hellcannon 2-6 (P), PiG_Bot 0-4 (P), WorkingAsIntended 0-3 (R), Dodo 0-3 (Z), Lighter 0-2 (P), FlowerPrincess 0-2 (Z), 72Tortoises 0-2 (Z), PhantomBot 0-2 (Z).

**Best matchups:** Lissy 4-0 (Z), ArtZerg 4-1 (Z), Princess-Mika-Test 3-0 (Z), 27turtles 3-0 (T), Apidae 3-0 (P), Crawler 3-0 (Z), PerilousProtossBot 3-0 (P), smokinggunbot 3-0 (T).

## Observed builds (from its own replays)

**vs Hellcannon (P), 67.0 min, lost:** SCV×33, CommandCenter×2, SupplyDepot×2, Barracks×2, Refinery×2, Reaper×2, EngineeringBay×1, BarracksTechLab×1, Marine×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 11 | 30 | 250 | 0 | 8 | 28 |
| 6 | 8 | 41 | 250 | 300 | 4 | 33 |
| 8 | 2 | 63 | 50 | 1200 | 1 | 33 |
| 12 | 0 | 141 | 0 | 5400 | 0 | 33 |

**vs LoremIpsum (Z), 65.4 min, lost:** SCV×37, Marine×12, SupplyDepot×7, Barracks×3, Refinery×2, Reaper×2, KD8Charge×2, CommandCenter×1, BarracksTechLab×1, Marauder×1, EngineeringBay×1, Factory×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 32 | 38 | 300 | 625 | 26 | 28 |
| 6 | 43 | 62 | 475 | 900 | 33 | 40 |
| 8 | 65 | 92 | 1125 | 1400 | 40 | 70 |
| 12 | 64 | 162 | 1625 | 3400 | 36 | 80 |

**vs Hellcannon (P), 58.2 min, lost:** SCV×32, CommandCenter×2, SupplyDepot×2, Refinery×2, Reaper×2, Barracks×1, Bunker×1, EngineeringBay×1, BarracksTechLab×1, Marine×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 10 | 32 | 200 | 0 | 7 | 28 |
| 6 | 7 | 41 | 0 | 300 | 6 | 33 |
| 8 | 3 | 61 | 0 | 1200 | 3 | 33 |
| 12 | 0 | 151 | 0 | 5700 | 0 | 33 |

## Strengths

- Well-rounded; strong vs Zerg and in the Terran mirror.
- Reaper opening pressures economies.

## Weaknesses

- Closest matchup is Protoss (30-25) — colossus/storm out-splash its bio if it goes light.

## How to beat it

1. As Protoss, splash (colossus/storm) + immortals; defend the reaper.
2. Exploit any mech immobility with drops/multi-prong.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*