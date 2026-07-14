# Eris

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A top-tier **macro Zerg** and one of the ladder's most established bots. Drones hard, spreads creep, and converts a big economy into roach/ling/hydra waves with fast remax. (Closed source — build not directly captured in this sample; characterization from record + reputation.)

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Bot type** | python |
| **AI Arena Elo** | ~2283 (top-tier ladder bot) |
| **On ladder since** | 2021-02 |
| **Last source update** | 2026-07-13 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Hatch-first economic Zerg opening into a roach/ling macro game.

- Economy-first: heavy drone count, many hatcheries, creep spread for vision and speed.
- Converts economy into roach/hydra/ling and remaxes quickly after fights.
- Plays the macro game and wins on economy + trade efficiency.

## Performance (recent ladder sample)

**Overall: 96–38 (71%)** over 134 decided games (+16 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 35-25 | 58% |
| vs Protoss | 19-2 | 90% |
| vs Zerg | 40-9 | 81% |
| vs Random | 2-2 | 50% |

**Toughest opponents:** Ketroc 8-13 (T), Spiny 0-2 (Z), AlienAsh 1-2 (Z), Chance 0-1 (R), MicroMachine 0-1 (T), BugFinder 0-1 (T), Crustacean 0-1 (T), MiningMachine 1-1 (T).

**Best matchups:** Jensiiibot 10-1 (T), gotest 9-0 (Z), BenBotBC 15-7 (T), ZoeDev 10-4 (Z), SF4G 6-0 (P), HarvesterZerg 4-0 (Z), LucidZJS 3-0 (Z), Paul 3-0 (Z).

## Strengths

- Crushes Protoss in the sample (19-2) and is strong in the Zerg mirror (40-9).
- Fast remax — a lost fight rarely loses it the game.
- Deep, well-tuned macro from years of iteration.

## Weaknesses

- Its weakest matchup is Terran (35-25) — siege tanks / mech / splash punish roach-ling and out-position it.
- Like most macro Zerg, vulnerable in the window before its economy pays off to a sharp timing.

## How to beat it

1. Terran: mech / bio-with-tanks and splash are the systemic answer — hold a position and let roach-ling break on siege lines.
2. Hit an economic timing before its remax comes online rather than trading endlessly into a bigger economy.
3. Deny creep spread to cut its vision and army speed.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*