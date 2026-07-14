"""Measure AthenaBot's level over N games and print a win-rate summary.

    python athena/measure.py --games 10
    python athena/measure.py --games 10 --schedule mixed

Runs headless games against the built-in AI across a schedule of difficulties
(and races), writes per-game results, and prints a table. For games vs.
downloaded AI Arena bots, use harness/versus.py --bot athena (ladder path).
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

from main import AthenaBot

DIFF = {"Easy": Difficulty.Easy, "Medium": Difficulty.Medium, "Hard": Difficulty.Hard,
        "VeryHard": Difficulty.VeryHard, "CheatVision": Difficulty.CheatVision}
RACES = {"protoss": Race.Protoss, "terran": Race.Terran, "zerg": Race.Zerg}
MAP_POOL = ["PylonAIE", "PersephoneAIE", "LeyLinesAIE"]

# a spread that samples the bot's level: easy->hard across all races
DEFAULT_SCHEDULE = [
    ("zerg", "Medium"), ("terran", "Medium"), ("protoss", "Medium"),
    ("zerg", "Hard"), ("terran", "Hard"), ("protoss", "Hard"),
    ("zerg", "VeryHard"), ("terran", "VeryHard"), ("protoss", "VeryHard"),
    ("zerg", "CheatVision"),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--games", type=int, default=10)
    args = p.parse_args()

    schedule = DEFAULT_SCHEDULE[: args.games]
    results = []
    for i, (race, diff) in enumerate(schedule):
        map_name = MAP_POOL[i % len(MAP_POOL)]
        bot = Bot(Race.Protoss, AthenaBot())
        try:
            res = run_game(
                maps.get(map_name),
                [bot, Computer(RACES[race], DIFF[diff])],
                realtime=False,
            )
        except Exception as exc:  # noqa
            res = f"ERROR:{exc}"
        results.append((race, diff, map_name, str(res)))
        print(f"[{i+1}/{len(schedule)}] vs {race:<7} {diff:<11} on {map_name:<14} -> {res}")

    wins = sum(1 for *_, r in results if "Victory" in r)
    print(f"\n=== SUMMARY: {wins}/{len(results)} wins ===")
    for race, diff, mp, r in results:
        tag = "W" if "Victory" in r else ("T" if "Tie" in r else "L")
        print(f"  [{tag}] {race:<7} {diff:<11} {mp:<14} {r.split('.')[-1]}")


if __name__ == "__main__":
    main()
