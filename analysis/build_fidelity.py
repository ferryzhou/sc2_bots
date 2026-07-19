"""Compare a bot's actual build (from a replay) against a scripted build guide.

Shows, for each key structure / expansion / tech / upgrade in the guide, the
guide's benchmark time vs when the bot actually achieved it -- so you can see how
faithfully a ``--build <id>`` run reproduced the plan and where it drifts.

    python analysis/build_fidelity.py <replay> <build_id> [our_pid]

Reads the guide from strategy_engine/data/build_guides/<id>.json.
"""
import sys
import os
import json

import principle_analyzer as pa  # noqa: F401  (sc2reader arena shim)
import loss_analysis as la

KEY_BUILD = {"Nexus", "Gateway", "Cybernetics Core", "Assimilator", "Stargate",
             "Twilight Council", "Forge", "Robotics Facility", "Robotics Bay",
             "Templar Archives", "Fleet Beacon", "Dark Shrine"}
KEY_RES = {"Warp Gate", "Charge", "Blink", "Psionic Storm"}
# guide display name -> replay structure token / upgrade name
STRUCT = {"Cybernetics Core": "CyberneticsCore", "Twilight Council": "TwilightCouncil",
          "Robotics Facility": "RoboticsFacility", "Robotics Bay": "RoboticsBay",
          "Templar Archives": "TemplarArchive", "Fleet Beacon": "FleetBeacon",
          "Dark Shrine": "DarkShrine"}
UPGRADE = {"Warp Gate": "WarpGateResearch", "Blink": "BlinkTech",
           "Psionic Storm": "PsiStorm", "Charge": "Charge",
           "Protoss Ground Weapons Level 1": "ProtossGroundWeaponsLevel1",
           "Protoss Ground Weapons Level 2": "ProtossGroundWeaponsLevel2",
           "Protoss Ground Weapons Level 3": "ProtossGroundWeaponsLevel3",
           "Protoss Ground Armor Level 1": "ProtossGroundArmorsLevel1",
           "Protoss Ground Armor Level 2": "ProtossGroundArmorsLevel2",
           "Protoss Ground Armor Level 3": "ProtossGroundArmorsLevel3",
           "Protoss Air Weapons Level 1": "ProtossAirWeaponsLevel1",
           "Protoss Air Weapons Level 2": "ProtossAirWeaponsLevel2"}


def mmss(t):
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def main():
    replay, build_id = sys.argv[1], sys.argv[2]
    ours = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    guide_path = os.path.join(os.path.dirname(__file__), "..", "strategy_engine",
                              "data", "build_guides", f"{build_id}.json")
    steps = json.load(open(guide_path))["steps"]

    # guide: ordered first-occurrence of each key item
    pro, seen = [], set()
    for s in steps:
        n, t, a = s["name"], s["t"], s["action"]
        kind = ("build" if a == "build" and n in KEY_BUILD
                else "res" if a == "research" and (n in KEY_RES or "Level" in n) else None)
        if kind and (kind, n) not in seen:
            seen.add((kind, n))
            pro.append((t, kind, n))

    # replay: first-occurrence of each structure (warp gate counts as gateway) + upgrades
    r, units, stats, upg = la.load(replay)
    struct, nexus = {}, []
    for owner, name, born, _ in units.values():
        if owner != ours:
            continue
        if name == "Nexus":
            nexus.append(born)
            continue
        key = "Gateway" if name in ("Gateway", "WarpGate") else name
        struct[key] = min(struct.get(key, 1e9), born)
    nexus.sort()
    upg_first = {}
    for t, name in upg[ours]:
        upg_first.setdefault(name, t)

    nexus_i = [0]

    def actual(kind, name):
        if name == "Nexus":
            nexus_i[0] += 1
            return nexus[nexus_i[0]] if nexus_i[0] < len(nexus) else None
        if kind == "build":
            return struct.get(STRUCT.get(name, name))
        return upg_first.get(UPGRADE.get(name))

    print(f"# Build fidelity: {os.path.basename(replay)} vs build {build_id}\n")
    print(f"{'BUILD ITEM':28}{'GUIDE':>7}{'ACTUAL':>8}   status")
    print("-" * 55)
    for t, kind, n in pro:
        at = actual(kind, n)
        if at is None:
            print(f"{n:28}{mmss(t):>7}{'--':>8}   MISSING")
            continue
        d = int(at - t)
        tag = ("on time" if abs(d) < 25
               else f"{d:+d}s late" if d > 0 else f"{d:+d}s early")
        print(f"{n:28}{mmss(t):>7}{mmss(at):>8}   {tag}")


if __name__ == "__main__":
    main()
