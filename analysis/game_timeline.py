"""Minute-by-minute play-by-play for one player from a replay.

Per minute: workers, supply (used/made), mineral & gas income (bank/rate), and the
action sequence -- every structure, unit, and upgrade produced that minute.

    python analysis/game_timeline.py <replay> [our_pid] [build_id]

With a build_id, adds a head-to-head column vs that professional build: the pro's
supply benchmark (interpolated) and the pro's key actions that minute.
"""
import sys
import os
import json
from collections import Counter, defaultdict

import principle_analyzer as pa  # noqa: F401  (sc2reader arena shim)
import loss_analysis as la

TECH_STRUCT = {"CyberneticsCore", "TwilightCouncil", "Forge", "Stargate",
               "RoboticsFacility", "RoboticsBay", "TemplarArchive", "FleetBeacon",
               "DarkShrine"}
PRO_TECH = {"Cybernetics Core", "Twilight Council", "Forge", "Stargate",
            "Robotics Facility", "Robotics Bay", "Templar Archives", "Fleet Beacon"}
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

    # bucket births (structures / non-worker units / worker count) by minute,
    # and keep running totals (bases, tech buildings) for the state at time t
    struct_min = defaultdict(list)
    unit_min = defaultdict(Counter)
    probe_min = Counter()
    base_at = []   # (born, cumulative bases)  -- start base pre-exists
    tech_at = []   # (born, cumulative tech buildings)
    bases = tech = 0
    for born, name in sorted((b, n) for o, n, b, _ in units.values() if o == ours):
        if name == "Nexus":
            bases += 1
            base_at.append((born, bases))
        elif name in TECH_STRUCT:
            tech += 1
            tech_at.append((born, tech))
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
    # upgrades completed, by minute
    upg_min = defaultdict(list)
    for sec, name in upgrades[ours]:
        upg_min[int(sec) // 60].append(name)

    def count_by(pairs, t):
        """cumulative count from a sorted list of (time, cumulative) at time t."""
        c = 0
        for born, cum in pairs:
            if born <= t:
                c = cum
            else:
                break
        return c

    def upg_count(t):
        return sum(1 for sec, _ in upgrades[ours] if sec <= t)

    def stat(t, f):
        return int(la.stat_at(stats, ours, t, f))

    title = f"# Timeline: {os.path.basename(path)} ({r.map_name}, {r.game_length}) pid {ours}"
    if build_id:
        title += f"  vs PRO build {build_id}  ('!' = we're <80% of the pro benchmark)"
    print(title + "\n")
    if build_id:
        # us/pro side-by-side for every headline metric, then our income + actions
        hdr = (f"{'time':>5} | {'workers':>9} | {'army sup':>9} | {'supply':>9} | "
               f"{'bases':>7} | {'tech':>7} | {'upg':>7} | {'min/gas inc':>11} | "
               f"actions  (us  ‖  PRO)")
        print(hdr)
        print("-" * len(hdr))
    else:
        print(f"{'time':>5} | {'wk':>3} | {'sup':>7} | {'minerals':>11} | {'gas':>10} | actions this minute")
        print("-" * 110)
    for m in range(0, length // 60 + 1):
        t = m * 60
        if t == 0:
            continue
        wk = stat(t, "workers_active_count")
        used, made = stat(t, "food_used"), stat(t, "food_made")
        mb, mr = stat(t, "minerals_current"), stat(t, "minerals_collection_rate")
        gb, gr = stat(t, "vespene_current"), stat(t, "vespene_collection_rate")
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
            army = max(0, used - wk)          # non-worker supply
            us = {"workers": wk, "army": army, "supply": used,
                  "bases": count_by(base_at, t) + 1, "tech": count_by(tech_at, t),
                  "upg": upg_count(t)}
            pro = pro_metrics(steps, t)
            pa_line = ", ".join(dict.fromkeys(pro_acts.get(m - 1, []))) or "-"

            def cell(k):
                return f"{us[k]:>3}/{pro[k]:<3}{_flag(us[k], pro[k])}"
            print(f"{mmss(t):>5} | {cell('workers'):>9} | {cell('army'):>9} | "
                  f"{cell('supply'):>9} | {cell('bases'):>7} | {cell('tech'):>7} | "
                  f"{cell('upg'):>7} | {mr:>4}/{gr:<6} | {line}  ‖  {pa_line}")
        else:
            print(f"{mmss(t):>5} | {wk:>3} | {used:>3}/{made:<3} | "
                  f"{mb:>4}/{mr:<6} | {gb:>4}/{gr:<5} | {line}")


if __name__ == "__main__":
    main()
