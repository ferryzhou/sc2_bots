"""Run a gauntlet of headless games and maintain a persistent scoreboard.

Each game runs in its own subprocess (one SC2 instance per game) via
play_one.py. Results append to results/history_<bot>.jsonl (one file per
bot, so concurrent runs for different bots never contend) and a
per-matchup summary prints at the end.

Examples:
    python harness/gauntlet.py --games 6 --concurrency 2
    python harness/gauntlet.py --games 12 --difficulties CheatVision,CheatInsane
    python harness/gauntlet.py --summary-only          # re-print scoreboard
"""

import argparse
import itertools
import json
import random
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime
from os import environ
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAY_ONE = REPO_ROOT / "harness" / "play_one.py"
RESULTS_DIR = REPO_ROOT / "results"
# maps verified compatible with ares + the 4.10 linux client (see README)
MAP_POOL_FILE = REPO_ROOT / "harness" / "map_pool.txt"

WIN, LOSS, TIE = "Victory", "Defeat", "Tie"


def history_path(bot: str) -> Path:
    return RESULTS_DIR / f"history_{bot}.jsonl"


def load_all_history() -> list[dict]:
    """All records across every bot's history file."""
    records: list[dict] = []
    for path in sorted(RESULTS_DIR.glob("history_*.jsonl")):
        records += [json.loads(line) for line in path.read_text().splitlines()]
    return records


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def available_maps() -> list[str]:
    sc2_path = Path(environ.get("SC2PATH", Path.home() / "StarCraftII"))
    installed = sorted(p.stem for p in (sc2_path / "Maps").glob("*.SC2Map"))
    if MAP_POOL_FILE.is_file():
        verified = MAP_POOL_FILE.read_text().split()
        pool = [m for m in verified if m in installed]
        if pool:
            return pool
    return installed


def build_matchups(args) -> list[dict]:
    races = args.races.split(",")
    difficulties = args.difficulties.split(",")
    maps_pool = args.maps.split(",") if args.maps else available_maps()
    if not maps_pool:
        sys.exit("No maps found - run scripts/setup_env.sh first")

    combos = itertools.cycle(itertools.product(races, difficulties))
    rng = random.Random(args.seed)
    return [
        {
            "bot": args.bot,
            "race": race,
            "difficulty": difficulty,
            "map": rng.choice(maps_pool),
        }
        for race, difficulty in itertools.islice(combos, args.games)
    ]


def play(matchup: dict, wall_timeout: int) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        result_file = tf.name
    cmd = [
        sys.executable,
        str(PLAY_ONE),
        "--bot", matchup["bot"],
        "--map", matchup["map"],
        "--race", matchup["race"],
        "--difficulty", matchup["difficulty"],
        "--result-file", result_file,
    ]
    record = dict(matchup)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=wall_timeout
        )
        payload = Path(result_file).read_text().strip()
        if payload:
            record = json.loads(payload)
        else:
            record["result"] = "Error"
            record["error"] = (proc.stderr or proc.stdout)[-800:]
    except subprocess.TimeoutExpired:
        record["result"] = "Error"
        record["error"] = f"wall timeout after {wall_timeout}s"
    except Exception as exc:  # noqa: BLE001
        record["result"] = "Error"
        record["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        Path(result_file).unlink(missing_ok=True)
    return record


def outcome_char(result: str) -> str:
    return {WIN: "W", LOSS: "L", TIE: "T"}.get(result, "E")


def print_summary(records: list[dict], title: str) -> None:
    by_matchup: dict[tuple, list[str]] = defaultdict(list)
    for r in records:
        # records predating multi-bot support are all phoenix; versus-mode
        # records have an opponent bot name instead of a difficulty
        key = (r.get("bot", "phoenix"),
               r.get("opponent_race") or r.get("race") or "?",
               r.get("difficulty") or r.get("opponent_name") or "?")
        by_matchup[key].append(r.get("result", "Error"))

    print(f"\n=== {title} ===")
    print(f"{'bot':<9} {'opponent':<12} {'difficulty':<14} {'games':>5} "
          f"{'wins':>5} {'winrate':>8}  record")
    total_games = total_wins = 0
    for (bot, race, diff), results in sorted(by_matchup.items()):
        wins = results.count(WIN)
        total_games += len(results)
        total_wins += wins
        chars = "".join(outcome_char(r) for r in results)
        print(f"{bot:<9} {race:<12} {diff:<14} {len(results):>5} {wins:>5} "
              f"{wins / len(results):>7.0%}  {chars}")
    if total_games:
        print(f"{'TOTAL':<9} {'':<12} {'':<14} {total_games:>5} {total_wins:>5} "
              f"{total_wins / total_games:>7.0%}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot", default="phoenix",
                        choices=["phoenix", "griffin", "aegis"],
                        help="which repo bot to evaluate")
    parser.add_argument("--games", type=int, default=6)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--races", default="zerg,terran,protoss")
    parser.add_argument("--difficulties", default="CheatVision")
    parser.add_argument("--maps", default=None, help="comma-separated, default: all installed")
    parser.add_argument("--wall-timeout", type=int, default=1800,
                        help="max wall-clock seconds per game")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--summary-only", action="store_true",
                        help="print scoreboard from results/history_*.jsonl and exit")
    args = parser.parse_args()

    if args.summary_only:
        records = load_all_history()
        if not records:
            sys.exit(f"No history_*.jsonl files in {RESULTS_DIR}")
        print_summary(records, f"All-time scoreboard ({RESULTS_DIR}/history_*.jsonl)")
        return

    matchups = build_matchups(args)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    sha = git_sha()
    print(f"Gauntlet {run_id} @ {sha}: {len(matchups)} games, "
          f"concurrency {args.concurrency}")

    RESULTS_DIR.mkdir(exist_ok=True)
    records: list[dict] = []
    from concurrent.futures import ThreadPoolExecutor, as_completed

    start = time.time()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(play, m, args.wall_timeout): i
            for i, m in enumerate(matchups)
        }
        for future in as_completed(futures):
            record = future.result()
            record["run_id"] = run_id
            record["git_sha"] = sha
            records.append(record)
            with open(history_path(args.bot), "a") as f:
                f.write(json.dumps(record) + "\n")
            n = len(records)
            print(f"[{n}/{len(matchups)}] {record.get('result', '?'):<8} "
                  f"vs {record.get('opponent_race', '?'):<8} "
                  f"{record.get('difficulty', '?'):<13} "
                  f"on {record.get('map', '?'):<22} "
                  f"({record.get('game_time', '?')}s game, "
                  f"{record.get('wall_seconds', '?')}s wall)")
            if record.get("result") == "Error":
                print(f"    error: {record.get('error', '?')[:200]}")

    print(f"\nWall time: {time.time() - start:.0f}s")
    print_summary(records, f"Run {run_id}")

    print_summary(load_all_history(), "All-time scoreboard")


if __name__ == "__main__":
    main()
