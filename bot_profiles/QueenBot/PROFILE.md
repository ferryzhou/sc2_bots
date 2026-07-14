# QueenBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **queen-massing macro Zerg** (ares-sc2, open source). True to its name, its core army composition is literally **Queens** (proportion 1.0) — backed by a hatch-first economy, heavy creep, nydus, and worker defence, teching Lair→Hive with +missile/+armor upgrades. Strong vs Terran (51-41).

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~1611 (top-tier ladder bot) |
| **On ladder since** | 2020-10 |
| **Last source update** | 2026-03-06 |
| **Source public** | yes — Python source read directly for this profile |

## Strategy

**Opening:** Hatch-first economic open (from `zerg_builds.yml`): 12 drone, overlord scout to the enemy natural, 15 expand, gas, Spawning Pool ~13, then Queens in pairs — economy and queen count first, not early army.

- Masses **Queens** as the main army (transfuse, anti-air, and creep spread) — an unusual queen-centric composition, with ling/roach support.
- Hatch-first macro: drones to ~70 workers (min(70, bases×22)), constant creep tumors, and dedicated nydus + worker-defence managers.
- Teches Lair once it has 7+ queens, then Hive at ~170 supply; researches +missile/+armor 1/2/3 and overlord speed.
- Defensive and economy-first — leans on queens + creep + static defence to reach a strong upgraded late game.

## Performance (recent ladder sample)

**Overall: 76–61 (55%)** over 137 decided games (+13 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 51-41 | 55% |
| vs Protoss | 15-8 | 65% |
| vs Zerg | 9-7 | 56% |
| vs Random | 1-5 | 16% |

**Toughest opponents:** ANI_dev 2-8 (T), TestBot 0-6 (T), MicroMachine 0-2 (T), Chance 0-2 (R), TheGoldenArmada 0-2 (P), BenBotv3 0-1 (T), Fidolina 0-1 (T), Ketroc 0-1 (T).

**Best matchups:** BenBotBC 34-14 (T), Chaosbot 12-5 (T), MavBot 5-1 (P), Excess1972 5-2 (Z), Noobgam2 3-0 (P), BraxBot 2-0 (P), Paul 1-0 (Z), NewBy 1-0 (T).

## Strengths

- Strong defensive economy; good vs Terran (51-41) and Protoss (15-8).
- Queens give transfuse sustain, anti-air, and free creep/vision — hard to harass or all-in.
- Reaches a fully-upgraded Hive army if the game goes long.

## Weaknesses

- Queens are slow and can't chase — it cedes map control and is passive; a greedy opponent can out-expand it.
- The queen-heavy army lacks hard splash and hitting power — a maxed splashy/upgraded army out-values it late.
- Weak in the Zerg mirror-ish aggression window before creep/queens set up.

## How to beat it

1. Take the map and out-expand it — it turtles on creep and won't punish greed.
2. Out-range and out-splash the queen/roach army (tanks/colossus/tempest); don't melee into creep + transfuse.
3. Deny creep spread to cut its vision and queen mobility.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*