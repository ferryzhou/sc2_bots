# GriffinBot

Terran bot built on [ares-sc2](https://github.com/AresSC2/ares-sc2) — the
Terran counterpart of `phoenix/` (PhoenixBot), sharing its architecture.

## Architecture (v0)

- **Opening**: declared as data in `terran_builds.yml`, executed by the ares
  build runner. Multiple builds per opponent race are supported, with
  winrate-based selection persisted between ladder games (`UseData: True`).
- **Macro**: once the opening completes, ares macro controllers take over —
  `AutoSupply`, `BuildWorkers`, `SpawnController`, `ProductionController`,
  `ExpansionController`, `GasBuildingController`, `UpgradeController`
  (see `bot/main.py:_macro`). Terran plumbing on top: command centers morph
  to orbitals, orbital energy is dumped into MULEs, and supply depots
  raise/lower based on nearby enemy ground units.
- **Army**: marine/marauder/siege tank/medivac. Units get the `ATTACKING`
  role on creation. The bot rallies until it reaches an attack supply
  threshold (gated on stim + a medivac), defends its bases if threatened,
  and uses ares `CombatManeuver` behaviors (stutter-step, health-aware
  retreat, influence-grid pathing) for per-unit micro. Bio stims when
  healthy and in weapons range of real targets; tanks siege against nearby
  ground targets and unsiege to follow the army; medivacs hug the bio ball
  and rely on autocast heal. Tanks are load-bearing vs the built-in cheater
  AIs: pure-bio variants went 0-6 vs terran+protoss CheatVision across two
  timing sweeps, bio+tank went 4-2 (see `results/history_griffin.jsonl`).

The strategy surface (builds yml + army comp dict + thresholds) is
deliberately data-shaped so tooling can tune or swap strategies without
code changes.

## Run locally

```bash
# one-time setup (installs venv, SC2 headless client, ladder maps)
../scripts/setup_env.sh

~/venv/bin/python run.py                                   # random map vs Zerg CheatVision
~/venv/bin/python run.py --race protoss --difficulty VeryHard --map PylonAIE
```

Replays are saved to `replays/`.

## Ladder

`run.py --LadderServer ...` (AI Arena / local ladder manager) is handled by
`ladder.py`, the standard Sc2LadderServer client.
