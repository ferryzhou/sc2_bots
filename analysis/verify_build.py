"""Confirm a bot reproduced a scripted build, by reading the saved replay.

Given a replay and the spawningtool build id the bot was told to run, this
extracts the bot's ACTUAL build order (structures placed, units first trained,
upgrades finished) and diffs it against the INTENDED
``strategy_engine.build_guides`` script -- reporting which steps were reproduced,
at what game time, and the overall reproduction fraction.

    python analysis/verify_build.py <replay> <build_id> [player_name_or_race]

Names are matched by canonicalising to the sc2 id token (upper-case, alnum only,
morphs folded: WarpGate->Gateway, Lair->Hatchery, Orbital->CommandCenter), which
is exactly how build_guides tokens are spelled.
"""
import re
import sys
import os
from collections import defaultdict

import principle_analyzer as pa  # sc2reader arena shim
import sc2reader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from strategy_engine import get_build  # noqa: E402

MORPH = {"WARPGATE": "GATEWAY", "LAIR": "HATCHERY", "HIVE": "HATCHERY",
         "ORBITALCOMMAND": "COMMANDCENTER", "PLANETARYFORTRESS": "COMMANDCENTER",
         "SUPPLYDEPOTLOWERED": "SUPPLYDEPOT"}


def canon(name):
    tok = re.sub(r"[^A-Z0-9]", "", str(name).upper())
    return MORPH.get(tok, tok)


def mmss(sec):
    return f"{int(sec)//60}:{int(sec) % 60:02d}" if sec is not None else "  -  "


def pick_pid(r, hint):
    humans = [p for p in r.players if not p.is_observer] if r.players else []
    if hint:
        for p in humans:
            if hint.lower() in p.name.lower() or hint.lower() == p.play_race.lower():
                return p.pid, p.name
    # default: the non-"A.I." player, else player 1
    for p in humans:
        if not str(p.name).startswith("A.I."):
            return p.pid, p.name
    return (humans[0].pid, humans[0].name) if humans else (1, "player1")


def actual_build(r, pid):
    """token -> sorted list of event times (structures placed / unit born / upgrade)."""
    events = defaultdict(list)
    for e in r.tracker_events:
        cp = getattr(e, "control_pid", None) or getattr(e, "pid", None)
        if e.name == "UpgradeCompleteEvent" and e.pid == pid:
            events[canon(e.upgrade_type_name)].append(e.second)
            continue
        if cp != pid:
            continue
        if e.name == "UnitInitEvent":                 # structure placed
            n = getattr(e.unit, "name", None)
            if n:
                events[canon(n)].append(e.second)
        elif e.name == "UnitBornEvent":               # unit / morphed structure
            n = getattr(e.unit, "name", None)
            if not n or n in ("Larva", "Egg"):
                continue
            tok = canon(n)
            # the starting townhall is a Born at t~0 and is not a build step --
            # drop it so a build's expand steps match real expansions, not the main
            if tok in ("NEXUS", "COMMANDCENTER", "HATCHERY") and e.second <= 1:
                continue
            events[tok].append(e.second)
    for k in events:
        events[k].sort()
    return events


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    replay_path, build_id = sys.argv[1], int(sys.argv[2])
    hint = sys.argv[3] if len(sys.argv) > 3 else None

    build = get_build(build_id)
    if build is None:
        sys.exit(f"build {build_id} not ingested")
    # level 3 = tracker events only (Init/Born/UpgradeComplete); level 4 adds
    # game events whose sc2reader plugins crash on vs-AI replays.
    r = sc2reader.load_replay(replay_path, load_level=3)
    pid, name = pick_pid(r, hint)
    actual = actual_build(r, pid)

    print(f"# Reproduction check: {build.title} [{build.matchup}]")
    print(f"# replay: {os.path.basename(replay_path)}  player: {name} (pid {pid})\n")

    # walk intended build steps in order; consume actual events greedily
    used = defaultdict(int)
    rows, hit = [], 0
    for a in build.build_steps():
        tok = a.token
        if not tok:
            continue
        times = actual.get(tok, [])
        idx = used[tok]
        if idx < len(times):
            t = times[idx]
            used[tok] += 1
            hit += 1
            rows.append((a.at_supply, a.action, a.name, t, "OK"))
        else:
            rows.append((a.at_supply, a.action, a.name, None, "MISS"))

    total = sum(1 for a in build.build_steps() if a.token)
    print(f"{'supply':>6} {'step':<26} {'intended':>8} {'actual':>8}  status")
    for sup, act, nm, t, status in rows:
        print(f"{sup or '?':>6} {nm[:26]:<26} {'@'+str(sup) if sup else '':>8} "
              f"{mmss(t):>8}  {status}")
    print(f"\nreproduced {hit}/{total} steps ({round(100*hit/max(1,total))}%)")

    # order fidelity: are the reproduced steps in the intended order by time?
    seq = [t for *_, t, s in rows if s == "OK"]
    inversions = sum(1 for i in range(1, len(seq)) if seq[i] < seq[i - 1] - 5)
    print(f"order: {len(seq)} reproduced steps, {inversions} out-of-order (>5s)")


if __name__ == "__main__":
    main()
