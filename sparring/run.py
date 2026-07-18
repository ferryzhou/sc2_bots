"""Run a local game against a sparring partner (a replay-derived mimic).

Purpose: reproduce a loss to a specific opponent style so you can test defenses,
without the opponent's source code.

    python sparring/run.py                 # 4-gate zealot (default), vs Very Hard AI
    python sparring/run.py --bot massling  # mass-ling Zerg
    python sparring/run.py --map LeyLinesAIE

By default the sparring bot plays a Very Hard built-in AI so you can verify the
opening. To reproduce *your* bot's loss, import your bot and put it in the
players list (see the commented example).
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from four_gate_zealot_bot import FourGateZealotBot
from mass_ling_bot import MassLingBot
from twelve_pool_bot import TwelvePoolBot

SPARRING = {
    "fourgate": (FourGateZealotBot, Race.Protoss),
    "massling": (MassLingBot, Race.Zerg),
    "twelvepool": (TwelvePoolBot, Race.Zerg),
}

parser = argparse.ArgumentParser()
parser.add_argument("--bot", default="fourgate", choices=sorted(SPARRING))
parser.add_argument("--map", default="PersephoneAIE")
parser.add_argument("--opponent-race", default="Protoss")
args = parser.parse_args()

bot_cls, race = SPARRING[args.bot]
sparring = Bot(race, bot_cls())

# --- your bot under test ----------------------------------------------------
# Reproduce a loss by replacing this Computer with YOUR bot, e.g.:
#     sys.path.insert(0, os.path.join(<repo>, "lishimin"))
#     from multi_pylon import MultiPylonBot
#     opponent = Bot(Race.Protoss, MultiPylonBot())
opponent = Computer(Race[args.opponent_race], Difficulty.VeryHard)

if __name__ == "__main__":
    run_game(
        maps.get(args.map),
        [sparring, opponent],
        realtime=False,
        disable_fog=False,
        save_replay_as=f"sparring_{args.bot}.SC2Replay",
    )
