# Asteria

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Stargate skytoss Protoss**: adept/stalker into Stargate air, teching to **carriers and tempests**. Air-based macro. Even form (77-65), best vs Terran (25-15).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1642 (top-tier ladder bot) |
| **On ladder since** | 2026-05 |
| **Last source update** | 2026-07-14 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway/adept into Stargate; carriers + tempests as the win condition.

- Tech to capital air (carriers/tempests) behind a gateway core; win the late game on air + range.
- Adept/stalker hold the ground while air masses.

## Performance (recent ladder sample)

**Overall: 77–65 (54%)** over 142 decided games (+8 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 25-15 | 62% |
| vs Protoss | 22-21 | 51% |
| vs Zerg | 24-23 | 51% |
| vs Random | 6-6 | 50% |

**Toughest opponents:** puck 0-4 (P), Creepy_canon 0-4 (P), oberon 0-4 (T), MindMatrix 0-4 (Z), Creepy_macro 0-3 (Z), TyrP 0-2 (P), KoB 0-2 (Z), Klakinn 0-2 (P).

**Best matchups:** Princess-Mika 6-1 (Z), Stockfish 5-0 (T), NecroBot 4-0 (Z), Hestia 4-1 (T), GenesisLotus 4-1 (P), nida 4-1 (P), PolyMorph 4-1 (Z), muravevTerran 4-1 (T).

## Observed builds (from its own replays)

**vs Creepy_macro (Z), 69.4 min, lost:** Probe×48, Pylon×8, Assimilator×4, Adept×3, Nexus×2, Gateway×2, Stargate×2, Carrier×2, CyberneticsCore×1, Zealot×1, ShieldBattery×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 39 | 40 | 350 | 525 | 29 | 30 |
| 6 | 62 | 66 | 475 | 1525 | 42 | 45 |
| 8 | 92 | 104 | 2575 | 3150 | 52 | 62 |
| 12 | 164 | 194 | 6865 | 8200 | 81 | 70 |

**vs Creepy_macro (Z), 66.4 min, lost:** Probe×48, Pylon×7, Assimilator×4, Nexus×3, Adept×3, Gateway×2, Stargate×2, Carrier×2, CyberneticsCore×1, Zealot×1, ShieldBattery×1, FleetBeacon×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 39 | 38 | 350 | 350 | 29 | 29 |
| 6 | 62 | 62 | 475 | 1325 | 42 | 43 |
| 8 | 86 | 110 | 1915 | 1875 | 54 | 75 |
| 12 | 167 | 200 | 6725 | 8650 | 85 | 72 |

**vs Voltron (T), 61.9 min, lost:** Probe×44, Pylon×8, Assimilator×4, Nexus×3

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 34 | 0 | 325 | 35 | 27 |
| 6 | 44 | 63 | 0 | 1075 | 44 | 40 |
| 8 | 44 | 96 | 0 | 2325 | 44 | 53 |
| 12 | 19 | 198 | 0 | 7050 | 18 | 84 |

## Strengths

- Carriers/tempests out-range and out-scale most ground armies; strong vs Terran (25-15).
- Air ignores ground positioning and chokes.

## Weaknesses

- Slow, gas-heavy air tech — thin during the tech window.
- Anti-air (vikings/corruptors, mass queens/mutas) hard-counters it.

## How to beat it

1. Bring anti-air (vikings/corruptors) and hit a timing before carriers/tempests mass.
2. Deny expansions so it can't afford the air; pressure the tech window.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*