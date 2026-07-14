# Phobos

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A strong **Terran bio** macro bot (marine/marauder/medivac with reaper opening and a starport). Standard, well-executed MMM into upgrades.

## Identity

| | |
|---|---|
| **Race** | Terran |
| **Bot type** | python |
| **AI Arena Elo** | ~2150 (top-tier ladder bot) |
| **On ladder since** | 2023-06 |
| **Last source update** | 2026-07-12 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Reaper-expand into 2-base bio; barracks-heavy with reactor/tech-lab, starport for medivacs.

- Bio ball with stim/shield + combat upgrades; medivacs for mobility and drops.
- Reaper opening scouts and harasses; expands on a standard timing.
- Macro-oriented — trades bio efficiently and reinforces from home.

## Performance (recent ladder sample)

**Overall: 83–64 (56%)** over 147 decided games (+3 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 20-23 | 46% |
| vs Protoss | 28-15 | 65% |
| vs Zerg | 33-20 | 62% |
| vs Random | 2-6 | 25% |

**Toughest opponents:** Ketroc 0-5 (T), Xena 1-4 (R), DominionDog 0-3 (T), QueenBot 0-3 (Z), Dovahkiin 0-3 (Z), MicroMachine 0-3 (T), SharpShadows 1-3 (P), SF4G 0-2 (P).

**Best matchups:** Apidae 5-0 (P), SaShaBot 5-0 (Z), DadBotTest 5-0 (Z), Raiden-p-bot 4-0 (P), DadBot 3-0 (Z), PhantomBot 3-0 (Z), 12PoolBot 3-0 (Z), zigster 3-0 (T).

## Observed builds (from its own replays)

**vs Deimos (P), 16.8 min, lost:** SCV×47, Marine×24, SupplyDepot×8, Marauder×7, Barracks×5, Refinery×3, CommandCenter×2, Reaper×2, BarracksTechLab×2, Starport×2, BarracksReactor×1, Factory×1, StarportTechLab×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 38 | 400 | 425 | 27 | 30 |
| 6 | 65 | 64 | 1175 | 1275 | 38 | 44 |
| 8 | 77 | 81 | 1150 | 2475 | 45 | 46 |
| 12 | 52 | 136 | 850 | 5725 | 40 | 72 |

## Strengths

- Balanced, no exploitable extreme; strong vs Zerg (33-20) and Protoss (28-15).
- Bio mobility + medivac drops apply constant pressure.

## Weaknesses

- Bio without many tanks melts to splash — colossus, storm, banelings, lurkers.
- Slightly negative vs Terran mirrors in-sample; tank-count and positioning decide those.

## How to beat it

1. Force splash-favorable fights: colossus/storm (P), banelings/lurkers (Z), more tanks (T).
2. Defend drops (turrets/keep-back units) so its medivac harass gets nothing.
3. Don't fight stimmed bio in the open — use position and defender's advantage.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*