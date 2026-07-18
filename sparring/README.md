# sparring: replay-derived opponents for local testing

Reproduce losses to a specific opponent **without its source code** by mimicking
its behavior with a scripted bot built from the opponent's own replay. Run your
bot against the sparring partner locally to test fixes.

## How it works

An all-in like a 4-gate zealot rush is almost entirely a **scripted build +
timing push**. Everything you need is in the replay:

1. **Extract the build** — `analysis/extract_build_order.py REPLAY <pid>` prints
   the opponent's structures, units, and upgrades with game-time and supply, and
   writes a `*.buildorder.json` spec.
2. **Script a mimic** — a small python-sc2 bot follows that build on a timeline:
   same buildings, same composition, same timing, same attack.

This reproduces the **build, composition, and timing** faithfully. It does *not*
reproduce the original bot's exact reactive micro — for a scripted all-in that's
~90% of the behavior, which is plenty to test your defenses against. For a
reactive macro opponent it's a good approximation, not a clone.

**Why not machine learning / behavior cloning?** It needs many replays, an
action-extraction pipeline, and a trained policy — heavy, fragile, and overkill
for a sparring partner. A scripted mimic is deterministic and reproducible, which
is exactly what you want when testing a fix.

## FourGateZealotBot

`four_gate_zealot_bot.py` mimics the 4-gate zealot all-in that beat `lishimin`
(extracted from `...ZEALOCALYPSE...SC2Replay`):

```
Nexus, Pylon @13, Pylon @15, 4x Gateway (1:35-2:01), NO gas, mass Zealot,
warp-in pylons pushed forward, ~18 probes then all-in. First Zealot ~3:18.
```

Tunables at the top of the class: `TARGET_PROBES`, `NUM_GATEWAYS`,
`ATTACK_AT_ZEALOTS`.

## Run

```bash
# verify the sparring bot opens with a 4-gate (vs a built-in AI)
python sparring/run.py
python sparring/run.py --bot massling     # mass-ling Zerg macro
python sparring/run.py --bot twelvepool   # 12-pool ling rush
```

All three validated headless vs the VeryHard built-in AI (fingerprints from
replay tracker events): fourgate 4 gates / 0 gas / 27 zealots (first 2:38,
won 5:42); twelvepool pool 0:39 on 14 drones, 44 lings (first 2:08);
massling pool 1:19, 5 hatcheries, 4 queens, 73 drones, 288 lings (won).

To reproduce *your* bot's loss, import your bot in `run.py` and put it in the
players list (there's a commented example). Requires `python-sc2` and a local
StarCraft II install.

## Mimic a different opponent

1. `python analysis/extract_build_order.py THEIR_REPLAY <pid>` (use the numeric
   player id — AI Arena replays carry no player names).
2. Copy `four_gate_zealot_bot.py` and adjust the buildings / units / timings to
   the extracted spec (e.g. a mass-ling Zerg or a stalker timing).

The extractor handles AI Arena arena-client replays (via the sc2reader shim in
`analysis/principle_analyzer.py`).
