# muravevtest

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A test build of **muravev** — a strong **speedling/macro Zerg** (drone + creep + ling with melee upgrades). Excellent record (89-31), crushing Terran (43-6). One of this tier's strongest.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1710 (top-tier ladder bot) |
| **On ladder since** | 2025-02 |
| **Last source update** | 2026-05-27 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Fast pool/speed into drone + creep macro; ling with queens.

- Mass speedling off a big drone economy with heavy creep and upgrades; remax fast.
- Overwhelms with ling numbers + map control (creep).

## Performance (recent ladder sample)

**Overall: 89–31 (74%)** over 120 decided games (+30 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 43-6 | 87% |
| vs Protoss | 29-8 | 78% |
| vs Zerg | 12-16 | 42% |
| vs Random | 5-1 | 83% |

**Toughest opponents:** 49Terrapins 2-5 (P), Positive_Null 1-4 (Z), Saimon 0-3 (Z), Princess-Mika 3-4 (Z), muravev 2-3 (Z), t-bone 0-1 (T), norman 0-1 (P), AresRandomExample 0-1 (R).

**Best matchups:** smokinggunbot 7-0 (T), Laser-Circus 7-0 (P), GhostProtocol 6-0 (T), PrimordialOrigin 6-0 (P), Alexa 6-0 (T), GenesisLotus 6-0 (P), Gordon 5-0 (T), DSSTL 5-0 (P).

## Observed builds (from its own replays)

**vs smokinggunbot (T), 67.0 min, won:** Drone×54, CreepTumor×16, Overlord×10, Zergling×10, CreepTumorQueen×8, Queen×6, Hatchery×4, SpawningPool×1, Extractor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 28 | 525 | 200 | 30 | 23 |
| 6 | 58 | 32 | 925 | 400 | 44 | 24 |
| 8 | 70 | 51 | 1275 | 1300 | 50 | 27 |
| 12 | 173 | 80 | 3875 | 2125 | 97 | 43 |

**vs Alexa (T), 64.9 min, won:** Drone×36, Zergling×32, Overlord×6, Hatchery×3, Queen×3, Extractor×2, SpawningPool×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 27 | 32 | 0 | 550 | 22 | 18 |
| 6 | 19 | 27 | 325 | 400 | 11 | 18 |
| 8 | 14 | 31 | 450 | 0 | 8 | 29 |
| 12 | 8 | 62 | 350 | 675 | 4 | 43 |

**vs Positive_Null (Z), 44.5 min, lost:** Drone×52, Zergling×14, CreepTumor×11, Overlord×7, Hatchery×4, Queen×3, SpawningPool×2, CreepTumorQueen×2, Extractor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 24 | 175 | 500 | 26 | 12 |
| 6 | 28 | 36 | 25 | 625 | 23 | 23 |
| 8 | 17 | 52 | 275 | 1050 | 9 | 28 |
| 12 | 6 | 127 | 0 | 4725 | 4 | 41 |

## Strengths

- Dominant vs Terran (43-6) and Protoss (29-8) in-sample — the ling flood + upgrades out-trades unprepared bio/gateway.
- Efficient economy-to-army conversion + creep control.

## Weaknesses

- Zerglings are light/melee — splash (tanks/hellions, colossus/storm, banelings) is the structural counter; weaker in the Zerg mirror (12-16).

## How to beat it

1. Splash before the flood: tanks+hellions (T), colossus/storm (P), banelings (Z).
2. Wall and hold; deny creep; keep pace on armor upgrades then punish the economy.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*