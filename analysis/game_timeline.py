"""Minute-by-minute play-by-play for one player from a replay.

Per minute: workers, supply (used/made), mineral & gas income (bank/rate), and the
action sequence -- every structure, unit, and upgrade produced that minute.

    python analysis/game_timeline.py <replay> [our_pid] [build_id]

The per-minute numeric STATE is pulled from the shared ``loss_analysis.metrics_at``
extractor (the one place the metric set is defined), so this and every other
comparison tool score the same fields. This module only adds the play-by-play
(action sequences) and, with a build_id, the head-to-head vs a professional build:
each metric shown ``us/pro`` with '!' when we're under 80% of the pro benchmark.
The pro side is derived from the build guide by ``pro_metrics`` into the same dict
shape, so extraction and comparison stay decoupled.
"""
import sys
import os
import json
from collections import Counter, defaultdict

import principle_analyzer as pa  # noqa: F401  (sc2reader arena shim)
import loss_analysis as la

PRO_TECH = {"Cybernetics Core", "Twilight Council", "Forge", "Stargate",
            "Robotics Facility", "Robotics Bay", "Templar Archives", "Fleet Beacon"}
# the metrics scored us-vs-pro, in display order: (metric key, header, width).
# Add a metric by adding one row here (both sources already produce the key).
COMPARE_COLS = [("workers", "workers", 9), ("army", "army sup", 9),
                ("supply", "supply", 9), ("bases", "bases", 7),
                ("tech", "tech", 7), ("upg", "upg", 7)]
# guide unit name -> its supply cost
PRO_ARMY_SUPPLY = {"Adept": 2, "Zealot": 2, "Stalker": 2, "Sentry": 2, "Oracle": 3,
                   "Phoenix": 2, "Void Ray": 4, "Immortal": 4, "Colossus": 6,
                   "High Templar": 2, "Dark Templar": 2, "Archon": 4, "Carrier": 6,
                   "Tempest": 5, "Observer": 1, "Warp Prism": 2, "Disruptor": 3}


def load_pro(build_id):
    """Return the build's raw steps for per-minute metric derivation."""
    path = os.path.join(os.path.dirname(__file__), "..", "strategy_engine",
                        "data", "build_guides", f"{build_id}.json")
    return json.load(open(path))["steps"]


def _supply_pts(steps):
    return sorted({(s["t"], s["supply"]) for s in steps if s.get("supply")})


