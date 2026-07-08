# Harness

Automated evaluation for PhoenixBot: plays batches of headless games and
keeps a persistent scoreboard. This is the fitness function that strategy
changes, parameter tuning, and automated improvement loops plug into.

## Components

- `play_one.py` — plays a single game in this process (one SC2 instance),
  writes a JSON record: result, map, opponent, game/wall time, end-of-game
  bot stats, replay path.
- `gauntlet.py` — orchestrates N games across matchups (opponent race ×
  difficulty × random ladder map), running games in parallel subprocesses.
  Appends every record to `results/history.jsonl` (committed, so results
  survive ephemeral dev environments) and prints per-matchup winrates.

## Usage

```bash
VENV=~/venv   # created by scripts/setup_env.sh

# 6 games vs CheatVision (2 per race), 2 at a time
$VENV/bin/python harness/gauntlet.py --games 6 --concurrency 2

# harder gauntlet
$VENV/bin/python harness/gauntlet.py --games 12 \
    --difficulties CheatVision,CheatMoney,CheatInsane

# re-print the all-time scoreboard
$VENV/bin/python harness/gauntlet.py --summary-only
```

Replays land in `phoenix/replays/harness/` (gitignored). Loss replays are the
input for replay-based loss analysis (`analysis/sc2reader_analyzer.py`).

## Difficulty ladder

Built-in AI tiers, roughly in order: `VeryHard` < `CheatVision` <
`CheatMoney` < `CheatInsane`. A bot that reliably beats `CheatInsane` is
ready for a first AI Arena submission; real Elo comes from the ladder.
