# The first two minutes: opening build patterns of top players

What do strong players *build*, and *when*, in the opening two minutes? This is
an empirical companion to [`../STRATEGY.md`](../STRATEGY.md) (which covers
archetypes and how to read/counter them) focused narrowly on the **opening
building process** — the placement order and timing of the first structures.

**Data:** 66 ladder replays (132 player-openings) — 47 Protoss, 25 Terran, 60
Zerg — from top players. Regenerate with:

```
python analysis/opening_analysis.py <replay_dir>          # writes opening_summary.json
```

Times are game-time `m:ss`. "Built %" is the share of players who placed that
structure inside the first 120s; the range is the interquartile (p25–p75)
placement time — a proxy for how *standardized* the timing is.

## The headline: the opening is nearly deterministic

Across every race the opening is a **standard economic build executed with very
low variance.** The interquartile spread on the key buildings is only a few
seconds:

| Race    | First supply     | First production      | First gas        |
|---------|------------------|-----------------------|------------------|
| Protoss | Pylon **0:46** (0:44–0:47) | Gateway **1:18** (1:16–1:21) | Assimilator **1:33** (1:31–1:38) |
| Terran  | Depot **0:39** (0:38–0:40) | Barracks **1:15** (1:14–1:16) | Refinery **1:31** (1:26–1:32) |
| Zerg    | (Overlord/larva) | Spawning Pool **1:12** (0:46–1:35) | Extractor **0:55** (0:52–0:55) |

The tight ranges are the point: at the top level the first ~90 seconds are
essentially memorized. There is a single dominant opening skeleton per race, and
nearly everyone is on it.

## Per-race opening skeletons

### Protoss — Pylon → Gateway → Gas (85% of openings)

```
0:46  Pylon          (98%)
1:18  Gateway        (98%)
1:33  Assimilator    (85%)
```

- Modal order **Pylon > Gateway > Assimilator** — 40 of 47 openings. The rest
  are the same minus gas (a slightly later/greedier or all-in variant).
- **No expansion inside 2:00** (0%). Protoss holds one base through the opening;
  the natural comes later (~2:30+), behind the gateway/cyber wall.
- ~16 workers, 17 supply at 2:00.

### Terran — Depot → Barracks → Refinery (92% of openings)

```
0:39  SupplyDepot    (100%)
1:15  Barracks       (96%)
1:31  Refinery       (92%)
```

- Modal order **SupplyDepot > Barracks > Refinery** — 23 of 25 openings, the
  most uniform of any race.
- The start Command Center becomes an Orbital in place (not a new building);
  a true expansion inside 2:00 is rare (4%).
- ~15 workers, 16 supply at 2:00.

### Zerg — the branching race (economy vs. safety, live)

Zerg is the exception to "one skeleton." Its larva/hatch mechanic makes the
opening a genuine fork, and the data shows all the branches:

```
0:55  Extractor      (42%)      most common orders:
1:12  SpawningPool   (38%)        22x  Hatchery (hatch-first, expand @ ~1:42)
1:42  Hatchery(exp)  (60%)        13x  Extractor > Hatchery
                                  12x  SpawningPool (pool-first / safer)
                                   9x  Extractor > SpawningPool (gas-first)
```

- **60% take a second base inside 2:00** (median 1:42) — Zerg is the only race
  that routinely expands in the opening, because a hatchery *is* the economy
  (more larva), not just more mining.
- **First gas is much earlier than P/T** (0:55 vs ~1:30) — the extractor is
  cheap larva/economy management (and the "extractor trick" for an extra drone),
  not a commitment to tech.
- ~16 workers, 17 supply at 2:00 — the same economic floor as the other races.

## The opening does not decide the game

Splitting winners from losers, the openings are **almost identical**:

| Race    | Winner first-production | Loser first-production | Winner expand% | Loser expand% |
|---------|-------------------------|------------------------|----------------|---------------|
| Protoss | Gateway 1:17            | Gateway 1:19           | 0%             | 0%            |
| Terran  | Barracks 1:15           | Barracks 1:14          | 6%             | 0%            |
| Zerg    | Pool **1:33**           | Pool **1:07**          | 66%            | 54%           |

Two conclusions:

1. **For Protoss and Terran the opening is result-independent.** Winners and
   losers execute the same build within a second or two — the game is decided
   *after* the opening, by execution and trades, not by which standard opener
   you pick. This is consistent with the main finding in
   [`REPLAY_FINDINGS.md`](REPLAY_FINDINGS.md): trade **efficiency**, not the
   opening, is the dominant predictor of the winner.
2. **The one opening-time signal is Zerg greed.** Winning Zerg opened their
   spawning pool *later* (1:33 vs 1:07) and expanded slightly more (66% vs 54%).
   The greedier, more economic opening won more often — the economy investment
   paid off, and at this level it was rarely punished. This is the
   economy-vs-army tension from [`../PRINCIPLES.md`](../PRINCIPLES.md) visible in
   the raw timings: earlier pool = "safer/stronger now," later pool + expand =
   "stronger later," and *later* won more. (Correlational and matchup-confounded
   — pool timing partly reflects the opponent — but directionally clean.)

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
- **The greedy default is defensible.** Absent a scouted threat, the slightly
  more economic opening (delay the safety building, take the base) is what won
  more in the data — but only when paired with the efficiency to convert it.
  React to a *scouted* rush by shifting off the greedy line, not by opening
  defensively every game (this is exactly the proactive-vs-reactive defense
  balance the strategy engine encodes).
