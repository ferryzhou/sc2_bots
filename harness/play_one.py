"""Play a single headless game and write a structured JSON result file.

Designed to be invoked as a subprocess by gauntlet.py (one SC2 instance per
process), but works standalone too:

    python harness/play_one.py --map PylonAIE --race zerg \
        --difficulty CheatVision --result-file /tmp/result.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOT_DIR = REPO_ROOT / "phoenix"
sys.path.insert(0, str(BOT_DIR))

# ares reads config.yml / protoss_builds.yml from the working directory
os.chdir(BOT_DIR)

from sc2 import maps
from sc2.data import AIBuild, Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from bot.main import PhoenixBot

# filled in by HarnessBot.on_end, read after run_game returns
_game_stats: dict = {}


class HarnessBot(PhoenixBot):
    async def on_end(self, game_result) -> None:
        _game_stats["game_time"] = round(self.time, 1)
        _game_stats["workers"] = self.workers.amount
        _game_stats["bases"] = self.townhalls.amount
        _game_stats["army_supply"] = round(
            self.supply_used - self.supply_workers, 1
        )
        await super(HarnessBot, self).on_end(game_result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", required=True)
    parser.add_argument(
        "--race", default="zerg", choices=["zerg", "terran", "protoss", "random"]
    )
    parser.add_argument("--difficulty", default="CheatVision")
    parser.add_argument("--ai-build", default="Macro")
    parser.add_argument("--result-file", required=True)
    parser.add_argument(
        "--game-time-limit",
        type=int,
        default=2400,
        help="in-game seconds before the game is called a Tie",
    )
    parser.add_argument("--replay-dir", default=str(BOT_DIR / "replays" / "harness"))
    args = parser.parse_args()

    replay_dir = Path(args.replay_dir)
    replay_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    replay_path = str(
        replay_dir / f"{args.map}_{args.race}_{args.difficulty}_{stamp}.SC2Replay"
    )

    record = {
        "map": args.map,
        "opponent_race": args.race,
        "difficulty": args.difficulty,
        "ai_build": args.ai_build,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "replay": replay_path,
    }

    wall_start = time.time()
    try:
        result = run_game(
            maps.get(args.map),
            [
                Bot(Race.Protoss, HarnessBot(), "PhoenixBot"),
                Computer(
                    Race[args.race.title()],
                    Difficulty[args.difficulty],
                    ai_build=AIBuild[args.ai_build],
                ),
            ],
            realtime=False,
            save_replay_as=replay_path,
            game_time_limit=args.game_time_limit,
        )
        record["result"] = result.name if result is not None else "Unknown"
    except Exception as exc:  # noqa: BLE001 - report any crash as a result
        import traceback

        record["result"] = "Error"
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc(limit=25)

    record["wall_seconds"] = round(time.time() - wall_start, 1)
    record.update(_game_stats)

    Path(args.result_file).write_text(json.dumps(record))
    print(json.dumps(record))


if __name__ == "__main__":
    main()
