# Dodo

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **macro Zerg** with a **Nydus** twist: heavy drone economy (76 drones) into roach, using Nydus networks to reposition/attack. Losing form (50-94).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1678 (top-tier ladder bot) |
| **On ladder since** | 2022-11 |
| **Last source update** | 2026-01-03 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Very economic Zerg (drone-heavy) into roach + Nydus network.

- Over-drones into a big economy, uses Nydus to move army or drop into bases; roach-centric.

## Performance (recent ladder sample)

**Overall: 50–94 (34%)** over 144 decided games (+6 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 24-40 | 37% |
| vs Protoss | 13-23 | 36% |
| vs Zerg | 11-22 | 33% |
| vs Random | 2-9 | 18% |

**Toughest opponents:** sharkbot 1-11 (P), Ketroc 0-8 (T), Xena 1-8 (R), Eris 0-6 (Z), Zoe 0-6 (Z), DominionDog 0-5 (T), SmoothBrain 1-5 (T), EvilZoe 0-4 (Z).

**Best matchups:** Sharkling 4-0 (Z), spudde 4-0 (T), TyrT 5-2 (T), ANIbot 2-0 (T), zigster 2-0 (T), Raiden-p-bot 2-0 (P), t-bone 2-0 (T), OctopusV3 2-0 (P).

## Observed builds (from its own replays)

**vs TyrT (T), 31.4 min, lost:** Drone×76, Overlord×10, Roach×7, Queen×5, Hatchery×4, Extractor×4, SpawningPool×1, RoachWarren×1, NydusNetwork×1, NydusCanal×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 35 | 175 | 250 | 32 | 25 |
| 6 | 74 | 55 | 1025 | 1350 | 45 | 29 |
| 8 | 127 | 80 | 2600 | 2550 | 66 | 36 |
| 12 | 141 | 133 | 3000 | 4425 | 66 | 59 |

**vs LordSuperKing (P), 26.5 min, lost:** Drone×59, Overlord×9, Roach×7, Queen×5, Extractor×4, Zergling×4, Hatchery×3, SpawningPool×1, RoachWarren×1, NydusNetwork×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 37 | 650 | 375 | 25 | 26 |
| 6 | 68 | 56 | 1500 | 1600 | 42 | 33 |
| 8 | 90 | 78 | 1500 | 3000 | 47 | 41 |
| 12 | 152 | 104 | 4625 | 3900 | 62 | 57 |

**vs sharkbot (P), 26.5 min, lost:** Drone×61, Overlord×8, Roach×6, Extractor×4, Hatchery×3, Queen×3, Zergling×2, SporeCrawler×2, SpawningPool×1, RoachWarren×1, SpineCrawler×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 40 | 37 | 975 | 250 | 20 | 27 |
| 6 | 58 | 59 | 1150 | 1425 | 37 | 40 |
| 8 | 84 | 84 | 1350 | 2800 | 59 | 51 |
| 12 | 164 | 135 | 5075 | 5800 | 66 | 79 |

## Strengths

- Huge economy potential; Nydus enables surprise attacks/defense.

## Weaknesses

- Over-drones with a thin army — a wide vulnerability window; weak vs Terran (24-40) and Protoss (13-23).
- Nydus is all-or-nothing; a killed Nydus wastes the investment.

## How to beat it

1. Punish the over-drone window with a timing before its army/Nydus is ready.
2. Keep vision for Nydus exits (kill the worm on sight); splash the roach.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*