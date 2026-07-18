"""Play a repo bot one game vs EVERY downloaded AI Arena opponent, then summarize
which bots it reliably beats and loses to.

This operationalizes the deterministic-opponent framework (OPPONENTS.md): the
ladder field is fixed and knowable, and matchups are ~binary, so a one-game-each
sweep tells you exactly where effort converts into wins.

    python harness/field_measure.py --bot athena --timeout 600

Appends per-game results to results/history_<bot>.jsonl (via versus.py) and
prints a per-opponent W/L table grouped by race. Resumable: skips opponents
already recorded in this run's fresh history file.
"""
import argparse
import json
import subprocess
import sys
from os import environ
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BOTS_DIR = Path(environ.get("ARENA_BOTS_DIR", "/root/arena_bots"))
PY312 = environ.get("LADDER_PYTHON", "/root/venv312/bin/python")


def opponents():
    names = []
    for d in sorted(BOTS_DIR.iterdir()) if BOTS_DIR.is_dir() else []:
        if d.is_dir() and not d.name.startswith("."):
            names.append(d.name)
    return names


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bot", default="athena")
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--maps", default=None, help="optional comma-separated map override")
    args = p.parse_args()

    hist = REPO / "results" / f"history_{args.bot}.jsonl"
    hist.unlink(missing_ok=True)  # fresh sweep

    names = opponents()
    print(f"sweeping {args.bot} vs {len(names)} opponents (1 game each, {args.timeout}s cap)\n")
    for i, name in enumerate(names):
        cmd = [PY312, "harness/versus.py", "--bot", args.bot, "--opponent", name,
               "--games", "1", "--timeout", str(args.timeout)]
        if args.maps:
            cmd += ["--map", args.maps.split(",")[i % len(args.maps.split(","))]]
        print(f"[{i+1}/{len(names)}] vs {name} ...", flush=True)
        try:
            subprocess.run(cmd, cwd=REPO, timeout=args.timeout + 300,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            print(f"    {name}: process timeout")

    summarize(hist)


def _tag(r):
    res = r["result"]
    if "Victory" in res:
        return "W"
    if "Tie" in res:
        return "T"
    if res == "Error":
        return "E"          # never launched / harness or dependency failure
    return "L"


def summarize(hist):
    if not hist.is_file():
        print("no results")
        return
    rows = [json.loads(l) for l in hist.read_text().splitlines() if l.strip()]
    tags = [_tag(r) for r in rows]
    w, l, e = tags.count("W"), tags.count("L"), tags.count("E")
    decisive = w + l + tags.count("T")
    # Decisive record excludes matches that never happened (Error), so the win
    # rate reflects play, not the launchability of the downloaded field.
    print(f"\n=== FIELD RESULTS: {w}-{l} decisive ({w}/{decisive}); "
          f"{e} did-not-launch of {len(rows)} total ===\n")
    by_race = {}
    for r in rows:
        by_race.setdefault(r.get("opponent_race", "?"), []).append(r)
    for race in sorted(by_race):
        rs = by_race[race]
        rw = sum(_tag(r) == "W" for r in rs)
        rd = sum(_tag(r) in ("W", "L", "T") for r in rs)
        print(f"vs {race}: {rw}/{rd} decisive")
        for r in sorted(rs, key=lambda x: x.get("opponent_elo") or 0, reverse=True):
            tag = _tag(r)
            elo = r.get("opponent_elo")
            extra = ""
            if tag == "E":
                extra = "  " + (r.get("error", "").split(": ", 1)[-1][:60])
            print(f"   [{tag}] {r['opponent_name']:<20} elo={elo if elo else '   -'} "
                  f"({round(r['wall_seconds'])}s){extra}")


if __name__ == "__main__":
    main()
