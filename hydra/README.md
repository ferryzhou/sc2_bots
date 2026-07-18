# HydraBot

An adaptive **Zerg** bot that plays five distinct strategies — from all-in
**cheese** to a late-game **turtle** — and switches between them mid-game as it
reads the opponent. Built on the repo's [`strategy_engine`](../strategy_engine/)
(the shared strategic brain) and python-sc2.

The design goal is a bot that is **generic, configurable, adaptive, and flexible**
with as little hard-coded low-level behaviour as possible: strategy is declared as
data, a planner compiles it into a concrete plan every step, and dumb executors
carry the plan out. To change how the bot plays you edit the strategy library or
the planner — not the unit-level code.

## The five strategies (cheese → turtle)

They live as declarative profiles in [`zerg_strategies.yml`](zerg_strategies.yml)
— the "strategies library". Each is tagged with a *stance* that mirrors the
`strategy_engine` opponent spectrum, so the selector can map "the counter to what
the opponent is doing" onto one of ours with no ad-hoc table.

| Profile | Stance | Idea |
|---------|--------|------|
| `LingFlood` | cheese | one-base zergling/baneling all-in; attack on a critical mass |
| `RoachTiming` | timing | two-base roach/ravager pressure into a mid-game timing |
| `MacroRoachHydra` | standard | balanced three-base roach/hydra macro (the safe default) |
| `GreedyHydraLurker` | greedy | fast-expand, drone-heavy, hydra/lurker; out-mine and punish |
| `TurtleHive` | turtle | spine/spore up, tech to Hive (lurker/ultra); survive then roll out |

## Architecture

```
on_step:  perceive → advise (strategy_engine) → select strategy →
          plan (profile + advice → ExecutionPlan) → execute (macro / tech / army)
```

| Module | Responsibility |
|--------|----------------|
| `bot/perception.py` | scout → `enemy_memory` (max-ever structures, current army) feeding the engine |
| `bot/main.py` | builds the engine's `GameState` (+ Zerg reads) and wires the loop |
| `bot/strategies.py` | `StrategyProfile` + loads the YAML library; the `Stance` spectrum |
| `bot/selector.py` | **adaptive brain**: picks a profile from the engine's counter-stance and switches mid-game (with anti-thrash guards) |
| `bot/planner.py` | **dynamic plans**: compiles `profile + advice → ExecutionPlan` every step |
| `bot/zerg_data.py` | declarative Zerg tech tree & unit roster — the *only* Zerg-specific knowledge |
| `bot/macro.py` | economy executor: larva→drones/overlords, queens + injects, gas, expansions |
| `bot/tech.py` | production executor: prerequisite structures, Lair/Hive morphs, army + morphs, upgrades, static defense — all table-driven |
| `bot/army.py` | combat executor: defend / attack / harass / hold from the plan's stance |

### How it stays generic (no ad-hoc rules)

* **Strategy is data.** The five strategies are YAML. Their army is a set of
  composition weights and tech targets, not a scripted build order.
* **The plan is recompiled every step.** `Planner` turns the current profile plus
  the live `strategy_engine` reads (opponent archetype, engagement odds, power
  timing, defense emergency, detection/anti-air needs) into a fresh
  `ExecutionPlan`. Same profile → different plan as the game changes; swap the
  profile and the plan reshapes instantly. All adaptation lives here, in one
  place.
* **Tech is resolved from a table.** `tech.py` never hard-codes "if roach build
  roach warren". It reads `zerg_data` to find a unit's prerequisites, builds them
  in dependency order, morphs Hatchery→Lair→Hive when a tier is needed, and morphs
  base units up (ling→bane, roach→ravager, hydra→lurker, corruptor→broodlord).
  Teach the bot a new unit by adding a row to the table.
* **Executors hold no strategy.** They carry out whatever plan they're handed.

### How it switches mid-game

`StrategySelector` reads `strategy_engine`'s `counter_stance` for the scouted
opponent and maps its posture onto our spectrum (defensive→turtle,
aggressive→timing, economic→greedy, standard→standard), nudged by our trade
efficiency. Guards keep it stable: a committed all-in is never abandoned, an
opening-only strategy is never *started* late, a new read must persist before it's
acted on, and a detected emergency pins us to defence immediately. So the bot can
begin on any of the five and re-choose from the same five whenever its read firms.

### Which strategy it *starts* on (pre-game opponent prior)

`on_start` calls [`opponent_intel`](../opponent_intel/) with `self.opponent_id`
(the ladder passes the opponent's stable `game_display_id` UUID; the local
harness passes the name — either works). If the opponent is one we've profiled,
it opens on the counter to their known play-style instead of the blind default —
e.g. a zealot-flood opponent → `RoachTiming` (hold), an over-drone macro bot →
`LingFlood` (punish), a skytoss bot → `MacroRoachHydra` (hydra anti-air), a
broken bot → `GreedyHydraLurker`. The mid-game selector above then refines it by
live scouting. A forced `--strategy` or an unknown opponent skips this (safe
default). See [`opponent_intel/README.md`](../opponent_intel/README.md).

## Run

```bash
# local, headless (needs scripts/setup_env.sh done)
python hydra/run.py --race terran --difficulty VeryHard --map PylonAIE

# force / lock a single strategy (for testing one point on the spectrum)
python hydra/run.py --strategy TurtleHive --lock --race zerg --difficulty Hard

# measure level over N games vs the built-in AI
python hydra/measure.py --games 10

# vs downloaded AI Arena bots, through the real ladder path
python harness/versus.py --bot hydra --opponent <name>
```

`HYDRA_STRATEGY=<name>` and `HYDRA_LOCK=1` set the starting strategy / lock it
from the environment (handy for the ladder or A/B runs).
