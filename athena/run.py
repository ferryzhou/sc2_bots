"""Run AthenaBot locally (headless) or on the AI Arena ladder.

    python run.py                                   # vs Zerg VeryHard, random map
    python run.py --race protoss --difficulty CheatVision --map PylonAIE
    python run.py --LadderServer ...                # ladder (used by harness/versus.py)
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

from main import AthenaBot

DIFFS = {
    "Easy": Difficulty.Easy, "Medium": Difficulty.Medium, "Hard": Difficulty.Hard,
    "VeryHard": Difficulty.VeryHard, "CheatVision": Difficulty.CheatVision,
    "CheatMoney": Difficulty.CheatMoney, "CheatInsane": Difficulty.CheatInsane,
}
RACES = {"protoss": Race.Protoss, "terran": Race.Terran, "zerg": Race.Zerg, "random": Race.Random}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--race", default="zerg")
    p.add_argument("--difficulty", default="VeryHard")
    p.add_argument("--map", default=None)
    p.add_argument("--save-replay", default=None)
    p.add_argument("--build", default=None,
                   help="reproduce a spawningtool build id for the opening "
                        "(a Protoss build ingested into build_guides, e.g. 203087)")
    args, _ = p.parse_known_args()

    ai = AthenaBot()
    ai.force_build_id = args.build
    bot = Bot(Race.Protoss, ai)

    if "--LadderServer" in sys.argv:
        # lazy import: only needed on the ladder (griffin's helper matches this sc2)
        sys.path.insert(0, str(ROOT.parent / "griffin"))
        from ladder import run_ladder_game  # noqa: E402
        run_ladder_game(bot)
        return

    map_pool = ["PylonAIE", "PersephoneAIE", "LeyLinesAIE"]
    map_name = args.map or random.choice(map_pool)
    run_game(
        maps.get(map_name),
        [bot, Computer(RACES[args.race], DIFFS[args.difficulty])],
        realtime=False,
        save_replay_as=args.save_replay,
    )


if __name__ == "__main__":
    main()
