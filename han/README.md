# Han SC2 Bot

HanBot is a rule-based Terran bot (V2.0) that plays a bio/mech macro style. It can consistently beat the built-in cheater AIs, including Protoss CheatMoney and Terran CheatVision.

## How it plays

- **Army composition:** marines and marauders backed by siege tanks, with medivacs for healing/transport and ravens for support.
- **Economy:** trains SCVs up to a target saturation, upgrades command centers to orbital commands, calls down MULEs on the richest nearby mineral fields, and expands when bases are saturated (waiting on expansion funds before spending elsewhere).
- **Production:** builds barracks, factories, starports, engineering bays, and an armory with sensible caps relative to each other, appends addons, and researches infantry weapon/armor upgrades (armory unlocks levels 2–3).
- **Scouting:** sends an early worker scout around 14 supply, then keeps 1–2 medivac/raven scouts patrolling the map as the game progresses.
- **Defense:** detects cheese (enemy units or structures near the base) in the first 3 minutes and switches to an early game defense mode; detects when a base is under attack and counter-attacks when defending with a superior force.
- **Micro:** rallies at the ramp early on, sieges/unsieges tanks based on enemy distance, targets nearby enemies with tanks, and treats offensive enemy structures as attack targets.
- **Building placement:** searches placement angles every 15 degrees and filters out positions too close to expansion locations.

## Running

Run directly against the built-in AI (edit `main()` in `han.py` to change the opponent race and difficulty):

```bash
python han.py
```

Or use `run.py`, which also supports ladder games via `--LadderServer`:

```bash
python run.py
```

## Things to improve

- [Done] ignore overlords for enemy units.
- don't build factories on base location.
- win rate in some map is too low.
- [Done] rally at ramp in the beginning.
- [Done] detect early zerg cheese.
- [Done] build more marines to attack / defend air units.

## History

[2025-02-09] Initial code based on claude.ai, originally as an ML-based bot that used a learned model to make decisions.

My prompts:

- want to write a bot to play starcraft2, and use machine learning, how to do that?
- can you use python-sc2 library instead of pysc2 lib?
- improve the bot that can keep improving the model by running many games.
- I didn't see on_step function. also didn't see how reward are used. could you fix the issues.
- AttributeError: 'SC2MLBot' object has no attribute '_build_or_load_model'. please fix the issue.

There are some importing errors and use async for main function, which needs to be fixed. otherwise mostly good.

The initial ML bot was dumb, so it was rewritten as the current rule-based bot, which has since been iterated on heavily (refactored economy/production/army management, scouting, cheese detection, and combat micro).
