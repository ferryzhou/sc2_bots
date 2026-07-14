# sharpy_protoss_test1

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **gateway + Stargate Protoss** (sharpy test line): zealot/stalker off gateways with a Stargate (void rays), forge upgrades. Strong vs Terran (26-5).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1601 (top-tier ladder bot) |
| **On ladder since** | 2026-06 |
| **Last source update** | 2026-06-30 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway zealot/stalker into Stargate (void ray) with forge upgrades.

- Gateway army + void ray air; pressure and macro with upgrades.
- Void rays add anti-armor and air flexibility.

## Performance (recent ladder sample)

**Overall: 85–60 (58%)** over 145 decided games (+5 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 26-5 | 83% |
| vs Protoss | 23-26 | 46% |
| vs Zerg | 31-24 | 56% |
| vs Random | 5-5 | 50% |

**Toughest opponents:** Crawler 0-5 (Z), Creepy_duo_canon 0-4 (P), Forgefiend 0-4 (P), Montka 1-4 (R), OneBaseStalkerBot 1-4 (P), ZEALOCALYPSE 0-3 (P), Dodo 1-3 (Z), kas 1-3 (Z).

**Best matchups:** 27turtles 5-0 (T), Persephone 5-0 (Z), Horizon 5-0 (T), Lissy 5-0 (Z), zig-reapers 5-0 (T), Hestia 3-0 (T), smokinggunbot 3-1 (T), KoB 3-1 (Z).

## Observed builds (from its own replays)

**vs Princess-Mika (Z), 32.6 min, won:** Probe×30, Zealot×9, Pylon×6, Gateway×3, Assimilator×2, Stalker×2, Nexus×1, Forge×1, CyberneticsCore×1, TwilightCouncil×1, Stargate×1, VoidRay×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 26 | 29 | 175 | 750 | 19 | 16 |
| 6 | 38 | 44 | 950 | 750 | 22 | 30 |
| 8 | 54 | 65 | 1750 | 925 | 22 | 48 |
| 12 | 58 | 74 | 2375 | 1350 | 22 | 42 |

**vs KoB (Z), 30.1 min, lost:** Probe×45, Stalker×8, Pylon×6, Zealot×6, Gateway×4, Assimilator×3, Nexus×2, Stargate×2, VoidRay×2, CyberneticsCore×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 37 | 48 | 350 | 1150 | 29 | 22 |
| 6 | 52 | 70 | 200 | 1975 | 43 | 29 |
| 8 | 35 | 76 | 800 | 2075 | 25 | 35 |
| 12 | 52 | 106 | 1950 | 2400 | 22 | 56 |

**vs PerilousProtossBot (P), 27.2 min, lost:** Probe×37, Pylon×4, Stalker×4, Gateway×3, Zealot×3, Assimilator×2, Nexus×1, Forge×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 20 | 26 | 175 | 200 | 17 | 16 |
| 6 | 28 | 30 | 175 | 400 | 21 | 21 |
| 8 | 46 | 52 | 1050 | 1000 | 22 | 30 |
| 12 | 78 | 102 | 2975 | 3400 | 22 | 55 |

## Strengths

- Strong vs Terran (26-5) — void rays + zealots punish bio/mech.
- Gateway + air flexibility with upgrades.

## Weaknesses

- Even vs Protoss (23-26); gateway army light on splash.
- Void ray tech is thin if rushed.

## How to beat it

1. Anti-air for the void rays (as T, vikings/turrets; as Z, queens/corruptors); splash the gateway units.
2. Match upgrades and force favorable fights.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*