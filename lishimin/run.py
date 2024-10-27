# pylint: disable=E0401
import sys

from __init__ import run_ladder_game

# Load bot
from lishimin import LiShiMinBot
from multi_pylon import MultiPylonBot

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

bot = Bot(Race.Protoss, LiShiMinBot())
opponent = Bot(Race.Protoss, MultiPylonBot())

# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponent_id = run_ladder_game(bot)
        print(f"{result} against opponent {opponent_id}")
    else:
        # Local game
        print("Starting local game...")
        run_game(
            maps.get("CatalystLE"),
            #[bot, opponent],
            [bot, Computer(Race.Protoss, Difficulty.VeryHard)],
            realtime=False,
            disable_fog=False,
            save_replay_as="lishimin.SC2Replay"
        )
