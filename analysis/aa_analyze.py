"""Analyze AI Arena replays against the principles.

AA arena-client replays don't carry player results and use a few game-event types
sc2reader 1.9 can't parse, so we: load at load_level=3 (tracker events only), take
winner/names from the API metadata (aa_meta.json written by aa_download.py), and
infer race from tracker unit events. Metric extraction and principle attribution
are shared with principle_analyzer.py.

    python analysis/aa_analyze.py [replay_dir]   # dir must contain aa_meta.json
"""
import os
import re
import sys
import json
import glob
from collections import Counter, defaultdict

import principle_analyzer as pa  # applies the sc2reader arena shim on import
import sc2reader

TH_RACE = {"Nexus": "Protoss", "CommandCenter": "Terran", "Hatchery": "Zerg"}

DIR = sys.argv[1] if len(sys.argv) > 1 else "replays_aa"
META = json.load(open(os.path.join(DIR, "aa_meta.json")))


def player_metrics(s, upgrades, bases):
    final = s[-1]
    interval = max(1, (s[-1].second - s[0].second) / max(1, len(s) - 1))
    block = sum(1 for e in s if e.food_made < 200 and e.food_used >= e.food_made > 0)
    killed = final.minerals_killed + final.vespene_killed
    lost = final.minerals_lost + final.vespene_lost
    worker_losses = sum(
        max(0, a.workers_active_count - b.workers_active_count)
        for a, b in zip(s, s[1:])
        if a.workers_active_count - b.workers_active_count >= 3
    )
    return dict(
        peak_workers=max(e.workers_active_count for e in s),
        final_workers=final.workers_active_count,
        bases=len(bases), block_seconds=round(block * interval),
        avg_bank=round(sum(e.minerals_current + e.vespene_current for e in s) / len(s)),
        killed=killed, lost=lost,
        trade_ratio=round(killed / lost, 2) if lost else float("inf"),
        income=round(final.minerals_collection_rate + final.vespene_collection_rate),
        upgrades=len(upgrades), worker_losses=worker_losses,
    )


def analyze(path):
    mid = re.match(r"aa_(\d+)_", os.path.basename(path)).group(1)
    m = META.get(mid)
    if not m:
        return None
    r = sc2reader.load_replay(path, load_level=3)
    if r.game_length.seconds < 180:
        return None
    stats, upgrades, bases = defaultdict(list), defaultdict(list), defaultdict(set)
    race_votes = defaultdict(Counter)
    for e in r.tracker_events:
        if e.name == "PlayerStatsEvent":
            stats[e.pid].append(e)
        elif e.name == "UpgradeCompleteEvent" and not e.upgrade_type_name.lower().startswith("spray"):
            upgrades[e.pid].append(e.upgrade_type_name)
        elif e.name in ("UnitBornEvent", "UnitInitEvent") and e.unit.name in pa.TOWNHALLS:
            cpid = getattr(e, "control_pid", None)
            bases[cpid].add(e.unit_id)
            if e.unit.name in TH_RACE:
                race_votes[cpid][TH_RACE[e.unit.name]] += 1
    if set(stats) != {1, 2} or not stats[1] or not stats[2]:
        return None
    names = {1: m["b1"], 2: m["b2"]}
    winner_pid = 1 if m["type"] == "Player1Win" else 2
    pp = {}
    for pid in (1, 2):
        race = race_votes[pid].most_common(1)
        pp[pid] = dict(name=names[pid], race=race[0][0] if race else "?",
                       result="Win" if pid == winner_pid else "Loss",
                       **player_metrics(stats[pid], upgrades[pid], bases[pid]))
    w, l = pp[winner_pid], pp[3 - winner_pid]
    return dict(map=r.map_name, length_min=round(r.game_length.seconds / 60, 1),
                matchup=f"{w['race'][0]}v{l['race'][0]}", winner=w, loser=l,
                verdicts=pa.attribute(w, l))


def main():
    games = []
    for path in sorted(glob.glob(os.path.join(DIR, "*.SC2Replay"))):
        try:
            g = analyze(path)
        except Exception as ex:
            print(f"skip {os.path.basename(path)}: {ex}", file=sys.stderr)
            continue
        if g:
            games.append(g)
    print(f"Analyzed {len(games)} AI Arena 1v1 games\n")
    for g in games:
        w, l = g["winner"], g["loser"]
        print(f"=== {g['matchup']} {w['name']} beat {l['name']} on {g['map']} ({g['length_min']}min) ===")
        print(f"  WIN  {w['name']:<16} wk {w['peak_workers']:>3} base {w['bases']:>2} upg {w['upgrades']:>2} "
              f"trade {w['trade_ratio']} bank {w['avg_bank']:>5} block {w['block_seconds']:>3}s")
        print(f"  LOSS {l['name']:<16} wk {l['peak_workers']:>3} base {l['bases']:>2} upg {l['upgrades']:>2} "
              f"trade {l['trade_ratio']} bank {l['avg_bank']:>5} block {l['block_seconds']:>3}s")
        for principle, tag, note in g["verdicts"]:
            print(f"    [{tag:<7}] {principle}: {note}")
        print()
    agg = Counter()
    for g in games:
        for principle, tag, _ in g["verdicts"]:
            agg[(principle, tag)] += 1
    print("=== AGGREGATE (principle, verdict): count ===")
    for (principle, tag), c in sorted(agg.items(), key=lambda x: -x[1]):
        print(f"  {principle:<12} {tag:<7} {c}/{len(games)}")


if __name__ == "__main__":
    main()
