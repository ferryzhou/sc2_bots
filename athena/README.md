# AthenaBot

A modular, adaptive Protoss bot driven by the [`strategy_engine`](../strategy_engine/)
model. Simple pieces, one shared brain: each step it **perceives**, **advises**,
then **acts**.

## Architecture

```
on_step:  perception -> strategy (advisor) -> economy + production + army
```

| Module          | Responsibility |
|-----------------|----------------|
| `perception.py` | Fold visible enemy units/structures into `enemy_memory` (scout → belief) that feeds the engine. Max-ever structure counts survive fog. |
| `strategy.py`   | Build a `GameState` from the bot + memory, add Protoss reads (detection, composition vs. race), return one `Advice` from `StrategicAdvisor`. |
| `economy.py`    | Probes, supply (aggressive — no idle-from-block floating), gas, expansions, chrono. Gated by the advisor's posture/investment. |
| `production.py` | Gateway + robo core, forge upgrades, Twilight/Charge, Colossus splash vs. Zerg, and static defense when the advisor flags an all-in. |
| `army.py`       | Defend the economy first; attack or hold from the engagement read; early probe scout; observer control. |
| `main.py`       | `AthenaBot` — wires the managers and logs one advisor digest per minute. |

## How it adapts

Everything reactive flows from `strategy_engine`:
- **Opponent archetype** (`classify_opponent`) → static defense + hold vs. a
  detected all-in; expand/attack vs. greed.
- **Engagement** (`assess_engagement`) → attack when favorable, hold otherwise.
- **Investment priority** → economy vs. army emphasis and expansion timing.
- **Composition** → zealot-heavy + Colossus vs. Zerg mass-light; stalker/immortal
  otherwise (the lishimin mono-stalker failure informs this).

## Run

```bash
# local, headless (needs scripts/setup_env.sh done)
python athena/run.py --race zerg --difficulty VeryHard --map PylonAIE

# measure level over N games vs the built-in AI
python athena/measure.py --games 10

# vs a downloaded AI Arena bot (ladder path)
python harness/versus.py --bot athena --opponent 12PoolBot
```

## Status

A first working baseline: it macros, adapts, and defends, driven end-to-end by
the strategy engine. It is not yet tuned to reliably beat the strongest built-in
AI — see the measured win-rate in the PR and the tuning knobs at the top of each
manager (gateway targets, attack thresholds, worker caps).
