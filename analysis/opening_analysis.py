"""What do top players build in the first two minutes?

Batch-reads a directory of ladder replays and, for EACH player, extracts the
opening building sequence and key economic markers inside the first 120 seconds
of game time. Aggregates by race to surface the common patterns:

  - the modal order in which the opening structures go down,
  - the typical (median + interquartile) timing of each key building,
  - first-gas and first-expansion timing, and worker/supply count at 2:00.

    python analysis/opening_analysis.py [REPLAY_DIR] [--window SECONDS]

Writes a machine-readable summary next to the findings doc. Requires sc2reader
(imports the arena shim from principle_analyzer for robustness).
"""
import sys
import glob
import json
import os
from collections import Counter, defaultdict
from statistics import median

import principle_analyzer as pa  # applies the sc2reader arena shim on import
import sc2reader
from extract_openings import eligible  # clean-1v1 quality gate (shared)

WINDOW = 120  # seconds of game time to consider "the opening"

# Structures worth tracking in an opening, per race.
STRUCTURES = {
    # Protoss
    "Pylon", "Gateway", "WarpGate", "Nexus", "Assimilator", "Forge",
    "CyberneticsCore", "PhotonCannon", "ShieldBattery", "RoboticsFacility",
    "Stargate", "TwilightCouncil",
    # Terran
    "SupplyDepot", "Barracks", "Refinery", "CommandCenter", "OrbitalCommand",
    "Factory", "Bunker", "EngineeringBay",
    # Zerg
    "Hatchery", "SpawningPool", "Extractor", "SpawningTool", "RoachWarren",
    "BanelingNest", "EvolutionChamber", "SpineCrawler", "Lair",
}
WORKERS = {"Probe", "SCV", "Drone"}
# sc2reader names a unit by its FINAL type, so a Gateway that later morphed to a
# WarpGate reads "WarpGate" from birth, a Hatchery that became a Lair reads
# "Lair", etc. Normalize morphs back to the base building for build-order
# identity. (Morphs fire only a Born event in place -- no Init -- so a Nexus/CC/
# Hatchery Init event is always a brand-new expansion, never an in-place morph.)
NORMALIZE = {
    "WarpGate": "Gateway",
    "OrbitalCommand": "CommandCenter", "PlanetaryFortress": "CommandCenter",
    "Lair": "Hatchery", "Hive": "Hatchery",
    "SupplyDepotLowered": "SupplyDepot",
}


def norm(name):
    return NORMALIZE.get(name, name)


# The "expansion" townhall (2nd base) per race -- a repeat of the start townhall.
TOWNHALL = {"Protoss": "Nexus", "Terran": "CommandCenter", "Zerg": "Hatchery"}
GAS = {"Assimilator", "Refinery", "Extractor"}
FIRST_PRODUCTION = {"Protoss": "Gateway", "Terran": "Barracks", "Zerg": "SpawningPool"}


def mmss(sec):
    return f"{int(sec)//60}:{int(sec) % 60:02d}"


def opening_of(r, pid, race, window):
    """Return the opening structures (<= window s) and economic markers."""
    stats = sorted((e for e in r.tracker_events
                    if e.name == "PlayerStatsEvent" and e.pid == pid),
                   key=lambda e: e.second)

    def stat_at(sec, field, default=0):
        val = default
        for e in stats:
            if e.second <= sec:
                val = getattr(e, field)
            else:
                break
        return val

    # Build order = the structures the player PLACES (UnitInitEvent), by
    # placement time and normalized to base identity. The starting main base is
    # not an Init (it exists at frame 0) -- seed it separately at 0:00.
    placements = []   # (second, normalized_name)
    born_workers = 0
    for e in r.tracker_events:
        cpid = getattr(e, "control_pid", None) or getattr(e, "pid", None)
        if cpid != pid:
            continue
        name = getattr(getattr(e, "unit", None), "name", None)
        base = norm(name) if name else None
        if e.name == "UnitInitEvent" and base in STRUCTURES and e.second <= window:
            placements.append((e.second, base))
        elif e.name == "UnitBornEvent" and name in WORKERS and e.second <= window:
            born_workers += 1

    placements.sort()
    first_of = {}
    for t, n in placements:
        first_of.setdefault(n, t)

    th = TOWNHALL.get(race)
    gas_t = min((t for t, n in placements if n in GAS), default=None)
    # Any Init of the townhall type is a brand-new base (the start base is a
    # Born, not an Init), so the earliest such Init is the natural expansion.
    expand_t = min((t for t, n in placements if n == th), default=None)

    return dict(
        order=[n for _, n in placements],
        first_of=first_of,
        first_gas=gas_t,
        expand=expand_t,
        workers_born=born_workers,
        supply_2m=int(stat_at(window, "food_used", 12)),
    )


