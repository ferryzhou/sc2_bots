# The first two minutes: opening build patterns of top players

What do strong players *build*, and *when*, in the opening two minutes? This is
an empirical companion to [`../STRATEGY.md`](../STRATEGY.md) (which covers
archetypes and how to read/counter them) focused narrowly on the **opening
building process** — the placement order and timing of the first structures.

**Data:** 273 pro/high-ladder 1v1 replays (546 player-openings) — 205 Protoss,
129 Terran, 212 Zerg — grown from an initial 67 via
[`spawningtool_download.py`](spawningtool_download.py) and gated to clean 1v1s
(two human non-AI players, Diamond+, past 2:00). Regenerate with:

```
python analysis/opening_analysis.py <replay_dir>          # writes opening_summary.json
```

Times are game-time `m:ss`. "Built %" is the share of players who placed that
structure inside the first 120s; the range is the interquartile (p25–p75)
placement time — a proxy for how *standardized* the timing is.

## The headline: the opening order is deterministic

Across every race the opening is one **standard economic build**, and the
*order* is near-universal — a single dominant skeleton per race that the large
majority are on:

| Race    | First supply     | First production      | First gas        | Modal order (share) |
|---------|------------------|-----------------------|------------------|---------------------|
| Protoss | Pylon **0:44** | Gateway **1:16** | Assimilator **1:31** | Pylon > Gateway > Gas (73%) |
| Terran  | Depot **0:39** | Barracks **1:15** | Refinery **1:27** | Depot > Rax > Refinery (73%) |
| Zerg    | (Overlord/larva) | Spawning Pool **1:33** | Extractor **0:55** | branches (see below) |

The *timing* is tightest for the pure-pro subset and spreads a little wider once
Diamond/Master ladder games are included (e.g. Protoss Gateway IQR 1:00–1:20),
but the sequence itself barely varies. The first ~90 seconds are essentially
memorized: one skeleton per race, and nearly everyone on it.

## Per-race opening skeletons

### Protoss — Pylon → Gateway → Gas (73% of openings)

```
0:44  Pylon          (100%)
1:16  Gateway        (96%)
1:31  Assimilator    (83%)
```

- Modal order **Pylon > Gateway > Assimilator** — 150 of 205 openings. The rest
  are the same minus gas (23×, a slightly greedier/all-in line) or with a Forge
  spliced in (9×, forge-fast / cannon).
- **Almost no expansion inside 2:00** (4%). Protoss holds one base through the
  opening; the natural comes later (~2:30+), behind the gateway/cyber wall.
- ~16 workers, 17 supply at 2:00.

### Terran — Depot → Barracks → Refinery (73% of openings)

```
0:39  SupplyDepot    (100%)
1:15  Barracks       (94%)
1:27  Refinery       (87%)
```

- Modal order **SupplyDepot > Barracks > Refinery** — 94 of 129 openings; another
  12× swap Barracks/Refinery. The most uniform race by order.
- The start Command Center becomes an Orbital in place (not a new building);
  a true expansion inside 2:00 is rare (5%).
- ~15 workers, 16 supply at 2:00.

### Zerg — the branching race (economy vs. safety, live)

Zerg is the exception to "one skeleton." Its larva/hatch mechanic makes the
opening a genuine fork, and the data shows all the branches (see the family
table below for the full split):

```
0:55  Extractor      (62%)      the fork:
1:33  SpawningPool   (50%)        hatch-first (greedy, expand @ ~1:42) — most common
1:42  Hatchery(exp)  (62%)        pool-first (safer) / gas-first (extractor first)
                                  pool-rush (pool < 0:45, thin economy)
```

- **62% take a second base inside 2:00** (median 1:42) — Zerg is the only race
  that routinely expands in the opening, because a hatchery *is* the economy
  (more larva), not just more mining.
- **First gas is much earlier than P/T** (0:55 vs ~1:30) — the extractor is
  cheap larva/economy management (and the "extractor trick" for an extra drone),
  not a commitment to tech.
- ~16 workers, 17 supply at 2:00 — the same economic floor as the other races.

## The opening does not decide the game

Splitting winners from losers (273 games), the openings are **statistically
identical**:

| Race    | Winner first-production | Loser first-production | Winner expand% | Loser expand% |
|---------|-------------------------|------------------------|----------------|---------------|
| Protoss | Gateway 1:16            | Gateway 1:16           | 2%             | 5%            |
| Terran  | Barracks 1:15           | Barracks 1:15          | 8%             | 0%            |
| Zerg    | Pool 1:33               | Pool 1:30              | 62%            | 61%           |

**The opening does not predict the result.** Winners and losers execute the
same build at the same times — for Protoss and Terran the first-production
timing is *identical to the second*, and for Zerg it is within three seconds
with equal expansion rates. The game is decided *after* the opening, by
execution and trades, not by which standard opener you pick — consistent with
the main finding in [`REPLAY_FINDINGS.md`](REPLAY_FINDINGS.md) that trade
**efficiency**, not the opening, is the dominant predictor of the winner.

> An earlier, smaller sample (67 games) showed a "greedy Zerg wins" signal —
> winning Zerg opening pool at 1:33 vs losers at 1:07. On 273 games that gap
> collapses to 1:33 vs 1:30 with equal expand rates: it was small-sample noise.
> Growing the study set corrected the conclusion — which is the point of
> studying more games.

## Opening families: there is more than one opening

