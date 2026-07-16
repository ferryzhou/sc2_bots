"""Analyze AegisBot harness replays against aegis/STRATEGY.md.

Joins ``aegis/results/history.jsonl`` (result, difficulty, opponent race, replay
path) with each replay's tracker events. AegisBot is always player 1 (Terran);
the built-in AI is player 2. Replays are loaded at ``load_level=3`` to avoid the
game-event parse crash on headless replays (same approach as ``aa_analyze.py``).

Beyond the shared ``principle_analyzer.attribute`` verdicts (economy, supply,
float, trade, upgrades, expand, harassment), this reports the two things the
AegisBot strategy contract lives or dies on:

  - **Composition** actually built (tanks/ghosts/vikings/... = STRATEGY §Composition)
  - **Production + static defense** structures (barracks vs factories, tech labs,
    bunkers, turrets, engineering bays) -- whether production capacity matches the
    comp (principle 2) and whether the defensive line exists (principle 4)

Usage:
    python analysis/analyze_aegis_replays.py [run_id]

CheatVision+ opponents get resource cheats, so their economy/float numbers are
inflated; weight macro attributions toward the non-cheating VeryHard games.
"""
import os
import sys
import json
import glob
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import principle_analyzer as pa  # applies sc2reader arena patch on import
import sc2reader

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(REPO, "aegis", "results", "history.jsonl")

ARMY_UNITS = {
    "Marine", "Marauder", "SiegeTank", "Medivac", "Ghost", "VikingFighter",
    "Viking", "Reaper", "Hellion", "Cyclone", "Thor", "Banshee", "Raven",
    "Liberator", "WidowMine",
}
STRUCTS = {
    "Barracks", "Factory", "Starport", "BarracksTechLab", "FactoryTechLab",
    "StarportTechLab", "EngineeringBay", "Bunker", "MissileTurret", "Refinery",
    "CommandCenter", "OrbitalCommand", "PlanetaryFortress",
}


def metrics(s):
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
    army_val = [e.minerals_used_current_army + e.vespene_used_current_army for e in s]
    biggest_drop = max((a - b for a, b in zip(army_val, army_val[1:])), default=0)
    return dict(
        peak_workers=max(e.workers_active_count for e in s),
        block_seconds=round(block * interval),
        avg_bank=round(sum(e.minerals_current + e.vespene_current for e in s) / len(s)),
        peak_bank=max(e.minerals_current + e.vespene_current for e in s),
        killed=killed, lost=lost,
        trade_ratio=round(killed / lost, 2) if lost else float("inf"),
        income=round(final.minerals_collection_rate + final.vespene_collection_rate),
        peak_army_val=max(army_val, default=0), biggest_army_drop=biggest_drop,
        worker_losses=worker_losses,
    )


def analyze(rec):
    path = rec["replay"]
    if not os.path.exists(path):
        return None
    r = sc2reader.load_replay(path, load_level=3)
    if r.game_length.seconds < 120:
        return None
    stats = defaultdict(list)
    upgrades = defaultdict(list)
    bases = defaultdict(set)
    comp = Counter()
    structs = Counter()
    for e in r.tracker_events:
        if e.name == "PlayerStatsEvent":
            stats[e.pid].append(e)
        elif e.name == "UpgradeCompleteEvent" and not e.upgrade_type_name.lower().startswith("spray"):
            upgrades[e.pid].append(e.upgrade_type_name)
        elif e.name in ("UnitBornEvent", "UnitInitEvent"):
            cpid = getattr(e, "control_pid", None)
            if e.unit.name in pa.TOWNHALLS:
                bases[cpid].add(e.unit_id)
            if cpid == 1:
                if e.unit.name in ARMY_UNITS:
                    comp[e.unit.name] += 1
                elif e.unit.name in STRUCTS:
                    structs[e.unit.name] += 1
    if not stats.get(1) or not stats.get(2):
        return None
    bot_win = rec["result"] == "Victory"
    pp = {}
    for pid in (1, 2):
        m = metrics(stats[pid])
        m["bases"] = len(bases[pid])
        m["upgrades"] = len(upgrades[pid])
        m["name"] = "AegisBot" if pid == 1 else f"AI-{rec['opponent_race']}"
        m["race"] = "Terran" if pid == 1 else rec["opponent_race"].title()
        m["result"] = "Win" if (pid == 1) == bot_win else "Loss"
        pp[pid] = m
    winner, loser = (pp[1], pp[2]) if bot_win else (pp[2], pp[1])
    return dict(
        map=r.map_name, length_min=round(r.game_length.seconds / 60, 1),
        difficulty=rec["difficulty"], opp_race=rec["opponent_race"], result=rec["result"],
        bot=pp[1], opp=pp[2], comp=dict(comp.most_common()), structs=dict(structs),
        verdicts=pa.attribute(winner, loser),
    )


def _army_supply(e):
    """food_used minus workers ~= army+structure supply (army-strength proxy)."""
    return e.food_used - e.workers_active_count


def _at_time(series, t):
    best = None
    for e in series:
        if e.second <= t:
            best = e
        else:
            break
    return best


