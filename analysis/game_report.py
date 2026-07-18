"""First-question debugging report for a replay: production & economy.

The debugging discipline: before anything else, ask *did production run well and
did the economy look good?* This reads a replay and answers that for one player
with a timeline and a red-flag scan -- so a loss is triaged as "macro broke"
(floating minerals, supply blocks, stalled workers, idle production) vs "macro
was fine, it was a tactical/army loss" before digging into micro.

    python analysis/game_report.py <replay> [player_name_or_race]

ECONOMY  -- workers, supply used/made, mineral+gas income, banked (floating).
PRODUCTION -- structures placed over time, and whether money was being spent.
RED FLAGS  -- floating cash, supply blocks, worker stalls, idle production.
"""
import re
import sys
import os
from collections import defaultdict

import principle_analyzer as pa  # sc2reader arena shim
import sc2reader

STRUCT = {  # normalized structure names worth listing in a build timeline
    "Nexus", "Pylon", "Gateway", "WarpGate", "Assimilator", "CyberneticsCore",
    "Forge", "RoboticsFacility", "Stargate", "TwilightCouncil", "PhotonCannon",
    "ShieldBattery", "RoboticsBay", "TemplarArchive", "DarkShrine", "FleetBeacon",
    "CommandCenter", "OrbitalCommand", "PlanetaryFortress", "SupplyDepot",
    "SupplyDepotLowered", "Barracks", "Refinery", "Factory", "Starport",
    "EngineeringBay", "Armory", "Bunker", "MissileTurret",
    "Hatchery", "Lair", "Hive", "SpawningPool", "Extractor", "RoachWarren",
    "BanelingNest", "EvolutionChamber", "HydraliskDen", "InfestationPit", "Spire",
}
NORM = {"WarpGate": "Gateway", "OrbitalCommand": "CommandCenter",
        "PlanetaryFortress": "CommandCenter", "Lair": "Hatchery", "Hive": "Hatchery",
        "SupplyDepotLowered": "SupplyDepot"}


def mmss(sec):
    return f"{int(sec)//60}:{int(sec) % 60:02d}"


def pick_pid(r, hint):
    humans = [p for p in r.players if not p.is_observer] if r.players else []
    if hint:
        for p in humans:
            if hint.lower() in p.name.lower() or hint.lower() == p.play_race.lower():
                return p.pid, p.name, p.result
    for p in humans:
        if not str(p.name).startswith("A.I."):
            return p.pid, p.name, p.result
    return (humans[0].pid, humans[0].name, humans[0].result) if humans else (1, "?", "?")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    hint = sys.argv[2] if len(sys.argv) > 2 else None
    r = sc2reader.load_replay(path, load_level=3)
    pid, name, result = pick_pid(r, hint)

    stats = sorted((e for e in r.tracker_events
                    if e.name == "PlayerStatsEvent" and e.pid == pid),
                   key=lambda e: e.second)
    builds = []
    for e in r.tracker_events:
        cp = getattr(e, "control_pid", None) or getattr(e, "pid", None)
        if cp == pid and e.name == "UnitInitEvent":
            n = getattr(e.unit, "name", None)
            if n in STRUCT:
                builds.append((e.second, NORM.get(n, n)))

    print(f"# Game report -- {name} ({r.map_name}), result: {result}, "
          f"length {r.game_length}\n")

    # ECONOMY + PRODUCTION timeline every ~45s
    print("time  | workers supply  min/min gas/min | banked(m/g)  spending  note")
    flags = []
    last_workers = 0
    for e in stats:
        if e.second % 45 > 4 and e.second not in (stats[-1].second,):
            continue
        w = int(getattr(e, "workers_active_count", 0))
        used, made = int(e.food_used), int(e.food_made)
        mrate = int(getattr(e, "minerals_collection_rate", 0))
        grate = int(getattr(e, "vespene_collection_rate", 0))
        bank_m, bank_g = int(e.minerals_current), int(e.vespene_current)
        in_prog = int(getattr(e, "minerals_used_in_progress", 0))
        note = ""
        blocked = made - used <= 1 and made < 200
        floating = bank_m > 500
        if blocked:
            note = "SUPPLY BLOCK"
        elif floating:
            note = "floating"
        print(f"{mmss(e.second):>5} | {w:>7} {used:>3}/{made:<3} {mrate:>7} {grate:>6} "
              f"| {bank_m:>5}/{bank_g:<4}  {in_prog:>6}  {note}")
        last_workers = w

    # RED-FLAG scan across the whole game
    peak_w = max((int(getattr(e, "workers_active_count", 0)) for e in stats), default=0)
    blocks = sum(1 for e in stats if int(e.food_made) - int(e.food_used) <= 1
                 and int(e.food_made) < 200)
    floats = sum(1 for e in stats if int(e.minerals_current) > 500)
    print("\n--- did production run well & economy look good? ---")
    print(f"  peak workers: {peak_w}  ({'ok' if peak_w >= 40 else 'LOW -- economy never developed'})")
    print(f"  supply-blocked samples: {blocks}  "
          f"({'ok' if blocks <= 2 else 'MACRO SLIP -- idle production from supply blocks'})")
    print(f"  floating (>500 min) samples: {floats}  "
          f"({'ok' if floats <= 2 else 'MACRO SLIP -- money not spent, production too slow'})")

    print("\n--- production (structures placed) ---")
    for t, n in builds[:40]:
        print(f"  {mmss(t):>5}  {n}")


if __name__ == "__main__":
    main()
