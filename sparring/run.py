"""Run a sparring partner locally (vs built-in AI) or as a ladder client.

Purpose: reproduce a loss to a specific opponent style so you can test defenses,
without the opponent's source code.

    python sparring/run.py                 # 4-gate zealot (default), vs Very Hard AI
    python sparring/run.py --bot massling  # mass-ling Zerg
    python sparring/run.py --bot random    # Random race, random archetype
    python sparring/run.py --map LeyLinesAIE

Ladder-client mode (used by harness/versus.py to play downloaded AI Arena
bots): any --LadderServer invocation joins an external game instead. The
sparring bot to field defaults to "random"; set SPARRING_BOT=<key> to
override (versus.py passes no custom args through).

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

from archetype_bot import (FourGate2, GreedyProtoss2, GreedyTerran2, GreedyZerg2,
                           MassLing2, OneBaseStalker2, TwelvePool2)
from four_gate_zealot_bot import FourGateZealotBot
from mass_ling_bot import MassLingBot
from random_race_bot import RandomSparringBot
from twelve_pool_bot import TwelvePoolBot

SPARRING = {
    "fourgate": (FourGateZealotBot, Race.Protoss),
    "massling": (MassLingBot, Race.Zerg),
    "twelvepool": (TwelvePoolBot, Race.Zerg),
    # strategy_engine-driven recreations (archetype_bot.py)
    "fourgate2": (FourGate2, Race.Protoss),
    "massling2": (MassLing2, Race.Zerg),
    "twelvepool2": (TwelvePool2, Race.Zerg),
    "onebasestalker2": (OneBaseStalker2, Race.Protoss),
    "greedyp": (GreedyProtoss2, Race.Protoss),
    "greedyt": (GreedyTerran2, Race.Terran),
    "greedyz": (GreedyZerg2, Race.Zerg),
    # Random race + random archetype of that race (random_race_bot.py)
    "random": (RandomSparringBot, Race.Random),
}


def main():
    if "--LadderServer" in sys.argv:
        bot_cls, race = SPARRING[os.environ.get("SPARRING_BOT", "random")]
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.join(repo_root, "griffin"))
        from ladder import run_ladder_game
        print("Starting ladder game...")
        result, opponent_id = run_ladder_game(Bot(race, bot_cls()))
        print(result, " against opponent ", opponent_id)
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--bot", default="fourgate", choices=sorted(SPARRING))
    parser.add_argument("--map", default="PersephoneAIE")
    parser.add_argument("--opponent-race", default="Protoss")
    args = parser.parse_args()

    bot_cls, race = SPARRING[args.bot]
    sparring = Bot(race, bot_cls())

    # --- your bot under test --------------------------------------------
    # Reproduce a loss by replacing this Computer with YOUR bot, e.g.:
    #     sys.path.insert(0, os.path.join(<repo>, "lishimin"))
    #     from multi_pylon import MultiPylonBot
    #     opponent = Bot(Race.Protoss, MultiPylonBot())
    opponent = Computer(Race[args.opponent_race], Difficulty.VeryHard)

    run_game(
        maps.get(args.map),
        [sparring, opponent],
        realtime=False,
        disable_fog=False,
        save_replay_as=f"sparring_{args.bot}.SC2Replay",
    )


if __name__ == "__main__":
    main()
