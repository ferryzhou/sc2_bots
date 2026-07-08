# PhoenixBot

Protoss bot built on [ares-sc2](https://github.com/AresSC2/ares-sc2).

## Architecture (v0)

- **Opening**: declared as data in `protoss_builds.yml`, executed by the ares
  build runner. Multiple builds per opponent race are supported, with
  winrate-based selection persisted between ladder games (`UseData: True`).
- **Macro**: once the opening completes, ares macro controllers take over —
  `AutoSupply`, `BuildWorkers`, `SpawnController`, `ProductionController`,
  `ExpansionController`, `GasBuildingController`, `UpgradeController`
  (see `bot/main.py:_macro`).
- **Army**: units get the `ATTACKING` role on creation. The bot rallies until
  it reaches an attack supply threshold, defends its bases if threatened, and
  uses ares `CombatManeuver` behaviors (stutter-step, shield-aware retreat,
  influence-grid pathing) for per-unit micro.

The strategy surface (builds yml + army comp dict + thresholds) is
deliberately data-shaped so tooling can tune or swap strategies without
code changes.

## Run locally

```bash
# one-time setup (installs venv, SC2 headless client, ladder maps)
../scripts/setup_env.sh

~/venv/bin/python run.py                                   # random map vs Zerg CheatVision
~/venv/bin/python run.py --race terran --difficulty VeryHard --map PylonAIE
```

Replays are saved to `replays/`.

## Ladder

`run.py --LadderServer ...` (AI Arena / local ladder manager) is handled by
`ladder.py`, the standard Sc2LadderServer client.
