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
- **Army**: marine/marauder/siege tank/medivac, plus ghosts vs protoss.
  Units get the `ATTACKING` role on creation (a 10-supply `BASE_DEFENDER`
  home guard stays back to stop harassment). The bot stages at the natural
  with tanks pre-sieged until it reaches an attack supply threshold (gated
  on stim + a medivac + the ares combat sim predicting a winnable fight,
  with an unconditional commit at 70 supply), defends its bases if
  threatened, and uses ares `CombatManeuver` behaviors (stutter-step,
  health-aware retreat, influence-grid pathing) for per-unit micro. Bio
  stims when healthy and in weapons range; tanks siege against nearby
  ground targets; ghosts EMP the protoss deathball before engagements;
  medivacs hug the bio ball and rely on autocast heal.
  Composition results are documented in `bot/main.py` comments and
  `results/history.jsonl` — headline: pure bio went 0-6 vs
  terran+protoss CheatVision, adding tanks fixed TvT/TvZ, and adding
  EMP ghosts took TvP from 1-5 to 5-1.

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
