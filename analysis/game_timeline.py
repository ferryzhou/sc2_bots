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

PRO_KEY_BUILD = {"Nexus", "Gateway", "Cybernetics Core", "Stargate", "Robotics Facility",
                 "Robotics Bay", "Twilight Council", "Forge", "Templar Archives",
                 "Fleet Beacon", "Dark Shrine"}
PRO_KEY_RES = {"Warp Gate", "Charge", "Blink", "Psionic Storm"}


def load_pro(build_id):
    """Return (supply_points, actions_by_minute) for a build guide."""
    path = os.path.join(os.path.dirname(__file__), "..", "strategy_engine",
                        "data", "build_guides", f"{build_id}.json")
    steps = json.load(open(path))["steps"]
    pts = sorted({(s["t"], s["supply"]) for s in steps if s.get("supply")})
    acts = defaultdict(list)
    for s in steps:
        n, t, a = s["name"], s["t"], s["action"]
        if a == "build" and n in PRO_KEY_BUILD:
            acts[int(t) // 60].append(n.split()[0] if n != "Robotics Bay" else "RoboBay")
        elif a == "research" and (n in PRO_KEY_RES or "Level" in n):
            acts[int(t) // 60].append("*" + n.replace("Protoss ", "").replace("Level", "L"))
    return pts, acts


def pro_supply(pts, t):
    """Linear-interpolate the pro build's supply at time t."""
    if not pts or t < pts[0][0]:
        return pts[0][1] if pts else 0
    for (t0, s0), (t1, s1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return int(s0 + (s1 - s0) * (t - t0) / (t1 - t0)) if t1 > t0 else s0
    return pts[-1][1]

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


def main():
    path = sys.argv[1]
    ours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    build_id = sys.argv[3] if len(sys.argv) > 3 else None
    pro_pts, pro_acts = load_pro(build_id) if build_id else (None, None)
    r, units, stats, upgrades = la.load(path)
    length = int(r.game_length.seconds)

    # bucket births (structures / non-worker units / worker count) by minute
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
    # upgrades completed, by minute
    upg_min = defaultdict(list)
    for sec, name in upgrades[ours]:
        upg_min[int(sec) // 60].append(name)

    def stat(t, f):
        return int(la.stat_at(stats, ours, t, f))

    title = f"# Timeline: {os.path.basename(path)} ({r.map_name}, {r.game_length}) pid {ours}"
    if build_id:
        title += f"  vs PRO build {build_id}"
    print(title + "\n")
    if build_id:
        print(f"{'time':>5} | {'workers':>7} | {'supply us/PRO':>13} | {'min inc':>7} | "
              f"{'gas inc':>7} | our actions  ‖  PRO actions")
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
            ps = pro_supply(pro_pts, t)
            pa_line = ", ".join(dict.fromkeys(pro_acts.get(m, []))) or "-"
            flag = " !" if ps and used < 0.8 * ps else ""
            print(f"{mmss(t):>5} | {wk:>7} | {used:>4}/{ps:<8}{flag:<2} | {mr:>7} | "
                  f"{gr:>7} | {line}  ‖  {pa_line}")
        else:
            print(f"{mmss(t):>5} | {wk:>3} | {used:>3}/{made:<3} | "
                  f"{mb:>4}/{mr:<6} | {gb:>4}/{gr:<5} | {line}")


if __name__ == "__main__":
    main()
