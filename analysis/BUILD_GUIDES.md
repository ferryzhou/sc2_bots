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

## Running these builds in a bot (`--build`)

Two bots can reproduce these builds with a single flag; the paths differ because
the frameworks differ.

**AegisBot (ares-sc2, Terran)** already runs step-by-step openings from
`aegis/terran_builds.yml` in the ares build-runner DSL. `spawningtool_to_ares.py`
converts a build_guides JSON into that DSL (each of my sc2 tokens is exactly what
ares resolves; placement/morph steps use the ares keywords SUPPLY/GAS/EXPAND/
ORBITAL). The 8 Terran guides are already written into `terran_builds.yml`, so:

```
python aegis/run.py --build st_t_SpeCial_TvP_8_worker_standard_opening --race protoss
```

forces that opening via ares `switch_opening`; once the script completes the ares
macro controllers take over. Regenerate/add builds with:

```
python analysis/spawningtool_to_ares.py --write aegis/terran_builds.yml 203108 203133 ...
```

**AthenaBot (python-sc2, Protoss)** has no build runner, so `athena/buildscript.py`
wraps `BuildExecutor`: while active it issues each scripted structure / unit /
upgrade at its supply benchmark (mapping tokens to `UnitTypeId`/`UpgradeId` and
placements to Athena's wall / expansion / gas helpers), then hands off to the
adaptive managers. The defense advisor overrides it — a scouted all-in pauses the
script so the anti-rush behaviour isn't undone.

```
python athena/run.py --build 203087 --race zerg      # Harstem PvZ
```

Only same-race builds apply (AegisBot = Terran, Athena = Protoss). HydraBot is
deliberately not wired: it's declarative (profiles → dynamic planner), so its
analog is the mined `openings` families, not these exact scripts.

### Confirming reproduction (and timing fidelity)

`analysis/verify_build.py` reads a saved replay and diffs the bot's ACTUAL build
against the intended script:

```
python athena/run.py --build 203087 --race zerg --save-replay r.SC2Replay
python analysis/verify_build.py r.SC2Replay 203087 Protoss
```

It reports each step's intended vs actual **supply** (the fair fidelity measure
for a supply-triggered build — wall-clock lags with a slower economy) and time.
Measured results:

- **AthenaBot / Harstem PvZ: 20/20 steps reproduced.** The opening hits the
  script almost exactly on supply (Pylon @15 vs @12, Gateway @15 vs @14, Nexus
  @19 vs @19, Cybernetics @19 vs @19, Stargate @24 vs @24); median |Δsupply| ≈ 3.
- **AegisBot / SpeCial TvP: 28/30**, opening faithful (Depot 0:15, Barracks 0:46,
  Refinery 0:54, Factory 2:16, CC 3:33) before ares hands off to macro.

Athena's executor issues **every due, affordable, unblocked step each tick**
(parallel, budget-tracked — a slow step like the 3rd gas can't cascade-delay the
rest), fires at the earlier of the supply-or-time benchmark, and chrono-boosts
the build's chrono-flagged steps. The residual mid-game drift (e.g. Warp Gate
lands later than the pro's supply) is an **economy limit, not an executor bug**:
a gas-hungry pro build outruns an adaptive bot's gas income, so the 50-gas
research waits behind the 150-gas Stargate/Oracle. Closing that gap is a
bot-macro problem (worker/chrono/mining optimisation), not a build-order one.

## Adding more builds

```
python analysis/spawningtool_build.py 203110 203109 203690   # ids from the site
python -m strategy_engine.selftest                           # verify they load + reproduce
```

Find ids on the site's [build list](https://lotv.spawningtool.com/build/). If a
new build references a unit/upgrade not yet in the mapping, `coverage()` flags it
as unmapped — add the `name -> token` pair to `build_guides.py` (verify the token
against `UnitTypeId`/`UpgradeId` first).
