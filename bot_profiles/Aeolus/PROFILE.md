# Aeolus

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **stalker-based macro Protoss** that teches through Twilight Council (blink) into a gateway deathball. Even-ish across matchups.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | cpplinux |
| **AI Arena Elo** | ~1774 (top-tier ladder bot) |
| **On ladder since** | 2024-12 |
| **Last source update** | 2026-07-02 |
| **Source public** | yes (compiled/binary zip publicly downloadable; this profile is from replays + record) |

## Strategy

**Opening:** Gateway expand into cyber; stalker-heavy army (16+ stalkers) with Twilight Council (blink), forge upgrades.

- Stalker/blink core with upgrades; kite and out-position with blink.
- Macro-oriented — expands and grinds with a mobile stalker army.

## Performance (recent ladder sample)

**Overall: 63–78 (44%)** over 141 decided games (+9 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 28-28 | 50% |
| vs Protoss | 17-19 | 47% |
| vs Zerg | 13-15 | 46% |
| vs Random | 5-16 | 23% |

**Toughest opponents:** ANIbot 0-7 (T), changeling 1-7 (R), BenBotBC 0-6 (T), Deimos 0-6 (P), 12PoolBot 1-6 (Z), negativeZero 0-5 (P), Phobos 1-5 (T), Roro 2-5 (T).

**Best matchups:** GPT 8-1 (T), Mulebot 5-1 (T), theBigBot 6-3 (P), TyrT 4-1 (T), norman 4-1 (P), buckshot 4-1 (P), clone 3-0 (T), Clicadinha 3-1 (Z).

## Observed builds (from its own replays)

**vs Roro (T), 43.7 min, won:** Probe×48, Stalker×16, Gateway×5, Pylon×4, Nexus×3, Assimilator×2, CyberneticsCore×1, Forge×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 29 | 525 | 0 | 24 | 24 |
| 6 | 45 | 49 | 525 | 1050 | 36 | 31 |
| 8 | 54 | 71 | 350 | 1900 | 45 | 41 |
| 12 | 110 | 124 | 2275 | 3000 | 78 | 76 |

**vs ANIbot (T), 29.7 min, lost:** Probe×50, Stalker×11, Pylon×7, Assimilator×4, Nexus×3, VoidRay×3, Gateway×2, CyberneticsCore×1, Stargate×1, ShieldBattery×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 41 | 33 | 750 | 200 | 31 | 26 |
| 6 | 65 | 50 | 1450 | 1025 | 45 | 32 |
| 8 | 84 | 68 | 1625 | 2300 | 55 | 43 |
| 12 | 148 | 99 | 3075 | 3200 | 96 | 54 |

**vs Roro (T), 27.4 min, lost:** Probe×50, Stalker×12, Pylon×8, Assimilator×4, Immortal×4, Nexus×3, Gateway×3, CyberneticsCore×1, RoboticsFacility×1, Forge×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 47 | 37 | 875 | 300 | 33 | 28 |
| 6 | 71 | 57 | 1575 | 1125 | 46 | 39 |
| 8 | 92 | 80 | 2275 | 1175 | 59 | 55 |
| 12 | 144 | 132 | 3850 | 3975 | 96 | 75 |

## Strengths

- Blink stalkers are mobile and kite well; even vs Terran (28-28).

## Weaknesses

- Stalker-heavy armies lack splash — mass light and heavy air/splash trouble it; weak vs Random (5-16).
- Losing overall form (63-78).

## How to beat it

1. Bring splash and mass (banelings/lings, storm/colossus, tanks) — stalker-only folds to it.
2. Match blink micro or force fights where blink doesn't help (into a wall).

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*