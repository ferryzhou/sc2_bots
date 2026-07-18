# The first two minutes: opening build patterns of top players

What do strong players *build*, and *when*, in the opening two minutes? This is
an empirical companion to [`../STRATEGY.md`](../STRATEGY.md) (which covers
archetypes and how to read/counter them) focused narrowly on the **opening
building process** — the placement order and timing of the first structures.

**Data:** 166 **Grandmaster** 1v1 replays (332 player-openings) — 117 Protoss,
85 Terran, 130 Zerg — grown from an initial 67 via
[`spawningtool_download.py`](spawningtool_download.py) and gated to clean 1v1s
with at least one GM player (`extract_openings.eligible`, `min_league=7`; lower
it to 4 for a wider Diamond+ pool). Regenerate with:

```
python analysis/opening_analysis.py <replay_dir>          # writes opening_summary.json
```

Times are game-time `m:ss`. "Built %" is the share of players who placed that
structure inside the first 120s; the range is the interquartile (p25–p75)
placement time — a proxy for how *standardized* the timing is.

## The headline: the opening is nearly deterministic

Across every race the opening is one **standard economic build executed with
very low variance** — a single dominant skeleton per race, on tight timings:

| Race    | First supply     | First production      | First gas        | Modal order (share) |
|---------|------------------|-----------------------|------------------|---------------------|
| Protoss | Pylon **0:46** (0:44–0:47) | Gateway **1:18** (1:16–1:21) | Assimilator **1:34** (1:31–1:37) | Pylon > Gateway > Gas (79%) |
| Terran  | Depot **0:39** (0:38–0:44) | Barracks **1:15** (1:14–1:17) | Refinery **1:31** (1:26–1:32) | Depot > Rax > Refinery (79%) |
| Zerg    | (Overlord/larva) | Spawning Pool **1:33** | Extractor **0:55** (0:53–0:56) | branches (see below) |

The interquartile spreads are only a few seconds: at GM the first ~90 seconds
are essentially memorized. (In a wider Diamond+ pool the same medians hold but
the spread roughly doubles — the tight execution is specifically a top-level
trait.)

## Per-race opening skeletons

### Protoss — Pylon → Gateway → Gas (79% of openings)

```
0:46  Pylon          (100%)
1:18  Gateway        (98%)
1:34  Assimilator    (79%)
```

- Modal order **Pylon > Gateway > Assimilator** — 93 of 117 openings. Nearly all
  the rest are the same minus gas (20×, a slightly greedier/all-in line).
- **Almost no expansion inside 2:00** (2%). Protoss holds one base through the
  opening; the natural comes later (~2:30+), behind the gateway/cyber wall.
- ~16 workers, 17 supply at 2:00.

### Terran — Depot → Barracks → Refinery (79% of openings)

```
0:39  SupplyDepot    (100%)
1:15  Barracks       (94%)
1:31  Refinery       (86%)
```

- Modal order **SupplyDepot > Barracks > Refinery** — 67 of 85 openings; another
  9× stop at Depot > Barracks. The most uniform race by order.
- The start Command Center becomes an Orbital in place (not a new building);
  a true expansion inside 2:00 is rare (4%).
- ~15 workers, 16 supply at 2:00.

### Zerg — the branching race (economy vs. safety, live)

Zerg is the exception to "one skeleton." Its larva/hatch mechanic makes the
opening a genuine fork, and the data shows all the branches (see the family
table below for the full split):

```
0:55  Extractor      (65%)      the fork (modal orders):
1:33  SpawningPool   (42%)        46x  Extractor > Hatchery
1:44  Hatchery(exp)  (59%)        29x  Extractor > SpawningPool
                                  25x  Hatchery (hatch-first)
                                  20x  SpawningPool (pool-first / safer)
```

- **59% take a second base inside 2:00** (median 1:44) — Zerg is the only race
  that routinely expands in the opening, because a hatchery *is* the economy
  (more larva), not just more mining.
- **First gas is much earlier than P/T** (0:55 vs ~1:30) — the extractor is
  cheap larva/economy management (and the "extractor trick" for an extra drone),
  not a commitment to tech.
- ~16 workers, 17 supply at 2:00 — the same economic floor as the other races.

## The opening does not decide the game

Splitting winners from losers (166 GM games):

| Race    | Winner first-production | Loser first-production | Winner expand% | Loser expand% |
|---------|-------------------------|------------------------|----------------|---------------|
| Protoss | Gateway 1:18            | Gateway 1:18           | 0%             | 3%            |
| Terran  | Barracks 1:15           | Barracks 1:15          | 6%             | 0%            |
| Zerg    | Pool **1:34**           | Pool **1:12**          | 66%            | 52%           |

Two conclusions:

