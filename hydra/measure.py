"""Measure HydraBot's level over N games vs the built-in AI and print a table.

    python measure.py --games 10
    python measure.py --games 6 --strategy TurtleHive --lock   # test one strategy

Runs headless games across a spread of races/difficulties, writes per-game
results, and prints a win-rate summary. For games vs downloaded AI Arena bots use
harness/versus.py --bot hydra (the real ladder path).
"""
import argparse
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from bot.main import HydraBot

DIFF = {"Easy": Difficulty.Easy, "Medium": Difficulty.Medium, "Hard": Difficulty.Hard,
        "VeryHard": Difficulty.VeryHard, "CheatVision": Difficulty.CheatVision}
RACES = {"protoss": Race.Protoss, "terran": Race.Terran, "zerg": Race.Zerg}

DEFAULT_SCHEDULE = [
    ("terran", "Medium"), ("protoss", "Medium"), ("zerg", "Medium"),
    ("terran", "Hard"), ("protoss", "Hard"), ("zerg", "Hard"),
    ("terran", "VeryHard"), ("protoss", "VeryHard"), ("zerg", "VeryHard"),
    ("terran", "CheatVision"),
]


def installed_maps():
    sc2_path = os.environ.get("SC2PATH", os.path.expanduser("~/StarCraftII"))
    pool_file = ROOT.parent / "harness" / "map_pool.txt"
    installed = [p.stem for p in (Path(sc2_path) / "Maps").glob("*.SC2Map")]
    if pool_file.is_file():
        verified = [m for m in pool_file.read_text().split() if m in installed]
        if verified:
            return verified
    return installed or ["PylonAIE"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--games", type=int, default=10)
    p.add_argument("--strategy", default=None)
    p.add_argument("--lock", action="store_true")
    p.add_argument("--difficulty", default=None, help="override: play only this difficulty")
    args = p.parse_args()

    schedule = DEFAULT_SCHEDULE[: args.games]
    if args.difficulty:
        schedule = [(r, args.difficulty) for r, _ in schedule]
    pool = installed_maps()
    results = []
    for i, (race, diff) in enumerate(schedule):
        map_name = pool[i % len(pool)]
        bot = Bot(Race.Zerg, HydraBot(strategy=args.strategy, lock=args.lock))
        try:
            res = run_game(
                maps.get(map_name),
                [bot, Computer(RACES[race], DIFF[diff])],
                realtime=False,
            )
        except Exception as exc:  # noqa: BLE001
            res = f"ERROR:{exc}"
        results.append((race, diff, map_name, str(res)))
        print(f"[{i+1}/{len(schedule)}] vs {race:<7} {diff:<11} on {map_name:<16} -> {res}")

    wins = sum(1 for *_, r in results if "Victory" in r)
    print(f"\n=== SUMMARY: {wins}/{len(results)} wins ===")
    for race, diff, mp, r in results:
        tag = "W" if "Victory" in r else ("T" if "Tie" in r else "L")
        print(f"  [{tag}] {race:<7} {diff:<11} {mp:<16} {r.split('.')[-1]}")


if __name__ == "__main__":
    main()
