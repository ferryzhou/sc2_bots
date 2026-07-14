# who

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **Random cheese/all-in specialist** (open source). It carries a big library of aggressive openings across all three races — worker rushes, proxy marine/marauder/reaper, thor drops — plus race-specific macro builds. Unpredictable and punishing.

## Identity

| | |
|---|---|
| **Race** | Random |
| **Bot type** | python |
| **AI Arena Elo** | ~2033 (top-tier ladder bot) |
| **On ladder since** | 2026-02 |
| **Last source update** | 2026-07-03 |
| **Source public** | yes — Python source read directly for this profile |

## Strategy

**Opening:** Varies wildly: worker rush, proxy 2-rax marauder/marine, proxy reaper with planetary, thor drop, or a standard race build — chosen per game.

- Race is random AND the opening is often an all-in/proxy — double unpredictability (its `openings/` folder includes worker_rush, proxy_marauder, proxy_marine, proxy_reaper_with_pf, thor_drop).
- Dedicated combat modules for reaper harass, mine drops, cyclone, and battlecruisers if it reaches a macro game.
- Bets on ending the game early before the opponent stabilizes.

## Performance (recent ladder sample)

**Overall: 81–38 (68%)** over 119 decided games (+31 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 22-12 | 64% |
| vs Protoss | 28-9 | 75% |
| vs Zerg | 27-13 | 67% |
| vs Random | 4-4 | 50% |

**Toughest opponents:** Roro 0-3 (T), Eris 1-3 (Z), ArgoBot 0-2 (P), Dodo 0-2 (Z), KerrigansTorment 0-2 (Z), WaterLeak 0-2 (Z), BenBotBC 2-3 (T), LunaxVRR 1-2 (P).

**Best matchups:** Aeolus 3-0 (P), Sharkling 3-0 (Z), Mulebot 3-0 (T), PhantomTest 3-0 (Z), norman 3-0 (P), TyrT 3-0 (T), SpeedlingBot 3-0 (Z), SharpenedEdge 3-1 (P).

## Observed builds (from its own replays)

**vs norman (P), 43.5 min, won:** Drone×42, Mutalisk×11, Overlord×7, Extractor×4, Hatchery×2, SpawningPool×1, Spire×1, SpineCrawler×1, Queen×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 31 | 42 | 175 | 800 | 19 | 25 |
| 6 | 46 | 59 | 1375 | 2350 | 26 | 26 |
| 8 | 61 | 76 | 2175 | 3275 | 38 | 28 |
| 12 | 111 | 130 | 4375 | 4625 | 59 | 58 |

**vs HelioShard (P), 41.8 min, won:** Probe×16, Zealot×9, Nexus×2, Pylon×2, Gateway×2

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 34 | 29 | 900 | 0 | 16 | 25 |
| 6 | 34 | 27 | 900 | 0 | 16 | 23 |
| 8 | 34 | 34 | 900 | 0 | 16 | 30 |
| 12 | 34 | 33 | 900 | 125 | 16 | 29 |

**vs PhantomBot (Z), 30.5 min, won:** SCV×27, WidowMine×18, SupplyDepot×10, KD8Charge×7, Medivac×3, CommandCenter×2, Refinery×2, Factory×2, Barracks×1, Reaper×1, BarracksReactor×1, Armory×1, Starport×1, FactoryTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 33 | 41 | 500 | 775 | 23 | 28 |
| 6 | 60 | 51 | 1800 | 1000 | 24 | 34 |
| 8 | 82 | 49 | 2700 | 750 | 29 | 35 |
| 12 | 121 | 65 | 3850 | 1600 | 45 | 39 |

## Strengths

- Extremely hard to prepare for — random race + proxy/all-in library.
- Punishes greedy or slow openings hard (strong 81-38 sample).

## Weaknesses

- Most of its openings are all-ins — if the cheese is scouted and held, it has little economy to fall back on.
- A prepared, safe defender beats it consistently.

## How to beat it

1. Scout early and everywhere (worker-rush/proxy tells: missing workers, buildings near your base).
2. Wall, pull workers, add static defense, and simply survive the all-in — its economy is spent once it's held.
3. Then punish: a held cheese leaves it far behind.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*