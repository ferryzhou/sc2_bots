"""Play a repo bot one game vs EVERY downloaded AI Arena opponent, then summarize
which bots it reliably beats and loses to.

This operationalizes the deterministic-opponent framework (OPPONENTS.md): the
ladder field is fixed and knowable, and matchups are ~binary, so a one-game-each
sweep tells you exactly where effort converts into wins.

    python harness/field_measure.py --bot athena --timeout 600

Appends per-game results to <bot>/results/history.jsonl (via versus.py) and
prints a per-opponent W/L table grouped by race. A sweep is scoped by a start
timestamp: records at/after it count as this sweep, so an interrupted sweep
resumes with --since <printed timestamp> (already-played opponents are
skipped). --shard i/n runs an interleaved slice so multiple processes can
split the field.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
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


def sweep_records(hist: Path, since: str) -> list[dict]:
    if not hist.is_file():
        return []
    rows = []
    for line in hist.read_text().splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("mode") == "versus" and r.get("started_at", "") >= since:
            rows.append(r)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bot", default="athena")
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--maps", default=None, help="optional comma-separated map override")
    p.add_argument("--since", default=None,
                   help="ISO timestamp scoping this sweep (resume an "
                        "interrupted sweep by passing its printed value)")
    p.add_argument("--shard", default=None,
                   help="i/n: play only every n-th opponent starting at i "
                        "(run n processes to split the field)")
    args = p.parse_args()

    hist = REPO / args.bot / "results" / "history.jsonl"
    since = args.since or datetime.now().isoformat(timespec="seconds")
    print(f"sweep scope: --since {since}")

    names = opponents()
    if args.shard:
        i, n = (int(x) for x in args.shard.split("/"))
        names = names[i::n]
    print(f"sweeping {args.bot} vs {len(names)} opponents (1 game each, {args.timeout}s cap)\n")
    for i, name in enumerate(names):
        if name in {r["opponent_name"] for r in sweep_records(hist, since)}:
            print(f"[{i+1}/{len(names)}] vs {name} already recorded, skipping")
            continue
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

    summarize(hist, since)


def _tag(r):
    res = r["result"]
    if "Victory" in res:
        return "W"
    if "Tie" in res:
        return "T"
    if res == "Error":
        return "E"          # never launched / harness or dependency failure
    return "L"


def summarize(hist, since=""):
    rows = sweep_records(hist, since)
    if not rows:
        print("no results")
        return
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
