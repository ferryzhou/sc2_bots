# OmegaZ

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Zerg ling-flood** bot currently in a broken/losing state (0-22 in the sample) — mass zerglings that aren't converting. Not a current threat.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1600 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-05-05 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Fast pool into mass zergling (40+) with spines — a ling flood that is currently failing.

- Zergling aggression that isn't working in its current form.

## Performance (recent ladder sample)

**Overall: 0–22 (0%)** over 22 decided games (+8 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 0-12 | 0% |
| vs Protoss | 0-3 | 0% |
| vs Zerg | 0-7 | 0% |

**Toughest opponents:** DownedStar1 0-7 (T), Princess-Mika 0-7 (Z), Mulebot 0-5 (T), Cyne 0-2 (P), sharkbot 0-1 (P).

## Observed builds (from its own replays)

**vs DownedStar1 (T), 30.6 min, lost:** Zergling×44, Drone×39, Overlord×6, Extractor×4, Hatchery×2, SpineCrawler×2, Queen×2, EvolutionChamber×2, SpawningPool×1, RoachWarren×1, CreepTumorQueen×1, CreepTumor×1, Roach×1, SporeCrawler×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 29 | 28 | 400 | 275 | 19 | 22 |
| 6 | 42 | 42 | 1075 | 725 | 20 | 22 |
| 8 | 50 | 55 | 1375 | 1650 | 22 | 22 |
| 12 | 56 | 82 | 950 | 3250 | 34 | 26 |

**vs DownedStar1 (T), 25.2 min, lost:** Drone×30, Zergling×16, Overlord×4, Extractor×4, Hatchery×2, SpineCrawler×2, SpawningPool×1, RoachWarren×1, SporeCrawler×1, EvolutionChamber×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 14 | 28 | 125 | 250 | 11 | 22 |
| 6 | 18 | 44 | 275 | 1000 | 11 | 22 |
| 8 | 22 | 54 | 350 | 1950 | 12 | 22 |
| 12 | 9 | 86 | 400 | 2900 | 1 | 36 |

**vs DownedStar1 (T), 24.9 min, lost:** Drone×26, Overlord×4, Hatchery×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 16 | 30 | 0 | 400 | 16 | 22 |
| 6 | 16 | 44 | 0 | 1375 | 16 | 22 |
| 8 | 15 | 55 | 0 | 1925 | 13 | 22 |
| 12 | 18 | 92 | 175 | 3350 | 16 | 40 |

## Strengths

- None reliable — losing every matchup in the sample.

## Weaknesses

- 0-22; the ling flood is being held and punished across the board.

## How to beat it

1. Wall + splash and hold; it hands over the game once the flood breaks.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*