"""Extract, classify, and aggregate reproducible openings from replays.

Turns a directory of replays into a library of canonical openings that a bot can
*reproduce* and later *verify* against. For each player-opening (first N seconds)
it captures:

  - the build order: (time, structure, placement-zone) using Init events,
  - placement/positions: each building's distance from the main and the natural,
    bucketed into a zone (main / ramp-wall / natural / forward-proxy / gas),
  - economy: worker count, supply, and mineral collection rate at 30s marks,
  - units: first-seen time and total count of each non-worker unit.

It then classifies each opening into a race-specific FAMILY (rule-based) and
aggregates per family into a canonical spec (modal build order, median timings,
modal placement zone per building, and economy/unit reference bands) written to
``strategy_engine/data/openings.json`` -- the data the reusable
``strategy_engine.openings`` library loads.

    python analysis/extract_openings.py <replay_dir> [--window 150]
"""
import sys
import glob
import json
import os
from collections import Counter, defaultdict
from math import hypot
from statistics import median

import principle_analyzer as pa  # sc2reader arena shim
import sc2reader

WINDOW = 210  # through the first expansion/tech commitment (~3:30) -- the
              # natural nexus/CC/hatch is a *defining* feature of an opening, and
              # it often lands after 2:00, so the window must reach it.

STRUCTURES = {
    "Pylon", "Gateway", "WarpGate", "Nexus", "Assimilator", "Forge",
    "CyberneticsCore", "PhotonCannon", "ShieldBattery", "RoboticsFacility",
    "Stargate", "TwilightCouncil", "DarkShrine",
    "SupplyDepot", "SupplyDepotLowered", "Barracks", "Refinery", "CommandCenter",
    "OrbitalCommand", "Factory", "Bunker", "EngineeringBay", "Starport",
    "Hatchery", "SpawningPool", "Extractor", "RoachWarren", "BanelingNest",
    "EvolutionChamber", "SpineCrawler", "Lair", "HydraliskDen",
}
NORMALIZE = {
    "WarpGate": "Gateway", "OrbitalCommand": "CommandCenter",
    "PlanetaryFortress": "CommandCenter", "Lair": "Hatchery", "Hive": "Hatchery",
    "SupplyDepotLowered": "SupplyDepot",
}
WORKERS = {"Probe", "SCV", "Drone"}
TOWNHALLS = {"Nexus", "CommandCenter", "Hatchery"}
GAS = {"Assimilator", "Refinery", "Extractor"}
NONARMY = WORKERS | {"Overlord", "Larva", "Egg", "Broodling", "MULE",
                     "Interceptor", "AutoTurret"}
RACE_TH = {"Protoss": "Nexus", "Terran": "CommandCenter", "Zerg": "Hatchery"}
FIRST_PROD = {"Protoss": "Gateway", "Terran": "Barracks", "Zerg": "SpawningPool"}
MARKS = (30, 60, 90, 120, 150, 180)


def norm(n):
    return NORMALIZE.get(n, n)


def mmss(sec):
    return f"{int(sec)//60}:{int(sec) % 60:02d}"


def zone_of(dist_main, dist_nat, is_gas):
    # Rough map scale: main->ramp ~15-25, main->natural ~30-40, main->enemy ~120+.
    if is_gas:
        return "gas"
    if dist_nat is not None and dist_nat <= 12 and (dist_main is None or dist_main > 14):
        return "natural"
    if dist_main is None or dist_main <= 14:
        return "main"           # in the main mineral line / core
    if dist_main <= 30:
        return "ramp_wall"      # main perimeter / ramp -- Protoss/Terran walls
    if dist_main >= 55:
        return "forward"        # proxy / aggressive placement across the map
    return "outer"              # natural/third staging area (30-55 out)


def extract_player(r, pid, race, window):
    stats = sorted((e for e in r.tracker_events
                    if e.name == "PlayerStatsEvent" and e.pid == pid),
                   key=lambda e: e.second)

    def stat_at(sec, field, default=0):
        val = default
        for e in stats:
            if e.second <= sec:
                val = getattr(e, field, default)
            else:
                break
        return val

    # main base position: the townhall present at frame 0
    main = None
    for e in r.tracker_events:
        cp = getattr(e, "control_pid", None) or getattr(e, "pid", None)
        if (cp == pid and e.name == "UnitBornEvent"
                and norm(getattr(e.unit, "name", "")) in TOWNHALLS and e.second <= 1):
            main = e.location
            break

    placements = []           # (sec, base_name, x, y)
    natural = None
    unit_first, unit_count = {}, Counter()
    for e in r.tracker_events:
        cp = getattr(e, "control_pid", None) or getattr(e, "pid", None)
        if cp != pid:
            continue
        name = getattr(getattr(e, "unit", None), "name", None)
        if not name:
            continue
        base = norm(name)
        if e.name == "UnitInitEvent" and base in STRUCTURES and e.second <= window:
            loc = e.location
            placements.append((e.second, base, loc[0], loc[1]))
            if base == RACE_TH[race] and natural is None:
                natural = loc     # first newly-built townhall == the natural
        elif e.name in ("UnitBornEvent", "UnitInitEvent") and base not in STRUCTURES:
            if name in NONARMY or name.startswith("Beacon"):
                continue
            if e.second <= window:
                unit_count[name] += 1
                unit_first.setdefault(name, e.second)

    def dist(x, y, ref):
        return hypot(x - ref[0], y - ref[1]) if ref else None

    buildings = []
    for sec, base, x, y in sorted(placements):
        dm = dist(x, y, main)
        dn = dist(x, y, natural)
        buildings.append(dict(t=sec, s=base, x=x, y=y,
                              dist_main=round(dm, 1) if dm is not None else None,
                              dist_nat=round(dn, 1) if dn is not None else None,
                              zone=zone_of(dm if dm is not None else 999,
                                           dn, base in GAS)))

    economy = {m: dict(workers=int(stat_at(m, "workers_active_count", 12)),
                       supply=int(stat_at(m, "food_used", 12)),
                       mins_rate=int(stat_at(m, "minerals_collection_rate", 0)))
               for m in MARKS}
    th_inits = [b["t"] for b in buildings if b["s"] == RACE_TH[race]]
    return dict(
        race=race,
        buildings=buildings,
        order=[b["s"] for b in buildings],
        first_gas=next((b["t"] for b in buildings if b["s"] in GAS), None),
        expand=(th_inits[0] if th_inits else None),
        economy=economy,
        units=dict(unit_count),
        unit_first={k: v for k, v in sorted(unit_first.items(), key=lambda x: x[1])},
    )


