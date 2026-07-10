# Harness

Automated evaluation for the repo's ares bots (`phoenix`, `griffin`): plays
batches of headless games and keeps a persistent scoreboard. This is the
fitness function that strategy changes, parameter tuning, and automated
improvement loops plug into.

## Components

- `play_one.py` — plays a single game in this process (one SC2 instance),
  writes a JSON record: result, map, opponent, game/wall time, end-of-game
  bot stats, replay path.
- `gauntlet.py` — orchestrates N games across matchups (opponent race ×
  difficulty × random ladder map), running games in parallel subprocesses.
  Appends every record to `results/history.jsonl` (committed, so results
  survive ephemeral dev environments) and prints per-matchup winrates.
- `versus.py` — runs a repo bot against downloaded AI Arena bots through
  the real ladder entrypoint (see `download_bots.py`).

All three take `--bot {phoenix,griffin}` (default `phoenix`); the scoreboard
tracks each bot separately.

## Usage

```bash
VENV=~/venv   # created by scripts/setup_env.sh

# 6 games vs CheatVision (2 per race), 2 at a time
$VENV/bin/python harness/gauntlet.py --games 6 --concurrency 2

# same gauntlet for the Terran bot
$VENV/bin/python harness/gauntlet.py --bot griffin --games 6 --concurrency 2

# harder gauntlet
$VENV/bin/python harness/gauntlet.py --games 12 \
    --difficulties CheatVision,CheatMoney,CheatInsane

# re-print the all-time scoreboard
$VENV/bin/python harness/gauntlet.py --summary-only
```

Replays land in `<bot>/replays/harness/` (gitignored). Loss replays are the
input for replay-based loss analysis (`analysis/sc2reader_analyzer.py`).

## Map pool

`map_pool.txt` lists maps verified to work with ares-sc2 on the 4.10 Linux
client (some older map-pack files crash ares' building-placement solver at
game start, spawn-dependently). The gauntlet defaults to this pool when the
file exists; pass `--maps` to override. Re-validate after installing new map
packs by probing each map with a few short games
(`play_one.py --game-time-limit 8` — a placement crash shows up as an
instant Defeat with `game_time` 0).

## Difficulty ladder

Built-in AI tiers, roughly in order: `VeryHard` < `CheatVision` <
`CheatMoney` < `CheatInsane`. A bot that reliably beats `CheatInsane` is
ready for a first AI Arena submission; real Elo comes from the ladder.
