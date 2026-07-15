"""Run HydraBot locally (headless) or on the AI Arena ladder.

    python run.py                                  # vs Terran VeryHard, random map
    python run.py --race zerg --difficulty CheatVision --map PylonAIE
    python run.py --strategy TurtleHive --lock      # force a single strategy
    python run.py --LadderServer ...                # ladder (harness/versus.py)
"""
import argparse
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))  # repo root for strategy_engine

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from bot.main import HydraBot

DIFFS = {
    "Easy": Difficulty.Easy, "Medium": Difficulty.Medium, "Hard": Difficulty.Hard,
    "VeryHard": Difficulty.VeryHard, "CheatVision": Difficulty.CheatVision,
    "CheatMoney": Difficulty.CheatMoney, "CheatInsane": Difficulty.CheatInsane,
}
RACES = {"protoss": Race.Protoss, "terran": Race.Terran, "zerg": Race.Zerg,
         "random": Race.Random}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--race", default="terran")
    p.add_argument("--difficulty", default="VeryHard")
    p.add_argument("--map", default=None)
    p.add_argument("--strategy", default=None, help="force a starting strategy")
    p.add_argument("--lock", action="store_true", help="disable mid-game switching")
    p.add_argument("--save-replay", default=None)
    args, _ = p.parse_known_args()

    bot = Bot(Race.Zerg, HydraBot(strategy=args.strategy, lock=args.lock))

    if "--LadderServer" in sys.argv:
        sys.path.insert(0, str(ROOT.parent / "griffin"))
        from ladder import run_ladder_game  # noqa: E402
        run_ladder_game(bot)
        return

    def installed_maps():
        sc2_path = os.environ.get("SC2PATH", os.path.expanduser("~/StarCraftII"))
        return [p.stem for p in (Path(sc2_path) / "Maps").glob("*.SC2Map")]

    pool = installed_maps() or ["PylonAIE"]
    map_name = args.map or random.choice(pool)
    run_game(
        maps.get(map_name),
        [bot, Computer(RACES[args.race], DIFFS[args.difficulty])],
        realtime=False,
        save_replay_as=args.save_replay,
    )


if __name__ == "__main__":
    main()
