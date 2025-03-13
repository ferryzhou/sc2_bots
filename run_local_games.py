from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
import sc2

# Import your bots
from han.han import HanBot
from lishimin.lishimin import LiShiMinBot

def main():
    # Create the map
    map_name = "CatalystLE"  # You can change this to any other map

    # Create the players
    player1 = Bot(Race.Terran, HanBot())
    player2 = Bot(Race.Protoss, LiShiMinBot())

    # Run the game
    run_game(
        maps.get(map_name),
        [player1, player2],
        realtime=False,  # Set to True if you want to watch in real-time
        save_replay_as="replays/han_vs_lishimin.SC2Replay"
    )

if __name__ == "__main__":
    main()