def quantiles(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    p25 = xs[max(0, n // 4)]
    p75 = xs[min(n - 1, (3 * n) // 4)]
    return dict(n=n, median=median(xs), p25=p25, p75=p75, min=xs[0], max=xs[-1])


def analyze(replay_dir, window):
    files = sorted(glob.glob(os.path.join(replay_dir, "*.SC2Replay")))
    by_race = defaultdict(list)      # race -> list of opening dicts
    by_race_result = defaultdict(lambda: defaultdict(list))
    n_ok = 0
    for f in files:
        try:
            r = sc2reader.load_replay(f, load_level=4)
        except Exception:
            continue
        ok, humans = eligible(r)
        if not ok:
            continue
        n_ok += 1
        for p in humans:
            race = p.play_race
            if race not in TOWNHALL:
                continue
            try:
                op = opening_of(r, p.pid, race, window)
            except Exception:
                continue
            op["result"] = getattr(p, "result", None)
            by_race[race].append(op)
            by_race_result[race][op["result"]].append(op)

    return files, n_ok, by_race


def summarize(by_race, window):
    out = {}
    for race in ("Protoss", "Terran", "Zerg"):
        ops = by_race.get(race, [])
        if not ops:
            continue
        n = len(ops)
        # per-structure: coverage (% who built it in the window) + timing
        struct_names = set()
        for op in ops:
            struct_names.update(op["first_of"])
        timing = {}
        for s in struct_names:
            times = [op["first_of"].get(s) for op in ops if s in op["first_of"]]
            q = quantiles(times)
            if q:
                timing[s] = {"pct": round(100 * len(times) / n),
                             "median": mmss(q["median"]),
                             "range": f"{mmss(q['p25'])}-{mmss(q['p75'])}",
                             "median_s": q["median"]}
        # modal opening order: the first 4 distinct structures each player laid
        seqs = Counter()
        for op in ops:
            distinct = []
            for s in op["order"]:
                if s not in distinct:
                    distinct.append(s)
                if len(distinct) >= 4:
                    break
            seqs[" > ".join(distinct)] += 1
        gas_q = quantiles([op["first_gas"] for op in ops])
        exp_q = quantiles([op["expand"] for op in ops])
        exp_pct = round(100 * sum(op["expand"] is not None for op in ops) / n)
        workers = quantiles([op["workers_born"] for op in ops])
        supply = quantiles([op["supply_2m"] for op in ops])
        out[race] = dict(
            n=n,
            timing=dict(sorted(timing.items(), key=lambda kv: kv[1]["median_s"])),
            top_orders=seqs.most_common(5),
            first_gas=(mmss(gas_q["median"]) if gas_q else None),
            first_gas_range=(f"{mmss(gas_q['p25'])}-{mmss(gas_q['p75'])}" if gas_q else None),
            expand_pct_in_window=exp_pct,
            expand_median=(mmss(exp_q["median"]) if exp_q else None),
            workers_born_by_2m=(workers["median"] if workers else None),
            supply_at_2m=(supply["median"] if supply else None),
        )
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    window = WINDOW
    if "--window" in sys.argv:
        window = int(sys.argv[sys.argv.index("--window") + 1])
    replay_dir = args[0] if args else "."

    files, n_ok, by_race = analyze(replay_dir, window)
    summary = summarize(by_race, window)

    print(f"# Opening analysis (first {window}s) -- {n_ok} replays, "
          f"{sum(len(v) for v in by_race.values())} player-openings\n")
    for race, s in summary.items():
        print(f"## {race}  (n={s['n']} openings)")
        print(f"  workers built by 2:00 (median): {s['workers_born_by_2m']}")
        print(f"  supply at 2:00 (median): {s['supply_at_2m']}")
        print(f"  first gas: {s['first_gas']}  (IQR {s['first_gas_range']})")
        print(f"  expanded within window: {s['expand_pct_in_window']}% "
              f"(median {s['expand_median']})")
        print("  building timings (built% | median | IQR):")
        for st, t in s["timing"].items():
            print(f"    {st:<16} {t['pct']:>3}% | {t['median']:>5} | {t['range']}")
        print("  most common opening orders:")
        for order, c in s["top_orders"]:
            print(f"    {c:>3}x  {order}")
        print()

    out_path = os.path.join(os.path.dirname(__file__), "opening_summary.json")
    with open(out_path, "w") as f:
        json.dump({"window": window, "n_replays": n_ok, "summary": summary}, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