def pro_metrics(steps, t):
    """Derive the pro build's state at time t: workers, army supply, total supply,
    bases, tech-building count, upgrade count. Workers = total supply - army supply
    (the build lists no probes; they're continuous)."""
    pts = _supply_pts(steps)
    total = pts[0][1] if (not pts or t < pts[0][0]) else pts[-1][1]
    for (t0, s0), (t1, s1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            total = int(s0 + (s1 - s0) * (t - t0) / (t1 - t0)) if t1 > t0 else s0
            break
    army = bases = tech = upg = 0
    for s in steps:
        if s["t"] > t:
            continue
        n, a, c = s["name"], s["action"], s.get("count", 1)
        if a == "train" and n in PRO_ARMY_SUPPLY:
            army += PRO_ARMY_SUPPLY[n] * c
        elif a == "build" and n == "Nexus":
            bases += c
        elif a == "build" and n in PRO_TECH:
            tech += c
        elif a == "research":
            upg += c
    return {"workers": max(0, total - army), "army": army, "supply": total,
            "bases": 1 + bases, "tech": tech, "upg": upg}

STRUCTURES = {"Nexus", "Pylon", "Assimilator", "Gateway", "WarpGate",
              "CyberneticsCore", "Forge", "PhotonCannon", "ShieldBattery",
              "TwilightCouncil", "Stargate", "RoboticsFacility", "RoboticsBay",
              "TemplarArchive", "FleetBeacon", "DarkShrine"}
WORKER = "Probe"
DISPLAY = {"CyberneticsCore": "Cyber", "TwilightCouncil": "Twilight",
           "RoboticsFacility": "Robo", "RoboticsBay": "RoboBay",
           "TemplarArchive": "TemplarArchive", "PhotonCannon": "Cannon",
           "ShieldBattery": "Battery", "Assimilator": "Gas",
           "WarpGate": "Gateway"}  # a WarpGate is a morphed Gateway


def mmss(s):
    return f"{int(s) // 60}:{int(s) % 60:02d}"


def _pro_actions(steps):
    """Bucket the pro build's key actions by minute (deduped, for display)."""
    acts = defaultdict(list)
    for s in steps:
        n, a, m = s["name"], s["action"], int(s["t"]) // 60
        if a == "build":
            acts[m].append("+" + n)
        elif a == "train":
            acts[m].append(n)
        elif a == "research":
            acts[m].append("*" + n)
    return acts


def _flag(us, pro, ratio=0.8):
    """'!' when we're materially behind the pro benchmark (and the pro has any)."""
    return "!" if pro and us < ratio * pro else " "


def main():
    path = sys.argv[1]
    ours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    build_id = sys.argv[3] if len(sys.argv) > 3 else None
    steps = load_pro(build_id) if build_id else None
    pro_acts = _pro_actions(steps) if steps else {}
    r, units, stats, upgrades = la.load(path)
    length = int(r.game_length.seconds)

    # bucket the ACTIONS (structures / non-worker units / probes / upgrades) by
    # minute -- the play-by-play. The numeric STATE per minute (workers, army,
    # supply, bases, tech, upgrades, income) is not re-derived here: it comes from
    # the shared la.metrics_at extractor, so every scorecard sees the same metrics.
    struct_min = defaultdict(list)
    unit_min = defaultdict(Counter)
    probe_min = Counter()
    for owner, name, born, _ in units.values():
        if owner != ours:
            continue
        m = int(born) // 60
        if name in STRUCTURES:
            struct_min[m].append((born, name))
        elif name == WORKER:
            probe_min[m] += 1
        elif la.is_army(name) or name in ("Observer", "WarpPrism", "Oracle"):
            unit_min[m][name] += 1
    upg_min = defaultdict(list)
    for sec, name in upgrades[ours]:
        upg_min[int(sec) // 60].append(name)

    title = f"# Timeline: {os.path.basename(path)} ({r.map_name}, {r.game_length}) pid {ours}"
    if build_id:
        title += f"  vs PRO build {build_id}  ('!' = we're <80% of the pro benchmark)"
    print(title + "\n")
    if build_id:
        # us/pro side-by-side for every headline metric, then our income + actions
        hdr = f"{'time':>5} | " + " | ".join(f"{h:>{w}}" for _, h, w in COMPARE_COLS)
        hdr += f" | {'min/gas inc':>11} | actions  (us  ‖  PRO)"
        print(hdr)
        print("-" * len(hdr))
    else:
        print(f"{'time':>5} | {'wk':>3} | {'sup':>7} | {'minerals':>11} | {'gas':>10} | actions this minute")
        print("-" * 110)
    for m in range(0, length // 60 + 1):
        t = m * 60
        if t == 0:
            continue
        us = la.metrics_at(units, stats, upgrades, ours, t)
        made = int(la.stat_at(stats, ours, t, "food_made"))
        mb = int(la.stat_at(stats, ours, t, "minerals_current"))
        gb = int(la.stat_at(stats, ours, t, "vespene_current"))
        acts = []
        for _, name in sorted(struct_min.get(m - 1, [])):  # produced in the PRIOR minute
            acts.append("+" + DISPLAY.get(name, name))
        for name, c in unit_min.get(m - 1, Counter()).most_common():
            acts.append(f"{c}x{name}")
        if probe_min.get(m - 1):
            acts.append(f"{probe_min[m - 1]}xProbe")
        for u in upg_min.get(m - 1, []):
            acts.append("*" + u.replace("Level", "L").replace("Protoss", ""))
        line = ", ".join(acts) if acts else "-"
        if build_id:
            pro = pro_metrics(steps, t)
            pa_line = ", ".join(dict.fromkeys(pro_acts.get(m - 1, []))) or "-"
            cells = " | ".join(
                f"{f'{us[k]:>3}/{pro[k]:<3}{_flag(us[k], pro[k])}':>{w}}"
                for k, _, w in COMPARE_COLS)
            print(f"{mmss(t):>5} | {cells} | "
                  f"{us['min_inc']:>4}/{us['gas_inc']:<6} | {line}  ‖  {pa_line}")
        else:
            print(f"{mmss(t):>5} | {us['workers']:>3} | {us['supply']:>3}/{made:<3} | "
                  f"{mb:>4}/{us['min_inc']:<6} | {gb:>4}/{us['gas_inc']:<5} | {line}")


if __name__ == "__main__":
    main()
