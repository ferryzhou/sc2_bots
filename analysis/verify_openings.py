"""Validate the opening library against the replays it was mined from.

For each player-opening: extract its telemetry, classify it, then run
``strategy_engine.verify_opening`` against EVERY opening of that race. A healthy
library has two properties, both reported here:

  1. Fit -- an opening has few deviations against its own classified family.
  2. Separation -- its own family fits better (fewer deviations) than the other
     families of its race, i.e. the openings are actually distinct.

    python analysis/verify_openings.py <replay_dir>

This is also a worked example of reusing the library from outside a bot.
"""
import sys
import os
import glob
from collections import defaultdict

import principle_analyzer as pa  # sc2reader arena shim
import sc2reader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import extract_openings as ex
import strategy_engine as se


def dev_weight(devs, structural_only=False):
    # Early economy is near-identical across families (~16 workers at 2:00), so
    # it can't tell openings apart -- for SEPARATION score only the structural
    # signals (which buildings, when, where). Full weight is used for FIT.
    w = {"major": 3, "warn": 1, "info": 0.3}
    cats = {"missing", "timing", "placement"}
    return sum(w[d.severity] for d in devs
               if not structural_only or d.category in cats)


def main():
    replay_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    files = sorted(glob.glob(os.path.join(replay_dir, "*.SC2Replay")))

    per_family = defaultdict(lambda: {"n": 0, "own": 0.0, "sep_ok": 0})
    total = 0
    for f in files:
        try:
            r = sc2reader.load_replay(f, load_level=4)
        except Exception:
            continue
        ok, humans = ex.eligible(r)
        if not ok:
            continue
        for p in humans:
            if p.play_race not in ex.RACE_TH:
                continue
            try:
                op = ex.extract_player(r, p.pid, p.play_race, ex.WINDOW)
            except Exception:
                continue
            fam = ex.classify(op)
            own = se.get_opening(fam)
            if own is None:
                continue
            telem = {"buildings": op["buildings"], "economy": op["economy"],
                     "units": op["units"]}
            own_w = dev_weight(se.verify_opening(own, telem))
            # separation: structural fit vs the other openings of this race
            own_s = dev_weight(se.verify_opening(own, telem), structural_only=True)
            others = [o for o in se.openings_for_race(p.play_race) if o.name != fam]
            other_s = [dev_weight(se.verify_opening(o, telem), structural_only=True)
                       for o in others]
            total += 1
            st = per_family[fam]
            st["n"] += 1
            st["own"] += own_w
            if not other_s or own_s <= min(other_s):
                st["sep_ok"] += 1

    print(f"# Library validation over {total} player-openings\n")
    print(f"{'family':<24} {'n':>3} {'avg-own-dev':>12} {'own-fits-best':>14}")
    for fam in sorted(per_family, key=lambda k: -per_family[k]["n"]):
        s = per_family[fam]
        if not s["n"]:
            continue
        print(f"{fam:<24} {s['n']:>3} {s['own']/s['n']:>12.1f} "
              f"{100*s['sep_ok']//s['n']:>13}%")
    sep = sum(s["sep_ok"] for s in per_family.values())
    print(f"\nseparation: own family fit best (or tied) for {sep}/{total} "
          f"({100*sep//max(1,total)}%) openings")


if __name__ == "__main__":
    main()
