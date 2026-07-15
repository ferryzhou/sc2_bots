"""Run AegisBot locally (headless) or on the AI Arena ladder.

Local examples:
    python run.py                          # random map, Zerg CheatVision opponent
    python run.py --race protoss --difficulty VeryHard --map PylonAIE
"""

import argparse
import random
import sys
from datetime import datetime
from os import environ, path
from pathlib import Path

# ares reads config.yml from the working directory
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import yaml
from sc2 import maps
from sc2.data import AIBuild, Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from bot.main import AegisBot
from ladder import run_ladder_game

CONFIG_FILE = "config.yml"


def get_maps_dir() -> Path:
    sc2_path = environ.get("SC2PATH", path.expanduser("~/StarCraftII"))
    return Path(sc2_path) / "Maps"


def main():
    import os

    os.chdir(ROOT_DIR)

    bot_name = "AegisBot"
    race = Race.Terran
    config_path = ROOT_DIR / CONFIG_FILE
    if config_path.is_file():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            bot_name = config.get("MyBotName", bot_name)
            race = Race[config.get("MyBotRace", "Terran").title()]

    bot = Bot(race, AegisBot(), bot_name)

    if "--LadderServer" in sys.argv:
        print("Starting ladder game...")
        result, opponent_id = run_ladder_game(bot)
        print(result, " against opponent ", opponent_id)
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default=None, help="map name without extension")
    parser.add_argument(
        "--race",
        default="zerg",
        choices=["zerg", "terran", "protoss", "random"],
        help="opponent computer race",
    )
    parser.add_argument(
        "--difficulty",
        default="CheatVision",
        help="python-sc2 Difficulty name, e.g. VeryHard, CheatVision, CheatInsane",
    )
    parser.add_argument("--realtime", action="store_true")
    args = parser.parse_args()

    map_pool = [
        p.stem for p in get_maps_dir().glob("*.SC2Map") if p.is_file()
    ]
    if not map_pool:
        print(f"No maps found in {get_maps_dir()} - install a ladder map pack.")
        sys.exit(1)
    map_name = args.map or random.choice(map_pool)

    replay_dir = ROOT_DIR / "replays"
    replay_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    replay_path = str(replay_dir / f"{bot_name}_{map_name}_{stamp}.SC2Replay")

    print(f"Starting local game on {map_name} vs {args.race} {args.difficulty}...")
    result = run_game(
        maps.get(map_name),
        [
            bot,
            Computer(
                Race[args.race.title()],
                Difficulty[args.difficulty],
                ai_build=AIBuild.Macro,
            ),
        ],
        realtime=args.realtime,
        save_replay_as=replay_path,
    )
    print(f"Result: {result}")
    print(f"Replay: {replay_path}")


if __name__ == "__main__":
    main()
