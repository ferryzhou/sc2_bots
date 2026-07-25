"""Measure a repo bot's strength against every playable downloaded opponent.

One command plays N games vs each opponent in results/opponents.json (the
manifest is already filtered to bots verified to run -- see download_bots.py
probe-gating), running games in parallel, then reports: overall and per-race
records, a per-opponent table, a maximum-likelihood Elo estimate from games
vs ranked opponents, and the replays saved for loss analysis.

    python harness/measure_strength.py --bot phoenix
    python harness/measure_strength.py --bot griffin --games 2 --concurrency 3
    python harness/measure_strength.py --bot phoenix --min-elo 1400
    python harness/measure_strength.py --bot phoenix --opponents MicroMachine,who
    python harness/measure_strength.py --bot phoenix --since 2026-07-24T12:00:00
                                        # ^ resume an interrupted run
    python harness/measure_strength.py --bot phoenix --report-only --since ...

Writes <bot>/results/strength_report.md and prints the same summary.
Replays land in <bot>/replays/versus/ with the result in the filename;
loss replays are listed in the report for analysis
(analysis/sc2reader_analyzer.py).
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os import environ
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "results" / "opponents.json"
PY312 = environ.get("LADDER_PYTHON", "/root/venv312/bin/python")

W, L, T = "Victory", "Defeat", "Tie"


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


def mle_elo(games: list[tuple[float, float]]) -> tuple[int, int, int]:
    """Maximum-likelihood Elo from (opponent_elo, score) pairs, score in
    {1, 0.5, 0}. Returns (estimate, lo_bound, hi_bound) where the bounds
    flag an estimate pinned by an all-win/all-loss record."""
    lo, hi = 0.0, 3000.0

    def excess(r: float) -> float:
        return sum(s - 1 / (1 + 10 ** ((e - r) / 400)) for e, s in games)

    for _ in range(60):
        mid = (lo + hi) / 2
        if excess(mid) > 0:
            lo = mid
        else:
            hi = mid
    est = round((lo + hi) / 2)
    elos = [e for e, _ in games]
    return est, round(min(elos) - 400), round(max(elos) + 400)


def summarize(bot: str, since: str, opponents: list[dict]) -> str:
    hist = REPO / bot / "results" / "history.jsonl"
    rows = sweep_records(hist, since)
    by_opp: dict[str, list[dict]] = {}
    for r in rows:
        by_opp.setdefault(r["opponent_name"], []).append(r)

    real = [r for r in rows if r["result"] in (W, L, T)]
    wins = sum(r["result"] == W for r in real)
    ties = sum(r["result"] == T for r in real)
    losses = len(real) - wins - ties
    errors = [r for r in rows if r["result"] not in (W, L, T)]

    lines = [f"# Strength report: {bot}",
             "",
             f"- run started: {since}  ({len(rows)} games, "
             f"{len(by_opp)}/{len(opponents)} opponents)",
             f"- **decisive record: {wins}-{losses}-{ties}"
             + (f" ({wins / max(1, wins + losses):.0%} of W+L)**" if real else "**"),
             f"- opponent errors (crashes, not counted): {len(errors)}"]

    ranked = [(r_["opponent_elo"], {W: 1.0, T: 0.5, L: 0.0}[r_["result"]])
              for r_ in real if r_.get("opponent_elo")]
    if ranked:
        est, floor, ceil = mle_elo(ranked)
        pinned = ("" if floor < est < ceil else
                  " (pinned -- record vs ranked bots is one-sided)")
        lines.append(f"- **Elo estimate: ~{est}**{pinned} "
                     f"(MLE over {len(ranked)} games vs ranked opponents)")

    lines += ["", "## By opponent race", ""]
    for race in "PTZR":
        rs = [r for r in real if r.get("opponent_race") == race]
        if rs:
            rw = sum(r["result"] == W for r in rs)
            lines.append(f"- vs {race}: {rw}/{len(rs)}")

    lines += ["", "## Per opponent", "",
              "| result | opponent | elo | race | wall | replay |",
              "|---|---|---|---|---|---|"]
    elo_of = {o["name"]: o.get("elo") for o in opponents}
    ordered = sorted(by_opp.items(),
                     key=lambda kv: -(elo_of.get(kv[0]) or 0))
    for name, games in ordered:
        for r in games:
            res = r["result"]
            tag = {W: "**W**", L: "L", T: "T"}.get(res, "E")
            replay = Path(r["replay"]).name if r.get("replay") else ""
            lines.append(f"| {tag} | {name} | {elo_of.get(name) or '-'} "
                         f"| {r.get('opponent_race', '?')} "
                         f"| {round(r['wall_seconds'])}s | {replay} |")

    loss_replays = [r["replay"] for r in real
                    if r["result"] == L and r.get("replay")]
    if loss_replays:
        lines += ["", "## Loss replays (feed to analysis/sc2reader_analyzer.py)",
                  ""] + [f"- {p}" for p in loss_replays]
    if errors:
        lines += ["", "## Opponent errors", ""]
        lines += [f"- {r['opponent_name']}: {r.get('error', '')[:120]}"
                  for r in errors]
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bot", default="phoenix",
                   help="repo bot to measure (must be in versus.py's registry)")
    p.add_argument("--games", type=int, default=1, help="games per opponent")
    p.add_argument("--concurrency", type=int, default=2,
                   help="parallel matches (each uses two SC2 instances)")
    p.add_argument("--timeout", type=int, default=600,
                   help="wall seconds per game")
    p.add_argument("--min-elo", type=int, default=None,
                   help="only play opponents at/above this current-season Elo")
    p.add_argument("--opponents", default=None,
                   help="comma-separated opponent names (default: all playable)")
    p.add_argument("--since", default=None,
                   help="resume/report a run started at this ISO timestamp")
    p.add_argument("--report-only", action="store_true",
                   help="skip playing; regenerate the report for --since")
    args = p.parse_args()

    opponents = json.loads(MANIFEST.read_text())
    if args.opponents:
        wanted = set(args.opponents.split(","))
        unknown = wanted - {o["name"] for o in opponents}
        if unknown:
            sys.exit(f"not in manifest: {', '.join(sorted(unknown))}")
        opponents = [o for o in opponents if o["name"] in wanted]
    if args.min_elo:
        opponents = [o for o in opponents if (o.get("elo") or 0) >= args.min_elo]
    if not opponents:
        sys.exit("no opponents selected")

    if args.report_only and not args.since:
        sys.exit("--report-only needs --since (the run's printed timestamp)")
    since = args.since or datetime.now().isoformat(timespec="seconds")
    hist = REPO / args.bot / "results" / "history.jsonl"

    if not args.report_only:
        print(f"measuring {args.bot} vs {len(opponents)} opponents, "
              f"{args.games} game(s) each, {args.concurrency} in parallel")
        print(f"resume with: --since {since}\n")

        def played(name: str) -> int:
            return sum(r["opponent_name"] == name
                       for r in sweep_records(hist, since))

        jobs = [o["name"] for o in opponents
                for _ in range(max(0, args.games - played(o["name"])))]

        def play(name: str) -> str:
            try:
                subprocess.run(
                    [PY312, "harness/versus.py", "--bot", args.bot,
                     "--opponent", name, "--games", "1",
                     "--timeout", str(args.timeout)],
                    cwd=REPO, timeout=args.timeout + 300,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.TimeoutExpired:
                return "Timeout"
            recs = [r for r in sweep_records(hist, since)
                    if r["opponent_name"] == name]
            return recs[-1]["result"] if recs else "Unknown"

        done = 0
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            for name, result in zip(jobs, pool.map(play, jobs)):
                done += 1
                print(f"[{done}/{len(jobs)}] {result:<8} vs {name}", flush=True)

    report = summarize(args.bot, since, opponents)
    out = REPO / args.bot / "results" / "strength_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    print("\n" + report)
    print(f"report: {out}")
    print(f"replays: {REPO / args.bot / 'replays' / 'versus'}/")


if __name__ == "__main__":
    main()
