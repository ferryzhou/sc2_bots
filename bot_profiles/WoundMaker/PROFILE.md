# WoundMaker

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **mutalisk/spire Zerg**: drone economy into fast Spire and mutalisks (with roach support). Strong record (112-36), demolishing Protoss (42-5) with muta harass.

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1932 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-05-17 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Economic Zerg into fast Lair + Spire; mutalisks for harass, roach for ground support.

- Muta harass on worker lines and anything without anti-air, dodging the main army; roaches hold the ground.
- Uses mutalisk mobility to attack the economy leg and pick off stragglers.

## Performance (recent ladder sample)

**Overall: 112–36 (75%)** over 148 decided games (+2 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 30-12 | 71% |
| vs Protoss | 42-5 | 89% |
| vs Zerg | 32-18 | 64% |
| vs Random | 8-1 | 88% |

**Toughest opponents:** Eris 0-5 (Z), Roro 0-5 (T), chito 1-3 (Z), BotTato 1-3 (T), Mulebot 1-3 (T), 12PoolBot 0-2 (Z), WaterLeak 0-2 (Z), Sharkling 1-2 (Z).

**Best matchups:** Clicadinha 5-0 (Z), Apidae 6-2 (P), JimmyBot 4-0 (R), clone 4-0 (T), MechaShark 4-0 (T), Aeolus 4-0 (P), Cyne 4-0 (P), CynEX 4-0 (P).

## Observed builds (from its own replays)

**vs Mulebot (T), 51.0 min, lost:** Drone×25, Extractor×4, Overlord×3, Hatchery×1, SpawningPool×1, Spire×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 23 | 3 | 0 | 0 | 23 | 3 |
| 6 | 21 | 3 | 0 | 0 | 21 | 3 |
| 8 | 22 | 3 | 175 | 0 | 20 | 3 |
| 12 | 72 | 5 | 2775 | 0 | 36 | 3 |

**vs Roro (T), 31.6 min, lost:** Drone×33, Extractor×4, Overlord×3, Roach×3, Hatchery×2, SpawningPool×1, RoachWarren×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 13 | 11 | 0 | 150 | 12 | 6 |
| 6 | 14 | 22 | 0 | 350 | 14 | 13 |
| 8 | 31 | 23 | 800 | 400 | 15 | 15 |
| 12 | 60 | 38 | 1700 | 400 | 31 | 27 |

**vs Roro (T), 30.5 min, lost:** Drone×87, CreepTumor×62, CreepTumorQueen×21, Overlord×14, Queen×10, Hatchery×4, Extractor×4, EvolutionChamber×2, SpawningPool×1, InfestationPit×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 54 | 37 | 700 | 300 | 37 | 28 |
| 6 | 81 | 59 | 1400 | 950 | 59 | 42 |
| 8 | 125 | 87 | 2475 | 1425 | 83 | 60 |
| 12 | 199 | 139 | 9900 | 4675 | 95 | 79 |

## Strengths

- Mutalisk harass is devastating vs bots with weak anti-air — crushes Protoss (42-5).
- Mobility + economy; hard to pin down.

## Weaknesses

- Anti-air hard-counters it: thors, turrets/spores, vikings, mass queens, phoenix.
- If the muta harass is neutralized, its ground army is relatively thin.

## How to beat it

1. Anti-air BEFORE the mutas pop (read the Spire): turrets/spores over worker lines, thors/vikings/phoenix, keep marines/queens home.
2. Then push the muta-thinned ground while the mutas are off harassing.
3. Don't chase mutas around the map with your main army.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*