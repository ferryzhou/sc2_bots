"""Run a local game against the FourGateZealotBot sparring partner.

Purpose: reproduce a loss to a 4-gate zealot rush so you can test defenses,
without the opponent's source code.

    python sparring/run.py

By default this pits FourGateZealotBot against a Very Hard built-in AI so you can
verify the sparring bot opens with a 4-gate. To reproduce *your* bot's loss,
import your bot and put it in the players list (see the commented example).
"""
import sys
import os

# Allow importing sibling bot packages (lishimin/, phoenix/, ...).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from four_gate_zealot_bot import FourGateZealotBot

# --- your bot under test ----------------------------------------------------
# Reproduce a loss by pitting YOUR bot against the sparring bot, e.g.:
#
#     sys.path.insert(0, os.path.join(<repo>, "lishimin"))
#     from lishimin import LiShiMinBot
#     from multi_pylon import MultiPylonBot
#     me = Bot(Race.Protoss, MultiPylonBot())
#
# For the ares-sc2 bots (phoenix/griffin) import their bot class similarly.
# Here we default to a built-in AI opponent so the file runs out of the box.
sparring = Bot(Race.Protoss, FourGateZealotBot())
opponent = Computer(Race.Protoss, Difficulty.VeryHard)

if __name__ == "__main__":
    run_game(
        maps.get("PersephoneAIE"),   # the map from the analyzed replay; any 1v1 map works
        [sparring, opponent],
        realtime=False,
        disable_fog=False,
        save_replay_as="sparring_4gate.SC2Replay",
    )
