"""Extract a build order from a replay, to script a mimic ("sparring") bot.

Given a replay and (optionally) which player to study, prints a readable build
order -- structures, key units, and upgrades with their game-time and supply --
and emits a compact JSON spec a scripted bot can follow.

    python analysis/extract_build_order.py REPLAY [player_name_substring]

Works on AI Arena arena-client replays too (imports the shim from
principle_analyzer). See sparring/ for a bot that consumes this.
"""
import sys
import json
from collections import defaultdict, Counter

import principle_analyzer as pa  # applies the sc2reader arena shim
import sc2reader

STRUCTURES = {
    "Pylon", "Gateway", "WarpGate", "Nexus", "Assimilator", "Forge", "CyberneticsCore",
    "PhotonCannon", "ShieldBattery", "TwilightCouncil", "RoboticsFacility", "Stargate",
    "TemplarArchive", "DarkShrine", "RoboticsBay", "FleetBeacon",
    # Terran / Zerg minimal set for cross-race extraction
    "Barracks", "Factory", "Starport", "CommandCenter", "SupplyDepot", "Refinery",
    "Hatchery", "SpawningPool", "RoachWarren", "BanelingNest", "HydraliskDen", "Lair",
}


def mmss(sec):
    return f"{int(sec)//60}:{int(sec)%60:02d}"


def extract(path, who=None):
    r = sc2reader.load_replay(path, load_level=3)
    humans = [p for p in r.players if not p.is_observer] if r.players else []

    # Map pid -> display name. AA replays may not populate players; fall back to
    # filename-derived names is left to the caller -- here we use pid.
    names = {p.pid: p.name for p in humans} if humans else {}

    # Choose the player to study. `who` may be a pid number ("2") or a name
    # substring (only works when the replay carries player names -- AA replays
    # don't, so use the pid there).
    pid = None
    if who is not None:
        if str(who).isdigit():
            pid = int(who)
        elif names:
            for p, n in names.items():
                if who.lower() in n.lower():
                    pid = p
                    break
    if pid is None:
        pid = 1  # default: player 1

    steps = []
    unit_first = {}
    unit_counts = Counter()
    upgrades = []
    supply_at = {}

    # Track supply from PlayerStatsEvent for annotation.
    stats = [e for e in r.tracker_events if e.name == "PlayerStatsEvent" and e.pid == pid]
    stats.sort(key=lambda e: e.second)

    def supply_near(sec):
        best = 12
        for e in stats:
            if e.second <= sec:
                best = int(e.food_used)
            else:
                break
        return best

    for e in r.tracker_events:
        cpid = getattr(e, "control_pid", None) or getattr(e, "pid", None)
        if cpid != pid:
            continue
        if e.name == "UnitInitEvent" and e.unit.name in STRUCTURES:
            steps.append((e.second, "structure", e.unit.name))
        elif e.name in ("UnitBornEvent",) and e.unit.name in STRUCTURES:
            # morphed structures (Lair, WarpGate) show as born
            steps.append((e.second, "structure", e.unit.name))
        elif e.name in ("UnitBornEvent", "UnitInitEvent"):
            n = e.unit.name
            # Ignore non-units: larva/eggs and AI Arena control "Beacon" markers.
            if n not in STRUCTURES and not n.startswith("Beacon") and n not in ("Larva", "Egg", "Broodling"):
                unit_counts[n] += 1
                if n not in unit_first:
                    unit_first[n] = e.second
        elif e.name == "UpgradeCompleteEvent":
            nm = e.upgrade_type_name
            if not nm.lower().startswith("spray"):
                upgrades.append((e.second, nm))

    steps.sort()
    return dict(
        player=names.get(pid, f"player{pid}"),
        map=r.map_name,
        length=str(r.game_length),
        structures=[(mmss(t), name, supply_near(t)) for t, _, name in steps],
        first_units=[(mmss(t), n) for n, t in sorted(unit_first.items(), key=lambda x: x[1])],
        unit_counts=dict(unit_counts.most_common()),
        upgrades=[(mmss(t), n) for t, n in upgrades],
    )


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    who = sys.argv[2] if len(sys.argv) > 2 else None
    bo = extract(path, who)

    print(f"# Build order: {bo['player']} on {bo['map']} ({bo['length']})\n")
    print("## Structures (time | building | supply)")
    for t, name, sup in bo["structures"]:
        print(f"  {t:>6}  {name:<16} @{sup} supply")
    print("\n## First of each unit")
    for t, n in bo["first_units"]:
        print(f"  {t:>6}  {n}")
    print("\n## Units produced (total)")
    for n, c in bo["unit_counts"].items():
        print(f"  {c:>4}  {n}")
    print("\n## Upgrades")
    for t, n in bo["upgrades"]:
        print(f"  {t:>6}  {n}")

    out = path.rsplit("/", 1)[-1].replace(".SC2Replay", "") + ".buildorder.json"
    with open(out, "w") as f:
        json.dump(bo, f, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
