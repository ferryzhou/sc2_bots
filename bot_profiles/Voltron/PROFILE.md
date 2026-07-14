# Voltron

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Terran bio-tank** bot (marine/marauder + tank + medivac + starport). Struggling recently (36-71).

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~1661 (top-tier ladder bot) |
| **On ladder since** | 2026-06 |
| **Last source update** | 2026-06-22 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Bio into siege tanks + starport (medivac/support); positional Terran.

- Marine/tank/medivac — a splash-supported bio that trades positionally.

## Performance (recent ladder sample)

**Overall: 36–71 (33%)** over 107 decided games (+43 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 6-18 | 25% |
| vs Protoss | 21-22 | 48% |
| vs Zerg | 9-24 | 27% |
| vs Random | 0-7 | 0% |

**Toughest opponents:** Alexa 0-3 (T), Hestia 0-3 (T), MY_SCRIPTING_SON 0-2 (Z), Chance 0-2 (R), Lighter 0-2 (P), NecroBot 0-2 (Z), muravevTerran 0-2 (T), SiriusBot 0-2 (R).

**Best matchups:** Leviabyss 3-0 (Z), PrimordialOrigin 3-0 (P), DownedStar1 2-0 (T), CodeX001 2-0 (P), CryptBotRevival 2-0 (P), Starlight 2-0 (P), TheCatSC2Bot 2-0 (P), DoopyBot 2-0 (Z).

## Observed builds (from its own replays)

**vs Myztery (Z), 75.2 min, won:** SCV×47, Marine×11, SupplyDepot×9, Barracks×4, Refinery×4, CommandCenter×3, Marauder×3, Starport×2, Medivac×2, SiegeTank×2, Reaper×1, Factory×1, BarracksTechLab×1, FactoryTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 36 | 275 | 350 | 25 | 29 |
| 6 | 66 | 64 | 1375 | 675 | 39 | 46 |
| 8 | 98 | 90 | 3025 | 1325 | 50 | 68 |
| 12 | 176 | 16 | 6025 | 525 | 76 | 6 |

**vs Creepy_macro (Z), 66.7 min, lost:** SCV×49, Marine×10, SupplyDepot×9, Refinery×5, CommandCenter×4, Barracks×2, Marauder×2, Starport×2, SiegeTank×2, Medivac×2, Reaper×1, Factory×1, BarracksTechLab×1, FactoryTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 36 | 325 | 350 | 27 | 30 |
| 6 | 63 | 58 | 1075 | 1175 | 41 | 40 |
| 8 | 96 | 104 | 2325 | 2750 | 54 | 62 |
| 12 | 144 | 196 | 3025 | 6650 | 84 | 76 |

**vs CryptBotRevival (P), 66.7 min, won:** SCV×47, SupplyDepot×9, Marine×9, Barracks×4, Refinery×4, Marauder×3, CommandCenter×2, Starport×2, SiegeTank×2, Medivac×2, Reaper×1, EngineeringBay×1, Factory×1, BarracksTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 36 | 275 | 675 | 28 | 23 |
| 6 | 63 | 48 | 1000 | 1025 | 39 | 30 |
| 8 | 97 | 67 | 2275 | 1550 | 53 | 43 |
| 12 | 187 | 60 | 6750 | 175 | 78 | 54 |

## Strengths

- Best vs Zerg (9-24 is poor though) — actually most competitive vs Protoss (21-22) in-sample; tanks give splash.

## Weaknesses

- Losing form; weak vs Zerg (9-24) and Terran (6-18) and Random (0-7).

## How to beat it

1. Exploit tank immobility (drops, flanks, air); out-macro it.
2. As Zerg, mass + flanks overwhelm; as Terran, out-tank and out-position.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*