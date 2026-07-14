# Creepy_duo_canon

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **cannon-rush Protoss** (Creepy family): a two-pronged photon-cannon rush with zealot backup. It lives or dies on the rush — strong vs Terran (21-8) and Protoss (24-9) but crushed by Zerg (9-37).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1655 (top-tier ladder bot) |
| **On ladder since** | 2026-02 |
| **Last source update** | 2026-07-13 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Proxy/double photon-cannon rush with forge and zealots.

- Rush cannons into the opponent's base/natural; if it connects, it can end the game early.
- Zealots support the cannons.

## Performance (recent ladder sample)

**Overall: 58–56 (50%)** over 114 decided games (+36 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 21-8 | 72% |
| vs Protoss | 24-9 | 72% |
| vs Zerg | 9-37 | 19% |
| vs Random | 4-2 | 66% |

**Toughest opponents:** Princess-Mika-Test 0-4 (Z), muravev 0-4 (Z), EPNRoach 0-3 (Z), PolyMorph 0-3 (Z), QueenBot 0-3 (Z), SharkGull 0-3 (Z), 72Tortoises 0-3 (Z), 27turtles 0-3 (T).

**Best matchups:** GenesisLotus 4-0 (P), version_2.0 4-0 (T), Bubu 4-0 (P), clone 4-0 (T), PiG_Bot 3-0 (P), PrimordialOrigin 3-0 (P), 49Terrapins 3-0 (P), version_1.0 3-0 (T).

## Observed builds (from its own replays)

**vs 27turtles (T), 43.7 min, lost:** Probe×32, Pylon×6, Zealot×5, Gateway×2, Nexus×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 16 | 28 | 0 | 200 | 15 | 23 |
| 6 | 14 | 43 | 200 | 550 | 5 | 29 |
| 8 | 21 | 69 | 400 | 1025 | 8 | 43 |
| 12 | 22 | 149 | 200 | 3900 | 13 | 68 |

**vs Laser-Circus (P), 29.9 min, won:** Probe×17, Zealot×13, Pylon×7, PhotonCannon×5, Gateway×2, Nexus×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 9 | 300 | 0 | 16 | 7 |
| 6 | 40 | 8 | 1000 | 0 | 16 | 7 |
| 8 | 52 | 25 | 1600 | 100 | 16 | 19 |
| 12 | 74 | 38 | 2900 | 600 | 11 | 24 |

**vs WaterLeak (Z), 25.8 min, won:** Probe×22, Zealot×13, Pylon×7, PhotonCannon×5, Gateway×2, Nexus×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 24 | 300 | 275 | 16 | 16 |
| 6 | 28 | 26 | 400 | 375 | 16 | 16 |
| 8 | 30 | 24 | 500 | 200 | 16 | 16 |
| 12 | 36 | 22 | 800 | 100 | 16 | 16 |

## Strengths

- Beats bots that don't scout the rush — strong vs Terran and Protoss.
- Can win outright before macro matters.

## Weaknesses

- Hard-countered by Zerg (9-37) — fast lings kill probes/cannons and the economy is too thin to recover.
- A scouted, denied rush loses on the spot.

## How to beat it

1. Scout early (probe/pylon/cannon near your base) and kill the probe/pylon before cannons finish.
2. As Zerg, fast lings crush it; as any race, deny the rush then punish the thin economy.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*