The single-skeleton view above is the *most common* line; classifying every
player-opening ([`extract_openings.py`](extract_openings.py)) shows each race
has a small set of distinct families. Counts below are from **273 pro/high-ladder
1v1 games (546 player-openings)** — grown from the initial 67 via
[`spawningtool_download.py`](spawningtool_download.py) and gated to clean 1v1s by
`extract_openings.eligible` (two human non-AI players, Diamond+, past 2:00).
"Expand%" is how often the family took a natural inside the ~3:30 window.

| Family | n | Defining signal | Expand% |
|--------|---|-----------------|---------|
| `protoss_gate_expand` | 105 | natural nexus in window (wall + expand) | 100% |
| `protoss_one_base`    | 65  | no early nexus — one-base tech/pressure | 0% |
| `protoss_proxy`       | 27  | pylon/gateway placed *forward* (across map) | 11% |
| `protoss_forge_fast`  | 5   | forge < 1:00 (cannon rush / FFE) | 0% |
| `protoss_gate_allin`  | 3   | 3+ gateways, no expand | 0% |
| `terran_rax_expand`   | 88  | natural CC in window | 100% |
| `terran_one_base`     | 24  | no early CC | 0% |
| `terran_2rax`         | 9   | 2+ barracks, no expand | 0% |
| `terran_proxy_rax`    | 8   | barracks placed forward | 12% |
| `zerg_hatch_first`    | 127 | hatch before pool (greedy) | 100% |
| `zerg_pool_first`     | 29  | pool < 1:30, hatch after | 72% |
| `zerg_gas_first`      | 28  | extractor before pool | 100% |
| `zerg_standard`       | 16  | pool ~1:35 then hatch | 94% |
| `zerg_pool_rush`      | 12  | pool < 0:45 (all-in, thin economy) | 42% |

The classifier keys on the same few signals a bot can scout early: **where** the
first buildings go (main / ramp-wall / natural / forward-proxy), the **order** of
production vs. gas vs. expansion, and whether a **natural** appears. The families
map onto the archetypes in [`../STRATEGY.md`](../STRATEGY.md) at opening
resolution.

**Validation:** verifying every opening against all families of its race by
*structural* fit — build order, timing, placement, since early economy is nearly
identical across families ([`verify_openings.py`](verify_openings.py)) — the
correct family fits best for **70%** of 546 openings. Distinct builds separate
cleanly (`zerg_pool_rush`, `terran_2rax`, `protoss_forge_fast` all 100%); the
misses are between adjacent families that differ by a *single* decision — e.g.
`rax_expand` vs `one_base` is just whether the natural Command Center appears —
which is exactly the branch a bot resolves with one more moment of scouting.

## Reusable library: `strategy_engine.openings`

The mined openings are folded into the strategy library so any bot can reuse
them (data in [`../strategy_engine/data/openings.json`](../strategy_engine/data/openings.json)):

```python
from strategy_engine import (
    classify_opening, best_opening, OpeningExecutor, verify_opening)

# 1) CLASSIFY an opponent from scouted buildings (name, second, zone)
fam = classify_opening("Zerg", [("Hatchery", 95, "natural"),
                                ("SpawningPool", 130, "main")],
                       first_gas=105, expand_time=95)      # -> "zerg_hatch_first"

# 2) REPRODUCE: drive our own build order + placements
opening = best_opening("Protoss")            # standard gate-expand
ex = OpeningExecutor(opening)
step = ex.next_step(have={"Pylon": 1})       # -> BuildStep(Gateway, RAMP_WALL, ...)
#   the bot maps step.placement (MAIN / RAMP_WALL / NATURAL / GAS / FORWARD)
#   onto its own placement helpers, builds step.structure, repeats.

# 3) VERIFY a played opening against the reference bands (economy, units,
#    placement, positions)
devs = verify_opening(opening, telemetry)    # list[Deviation]
```

Each `Opening` carries the modal build order (as `BuildStep`s with a `Placement`
zone and reference timing), the first-gas/expand timing bands, an economy
reference (worker/supply/mineral-rate bands at 0:30–3:00), and a unit reference.
`verify_opening` reports where a played opening departs from that reference —
missing buildings, late timings, wrong placement zone, or off-band economy —
which is how a bot self-checks that it actually executed the opening it intended.

## What a bot should take from this

- **Have one standard economic opening per race and execute it on rails.** The
  first ~90 seconds are not where creativity earns anything; hitting the
  standard timings (supply ~0:40, first production ~1:15, first gas ~1:30)
  reliably is worth more than a clever variation. AthenaBot's opening should aim
  for these marks (Pylon ~0:46, Gateway ~1:18, gas ~1:33).
- **Do not diverge before ~2:00 on blind information.** Since strong players all
  look the same early, early scouting rarely reveals a committed strategy before
  the 2-minute mark; the branch point is *after* the opening. Spend the opening
  on clean macro, not on premature reactions (see
  [`../INFORMATION.md`](../INFORMATION.md)).
- **The opener you pick won't win or lose the game — executing it will.** Since
  winners and losers open identically, there is no "winning opening" to chase;
  the payoff is in hitting the timings and then out-trading afterward. Don't
  agonize over opening selection; invest the effort in clean execution and the
  post-opening game (efficiency, see [`REPLAY_FINDINGS.md`](REPLAY_FINDINGS.md)).
- **Classify the opponent's opening, then react to a *scouted* threat only.** Use
  the families to recognize a proxy / pool-rush / all-in from placement and
  timing (`classify_opening`) and shift off the standard line when you actually
  see one — not by opening defensively every game. This is the proactive-vs-
  reactive defense balance the strategy engine encodes.