def timeline(rec):
    """Per-loss trajectory: army-supply vs opponent at checkpoints, the decisive
    single-fight army-value drop, and whether the army rebuilt -- to place the
    loss in the aegis/STRATEGY.md buckets (A early all-in / B mid remax / C late
    grind)."""
    if not os.path.exists(rec["replay"]):
        return None
    r = sc2reader.load_replay(rec["replay"], load_level=3)
    stats = defaultdict(list)
    ups = defaultdict(list)
    for e in r.tracker_events:
        if e.name == "PlayerStatsEvent":
            stats[e.pid].append(e)
        elif e.name == "UpgradeCompleteEvent" and not e.upgrade_type_name.lower().startswith("spray"):
            ups[e.pid].append(e.second)
    bot, opp = stats.get(1), stats.get(2)
    if not bot or not opp:
        return None
    glen = r.game_length.seconds
    traj = []
    for t in (t for t in (360, 480, 600, 720, 840, 960) if t < glen):
        b, o = _at_time(bot, t), _at_time(opp, t)
        if b and o:
            traj.append((t // 60, _army_supply(b), _army_supply(o)))
    val = [(e.second, e.minerals_used_current_army + e.vespene_used_current_army) for e in bot]
    worst_t = worst_drop = before = after = 0
    for (ta, a), (tb, b) in zip(val, val[1:]):
        if a - b > worst_drop:
            worst_drop, worst_t, before, after = a - b, tb, a, b
    peak_after = max((v for (t, v) in val if t >= worst_t), default=after)
    return dict(
        opp_race=rec["opponent_race"], difficulty=rec["difficulty"], map=r.map_name,
        glen=glen, traj=traj, worst_t=worst_t, worst_drop=worst_drop, before=before,
        after=after, rebuilt=peak_after > after * 1.5, end_val=val[-1][1],
        bot_ups=len(ups[1]), opp_ups=len(ups[2]),
        last_bot_up=(ups[1][-1] if ups[1] else 0),
    )


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_timeline = "--timeline" in sys.argv
    run_id = args[0] if args else None
    recs = [json.loads(l) for l in open(HIST)]
    if run_id:
        recs = [r for r in recs if r.get("run_id") == run_id]

    if do_timeline:
        print("Per-loss timelines (army-supply bot vs opp; decisive drop; rebuild?)\n")
        for rec in recs:
            if rec.get("result") != "Defeat":
                continue
            try:
                t = timeline(rec)
            except Exception as ex:  # noqa: BLE001
                print(f"skip: {ex}", file=sys.stderr)
                continue
            if not t:
                continue
            traj = "  ".join(f"{m}'={b:.0f}v{o:.0f}" for (m, b, o) in t["traj"])
            print(f"### {t['opp_race']} {t['difficulty']} on {t['map']} "
                  f"(game {t['glen']//60}:{t['glen']%60:02d})")
            print(f"  army-supply/min: {traj}")
            print(f"  decisive drop: {t['before']}->{t['after']} (-{t['worst_drop']}) "
                  f"at {t['worst_t']//60}:{t['worst_t']%60:02d}; "
                  f"{'REBUILT' if t['rebuilt'] else 'did NOT recover'} (end {t['end_val']})")
            print(f"  upgrades: bot {t['bot_ups']} (last @ {t['last_bot_up']//60}m) "
                  f"vs opp {t['opp_ups']}\n")
        return
    games = []
    for rec in recs:
        try:
            g = analyze(rec)
        except Exception as ex:  # noqa: BLE001
            print(f"skip {os.path.basename(rec.get('replay', ''))}: {ex}", file=sys.stderr)
            continue
        if g:
            games.append(g)
    print(f"Analyzed {len(games)} AegisBot games"
          + (f" (run {run_id})" if run_id else "") + "\n")
    for g in games:
        b, o, s = g["bot"], g["opp"], g["structs"]
        tag = "WIN " if g["result"] == "Victory" else "LOSS"
        print(f"=== [{tag}] AegisBot(T) vs {g['opp_race']} {g['difficulty']} "
              f"on {g['map']} ({g['length_min']}min) ===")
        print(f"  bot  wk {b['peak_workers']:>3} base {b['bases']:>2} upg {b['upgrades']:>2} "
              f"trade {b['trade_ratio']:<5} float avg {b['avg_bank']:>5} peak {b['peak_bank']:>5} "
              f"block {b['block_seconds']:>3}s army_peak {b['peak_army_val']:>5} "
              f"worst_drop {b['biggest_army_drop']:>5} lostWk {b['worker_losses']}")
        print(f"  opp  wk {o['peak_workers']:>3} base {o['bases']:>2} upg {o['upgrades']:>2} "
              f"trade {o['trade_ratio']:<5}")
        print(f"  comp:    {g['comp'] or '(none)'}")
        prod = {k: s.get(k, 0) for k in ("Barracks", "Factory", "Starport",
                "BarracksTechLab", "FactoryTechLab", "StarportTechLab",
                "EngineeringBay", "Bunker", "MissileTurret")}
        print(f"  structs: {prod}")
        for principle, vtag, note in g["verdicts"]:
            print(f"    [{vtag:<7}] {principle}: {note}")
        print()
    agg = Counter()
    for g in games:
        for principle, vtag, _ in g["verdicts"]:
            agg[(principle, vtag)] += 1
    print("=== AGGREGATE (principle, verdict): count ===")
    for (principle, vtag), c in sorted(agg.items(), key=lambda x: -x[1]):
        print(f"  {principle:<12} {vtag:<7} {c}/{len(games)}")


if __name__ == "__main__":
    main()