# ---- classification -------------------------------------------------------
# The canonical rules live in strategy_engine.openings so a bot classifies an
# opponent live with exactly the same logic used to bucket this reference data.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from strategy_engine.openings import classify_opening  # noqa: E402


def classify(op):
    structures = [(b["s"], b["t"], b["zone"]) for b in op["buildings"]]
    return classify_opening(op["race"], structures, op["first_gas"], op["expand"])


# ---- aggregation ----------------------------------------------------------

def band(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return dict(n=n, median=median(xs), p25=xs[n // 4], p75=xs[min(n - 1, 3 * n // 4)])


def aggregate(ops_by_family):
    out = {}
    for fam, ops in ops_by_family.items():
        n = len(ops)
        # modal build order (first 5 distinct structures)
        seqs = Counter()
        for op in ops:
            distinct = []
            for s in op["order"]:
                if s not in distinct:
                    distinct.append(s)
                if len(distinct) >= 5:
                    break
            seqs[tuple(distinct)] += 1
        modal_order = list(seqs.most_common(1)[0][0]) if seqs else []
        # per-structure timing + modal zone
        struct_stats = {}
        names = {b["s"] for op in ops for b in op["buildings"]}
        for s in names:
            times, zones = [], Counter()
            for op in ops:
                bs = [b for b in op["buildings"] if b["s"] == s]
                if bs:
                    times.append(bs[0]["t"])
                    zones[bs[0]["zone"]] += 1
            tb = band(times)
            struct_stats[s] = dict(
                pct=round(100 * len(times) / n), timing=tb,
                zone=zones.most_common(1)[0][0] if zones else None)
        # economy bands at each mark
        econ = {}
        for m in MARKS:
            econ[m] = {k: band([op["economy"][m][k] for op in ops])
                       for k in ("workers", "supply", "mins_rate")}
        # unit reference (median count of the common units)
        unit_names = Counter()
        for op in ops:
            for u in op["units"]:
                unit_names[u] += 1
        units = {}
        for u, seen in unit_names.items():
            if seen >= max(2, n // 3):     # only units most openings actually make
                counts = [op["units"].get(u, 0) for op in ops]
                fts = [op["unit_first"].get(u) for op in ops if u in op["unit_first"]]
                units[u] = dict(pct=round(100 * seen / n),
                                count=band(counts), first=band(fts))
        out[fam] = dict(
            n=n,
            modal_order=modal_order,
            structures=dict(sorted(
                struct_stats.items(),
                key=lambda kv: (kv[1]["timing"]["median"] if kv[1]["timing"] else 999))),
            first_gas=band([op["first_gas"] for op in ops]),
            expand=band([op["expand"] for op in ops]),
            expand_pct=round(100 * sum(op["expand"] is not None for op in ops) / n),
            economy=econ,
            units=units,
        )
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    window = WINDOW
    if "--window" in sys.argv:
        window = int(sys.argv[sys.argv.index("--window") + 1])
    replay_dir = args[0] if args else "."

    files = sorted(glob.glob(os.path.join(replay_dir, "*.SC2Replay")))
    ops_by_family = defaultdict(list)
    ops_by_race = Counter()
    n_ok = 0
    for f in files:
        try:
            r = sc2reader.load_replay(f, load_level=4)
        except Exception:
            continue
        humans = [p for p in r.players if not p.is_observer] if r.players else []
        if len(humans) != 2:
            continue
        n_ok += 1
        for p in humans:
            if p.play_race not in RACE_TH:
                continue
            try:
                op = extract_player(r, p.pid, p.play_race, window)
            except Exception:
                continue
            fam = classify(op)
            op["result"] = getattr(p, "result", None)
            ops_by_family[fam].append(op)
            ops_by_race[p.play_race] += 1

    agg = aggregate(ops_by_family)

    print(f"# Opening extraction -- {n_ok} replays, window {window}s\n")
    for fam in sorted(agg, key=lambda k: -agg[k]["n"]):
        s = agg[fam]
        wins = sum(op["result"] == "Win" for op in ops_by_family[fam])
        print(f"## {fam}  (n={s['n']}, wins={wins}, expand={s['expand_pct']}%)")
        print(f"   order: {' > '.join(s['modal_order'])}")
        for st, d in s["structures"].items():
            if d["timing"]:
                print(f"     {st:<15} {d['pct']:>3}% @ {mmss(d['timing']['median'])}"
                      f"  [{d['zone']}]")
        e120 = s["economy"][120]
        if e120["workers"]:
            print(f"   @2:00 workers~{e120['workers']['median']} "
                  f"supply~{e120['supply']['median']} mins/min~{e120['mins_rate']['median']}")
        print()

    out_dir = os.path.join(os.path.dirname(__file__), "..", "strategy_engine", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(out_dir, "openings.json"))
    with open(out_path, "w") as f:
        json.dump({"window": window, "n_replays": n_ok, "families": agg}, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
