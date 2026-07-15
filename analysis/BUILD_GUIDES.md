# Reproducing published build orders

Beyond the *statistical* openings mined from replays
([`OPENING_PATTERNS.md`](OPENING_PATTERNS.md) — structure-level averages), the
community publishes *exact, named* build orders: full step-by-step scripts by
pros, e.g. [Serral's Safe Macro Opener](https://lotv.spawningtool.com/build/184161/)
or [Harstem's PvZ](https://lotv.spawningtool.com/build/203087/). This documents
how we ingest those and make a bot **reproduce** them.

## Pipeline

```
analysis/spawningtool_build.py <id> ...   # fetch + parse -> data/build_guides/<id>.json
strategy_engine/build_guides.py           # reusable library: model + executor + mapping
```

`spawningtool_build.py` fetches a build page and parses its
`<table class="build-table">` — each row is `supply | time | <span
class="Building|Unit|Upgrade">name</span> | note`. It records every step
(supply, time, action, name, count, note), infers the race/matchup, and drops
generic "Action" annotations (a chrono boost, a worker pull) that are not
buildable entities. Output is one JSON per build under
[`../strategy_engine/data/build_guides/`](../strategy_engine/data/build_guides/).

## Reproducibility: where can we actually reproduce these?

A step is *reproducible* when its human name maps to an sc2 id a bot can issue.
`strategy_engine.build_guides` holds that mapping (`NAME_TO_UNIT` →
`UnitTypeId`, `NAME_TO_UPGRADE` → `UpgradeId`) as string tokens, so the module
stays `sc2`-free; a bot resolves `getattr(UnitTypeId, token)`.

Over the 17 builds ingested so far (all nine matchups; Serral, Harstem,
SpeCial, Heromarine, PiG, Lambo, SortOf):

- **Mean 100% / median 100% of build steps reproducible; 16 of 17 builds fully
  reproducible.** Every mapped token resolves against the live sc2 enums (a bot
  can issue it).
- The lone gap is `Interference Matrix` (a Raven *ability*, not a build step).
  Generic chrono/annotation rows are tagged as notes and excluded — they were
  never build steps.

So: **yes — these builds reproduce essentially fully.** The structures, units,
and upgrades all map to issuable game actions; only free-text tactical notes
("pull 2 drones off gas", "scout the natural") stay as human context.

## Reproducing a build in a bot

```python
from strategy_engine import get_build, BuildExecutor

build = get_build(184161)                 # Serral's Safe Macro Opener (ZvX)
ex = BuildExecutor(build)                  # reproducible steps only, in order

# each step: report what we've produced -> get the next action + its target
step = ex.next_action(have={"OVERLORD": 1, "DRONE": 14})
#   -> BuildAction(action="build", name="Extractor", token="EXTRACTOR", at_supply=17)
if BuildExecutor.is_due(step, supply=17, seconds=44):
    #   bot issues: build EXTRACTOR   (getattr(UnitTypeId, step.token))
    ...
```

`next_action` walks the script in order (handling `x2` counts and repeated
structures); `is_due` gates on the step's supply/time benchmark so the bot
paces to the guide rather than racing ahead. `ScriptedBuild.coverage()` reports
the reproducible fraction; `guides_for(race=..., matchup=...)` selects a guide.

## How this complements the mined openings

| | `openings` (mined) | `build_guides` (scripted) |
|---|---|---|
| Source | many replays, statistical | one published guide, exact |
| Granularity | structures + placement zones | structures + units + upgrades |
| Timing | median + IQR bands | exact supply/time per step |
| Use | classify an opponent; a robust default opening | reproduce a specific pro build end-to-end |

The mined openings answer "what does the field do, and which family is my
opponent on"; the scripted guides answer "execute *this exact* pro build." A bot
can open on a mined family for robustness, or follow a named guide step-for-step.

## Adding more builds

```
python analysis/spawningtool_build.py 203110 203109 203690   # ids from the site
python -m strategy_engine.selftest                           # verify they load + reproduce
```

Find ids on the site's [build list](https://lotv.spawningtool.com/build/). If a
new build references a unit/upgrade not yet in the mapping, `coverage()` flags it
as unmapped — add the `name -> token` pair to `build_guides.py` (verify the token
against `UnitTypeId`/`UpgradeId` first).
