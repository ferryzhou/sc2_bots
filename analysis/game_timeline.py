"""Minute-by-minute play-by-play for one player from a replay.

Per minute: workers, supply (used/made), mineral & gas income (bank/rate), and the
action sequence -- every structure, unit, and upgrade produced that minute.

    python analysis/game_timeline.py <replay> [our_pid]
"""
import sys
import os
from collections import Counter, defaultdict

import principle_analyzer as pa  # noqa: F401  (sc2reader arena shim)
import loss_analysis as la

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

    print(f"# Timeline: {os.path.basename(path)} ({r.map_name}, {r.game_length}) pid {ours}\n")
    print(f"{'time':>5} | {'wk':>3} | {'sup':>7} | {'minerals':>11} | {'gas':>10} | actions this minute")
    print(f"{'':>5} | {'':>3} | {'use/made':>7} | {'bank/rate':>11} | {'bank/rate':>10} |")
    print("-" * 100)
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
            acts.append(f"{probe_min[m - 1]}x Probe")
        for u in upg_min.get(m - 1, []):
            acts.append("*" + u.replace("Level", "L").replace("Protoss", ""))
        line = ", ".join(acts) if acts else "-"
        print(f"{mmss(t):>5} | {wk:>3} | {used:>3}/{made:<3} | "
              f"{mb:>4}/{mr:<6} | {gb:>4}/{gr:<5} | {line}")


if __name__ == "__main__":
    main()
