# Clicadinha

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **macro Zerg** (the well-known Clicadinha): heavy drone economy into roach/queen with creep and spore defense. Roach-centric macro.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1716 (top-tier ladder bot) |
| **On ladder since** | 2024-04 |
| **Last source update** | 2026-07-14 |
| **Source public** | yes (Python source publicly downloadable; this profile is from replays + record) |

## Strategy

**Opening:** Economic Zerg; drone-heavy into roach warren, queens, spore/spine defense, creep spread.

- Drone hard, defend with queens/spores, remax roach — a patient macro Zerg.

## Performance (recent ladder sample)

**Overall: 58–79 (42%)** over 137 decided games (+13 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 15-34 | 30% |
| vs Protoss | 19-17 | 52% |
| vs Zerg | 16-20 | 44% |
| vs Random | 8-8 | 50% |

**Toughest opponents:** BenBotBC 0-5 (T), AKal_T 0-3 (T), sharkbot 0-3 (P), zig-spudde 0-3 (T), Roro 0-3 (T), ANIbot 0-3 (T), GPT 0-3 (T), Eris 0-3 (Z).

**Best matchups:** AresRandomExample 3-0 (R), 27turtles 3-0 (T), Deimos 3-0 (P), DadBot 2-0 (Z), 72Tortoises 2-0 (Z), zig-reapers 2-0 (T), Klakinn 2-0 (P), WickedBot 2-0 (T).

## Observed builds (from its own replays)

**vs TyrT (T), 80.4 min, won:** Drone×56, Roach×17, Overlord×12, Queen×6, Extractor×4, Hatchery×3, SporeCrawler×2, SpawningPool×1, RoachWarren×1, EvolutionChamber×1, InfestationPit×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 33 | 350 | 150 | 34 | 25 |
| 6 | 52 | 65 | 525 | 1175 | 46 | 37 |
| 8 | 107 | 82 | 3475 | 1625 | 43 | 54 |
| 12 | 153 | 8 | 6025 | 800 | 43 | 0 |

**vs ANI_dev (T), 61.9 min, won:** Drone×56, Roach×17, Overlord×12, Queen×6, Extractor×4, Hatchery×3, CreepTumorQueen×2, SpawningPool×1, RoachWarren×1, EvolutionChamber×1, InfestationPit×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 37 | 350 | 150 | 35 | 28 |
| 6 | 78 | 72 | 525 | 1250 | 46 | 42 |
| 8 | 126 | 112 | 4000 | 3850 | 46 | 45 |
| 12 | 200 | 15 | 8450 | 1500 | 46 | 1 |

**vs nida (P), 42.7 min, lost:** Zergling×94, Drone×29, Overlord×9, Queen×6, Hatchery×3, SpineCrawler×3, CreepTumorQueen×3, SpawningPool×1, Extractor×1, CreepTumor×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 28 | 42 | 500 | 800 | 21 | 25 |
| 6 | 58 | 60 | 2100 | 2325 | 22 | 25 |
| 8 | 53 | 72 | 1600 | 3500 | 22 | 26 |
| 12 | 52 | 85 | 1550 | 3450 | 22 | 38 |

## Strengths

- Strong economy; grinds long games with roach remax.

## Weaknesses

- Losing form (58-79); weak vs Terran (15-34) — tanks/mech out-range roach.
- Roach without much splash struggles vs colossus/tanks.

## How to beat it

1. Terran: tanks/mech + splash and out-range the roaches.
2. Hit a timing before its economy + remax take over; deny creep.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*