1. **For Protoss and Terran the opening is result-independent.** Winners and
   losers execute the same build with *identical* first-production timing — the
   game is decided *after* the opening, by execution and trades, not by which
   standard opener you pick. Consistent with the main finding in
   [`REPLAY_FINDINGS.md`](REPLAY_FINDINGS.md): trade **efficiency**, not the
   opening, is the dominant predictor of the winner.
2. **At GM, greedy Zerg wins.** Winning Zerg opened their spawning pool much
   later (1:34 vs 1:12) and expanded more (66% vs 52%): the more economic
   opening won more often. This is the economy-vs-army tension from
   [`../PRINCIPLES.md`](../PRINCIPLES.md) in the raw timings — earlier pool =
   "safer/stronger now," later pool + expand = "stronger later," and *later* won.

> This Zerg signal is **level-dependent**, which is why sample choice matters. In
> a broader Diamond+ pool (273 games) it washes out (pool 1:33 vs 1:30, equal
> expand) — greed is only reliably rewarded at the very top, where opponents are
> less likely to punish it with an early all-in. Treat it as a GM tendency, not a
> universal law; on a modest sample (n=70/60) it is also matchup-confounded.

## Opening families: there is more than one opening

The single-skeleton view above is the *most common* line; classifying every
player-opening ([`extract_openings.py`](extract_openings.py)) shows each race
has a small set of distinct families. Counts below are from the **166 GM
1v1 games (332 player-openings)**. "Expand%" is how often the family took a
natural inside the ~3:30 window.

| Family | n | Defining signal | Expand% |
|--------|---|-----------------|---------|
| `protoss_gate_expand` | 64 | natural nexus in window (wall + expand) | 100% |
| `protoss_one_base`    | 42 | no early nexus — one-base tech/pressure | 0% |
| `protoss_proxy`       | 9  | pylon/gateway placed *forward* (across map) | 22% |
| `protoss_gate_allin`  | 2  | 3+ gateways, no expand | 0% |
| `terran_rax_expand`   | 66 | natural CC in window | 100% |
| `terran_one_base`     | 11 | no early CC | 0% |
| `terran_2rax`         | 4  | 2+ barracks, no expand | 0% |
| `terran_proxy_rax`    | 4  | barracks placed forward | 25% |
| `zerg_hatch_first`    | 78 | hatch before pool (greedy) | 100% |
| `zerg_gas_first`      | 25 | extractor before pool | 100% |
| `zerg_pool_first`     | 13 | pool < 1:30, hatch after | 62% |
| `zerg_standard`       | 8  | pool ~1:35 then hatch | 100% |
| `zerg_pool_rush`      | 6  | pool < 0:45 (all-in, thin economy) | 17% |

(`protoss_forge_fast` — forge < 1:00, cannon rush / FFE — appears in the wider
Diamond+ pool but not among these GM games; the classifier still recognizes it.)

The classifier keys on the same few signals a bot can scout early: **where** the
first buildings go (main / ramp-wall / natural / forward-proxy), the **order** of
production vs. gas vs. expansion, and whether a **natural** appears. The families
map onto the archetypes in [`../STRATEGY.md`](../STRATEGY.md) at opening
resolution.

**Validation:** verifying every opening against all families of its race by
*structural* fit — build order, timing, placement, since early economy is nearly
identical across families ([`verify_openings.py`](verify_openings.py)) — the
correct family fits best for **69%** of 332 openings, and GM players fit their
family's reference bands *tighter* than Diamond+ (lower avg deviation) — they
execute the standard builds more precisely. Distinct builds separate cleanly
(`zerg_pool_rush`, `zerg_standard`, `terran_proxy_rax` all 100%); the misses are
between adjacent families that differ by a *single* decision — e.g. `rax_expand`
vs `one_base` is just whether the natural Command Center appears — which is
exactly the branch a bot resolves with one more moment of scouting.

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

For *exact, named* pro builds (full step-by-step scripts ingested from
spawningtool.com — structures, units, and upgrades with supply/time triggers)
rather than these statistical averages, see
[`BUILD_GUIDES.md`](BUILD_GUIDES.md) and `strategy_engine.build_guides`.

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
- **Execution beats opening choice — but as Zerg, lean greedy.** For Protoss and
  Terran winners and losers open identically, so there is no "winning opening" to
  chase; the payoff is hitting the timings and out-trading afterward. The one
  exception is Zerg at GM, where the more economic opening (later pool, take the
  base) won more — so absent a scouted threat, prefer hatch-first and convert the
  lead with efficiency (see [`REPLAY_FINDINGS.md`](REPLAY_FINDINGS.md)).
- **Classify the opponent's opening, then react to a *scouted* threat only.** Use
  the families to recognize a proxy / pool-rush / all-in from placement and
  timing (`classify_opening`) and shift off the standard line when you actually
  see one — not by opening defensively every game. This is the proactive-vs-
  reactive defense balance the strategy engine encodes.
