# chito

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **speedling macro Zerg** (C++): mass zerglings backed by a big drone economy and creep, with melee upgrades. Excellent record (113-34), crushing Protoss (36-7) and the Zerg mirror (40-11).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~1977 (top-tier ladder bot) |
| **On ladder since** | 2026-04 |
| **Last source update** | 2026-07-05 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Fast pool + speed into a drone/ling macro; expands wide, +melee upgrades and evolution chambers.

- Mass speedling flood off a strong economy — like a stronger, better-macro'd 12PoolBot: it drones more and adds +melee/creep.
- Overwhelms with ling numbers + upgrades and remaxes fast.

## Performance (recent ladder sample)

**Overall: 113–34 (76%)** over 147 decided games (+3 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 21-13 | 61% |
| vs Protoss | 36-7 | 83% |
| vs Zerg | 40-11 | 78% |
| vs Random | 14-3 | 82% |
| vs ? | 2-0 | 100% |

**Toughest opponents:** puck 0-2 (P), DominionDog 0-2 (T), Eris 0-2 (Z), WaterLeak 0-2 (Z), BenBotBC 0-2 (T), JimmyBot 1-2 (R), BigDaddy 1-2 (T), ArtZerg 1-2 (Z).

**Best matchups:** WorkingAsIntended 3-0 (R), QueenBot 3-0 (Z), JimmyBotT 3-0 (T), Dasyatis 3-0 (P), Apidae 3-0 (P), TheLAW 3-0 (T), SharkGull 3-0 (Z), norman 3-0 (P).

## Observed builds (from its own replays)

**vs smokinggunbot (T), 48.3 min, won:** Drone×52, Zergling×38, Overlord×8, CreepTumor×6, Hatchery×3, Extractor×3, Queen×3, SpawningPool×1, CreepTumorQueen×1, EvolutionChamber×1, Changeling×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 29 | 450 | 250 | 17 | 23 |
| 6 | 51 | 38 | 600 | 675 | 39 | 27 |
| 8 | 71 | 57 | 1400 | 925 | 46 | 39 |
| 12 | 149 | 90 | 3875 | 2675 | 75 | 52 |

**vs SiriusBot (T), 45.4 min, won:** Drone×48, Zergling×48, Overlord×7, CreepTumor×6, Hatchery×3, Extractor×2, Queen×2, SpawningPool×1, CreepTumorQueen×1, EvolutionChamber×1, Changeling×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 24 | 30 | 375 | 500 | 16 | 19 |
| 6 | 46 | 39 | 400 | 700 | 37 | 24 |
| 8 | 46 | 44 | 425 | 400 | 37 | 31 |
| 12 | 60 | 66 | 1175 | 550 | 40 | 48 |

**vs whalemean (T), 36.0 min, won:** Zergling×92, Drone×16, Overlord×7, CreepTumor×6, Hatchery×2, Queen×2, SpawningPool×1, Extractor×1, CreepTumorQueen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 0 | 1050 | 0 | 12 | 0 |
| 6 | 54 | 0 | 2100 | 0 | 12 | 0 |
| 8 | 73 | 0 | 2900 | 0 | 13 | 0 |
| 12 | 111 | 0 | 4900 | 0 | 13 | 0 |

## Strengths

- Dominant vs Protoss (gateway armies get swarmed) and Zerg; very strong overall.
- Efficient economy-to-ling conversion + upgrades that compound.

## Weaknesses

- Zerglings are light/melee — splash (tanks, hellions, colossus, storm, banelings) is the structural counter; weaker vs Terran (21-13).
- A wall + defensive position neutralizes the flood at the choke.

## How to beat it

1. Get splash online before the flood: tanks + hellions (T), colossus/storm (P), banelings (Z).
2. Wall and hold — don't fight speedlings in the open; let them break on static defense.
3. Keep pace on armor upgrades so the ling trade stays bad, then punish its economy once the flood is spent.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*