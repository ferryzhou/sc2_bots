"""Run PhoenixBot against downloaded AI Arena bots, exactly like the ladder.

For each match this launches two headless SC2 instances, creates a 2-slot
game on the first, then starts BOTH bots as external ladder-client
subprocesses (ours via phoenix/run.py --LadderServer, the opponent from its
extracted zip) that join with the standard StartPort port convention. This
exercises our real ladder entrypoint.

Usage:
    python harness/versus.py --opponent MicroMachine --games 2
    python harness/versus.py --list            # show downloaded opponents
"""

import argparse
import asyncio
import json
import random
import re
import socket
import sys
import time
from datetime import datetime
from os import environ
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOT_DIR = REPO_ROOT / "phoenix"
BOTS_DIR = Path(environ.get("ARENA_BOTS_DIR", "/root/arena_bots"))
MANIFEST = REPO_ROOT / "results" / "opponents.json"
HISTORY = REPO_ROOT / "results" / "history.jsonl"
MAP_POOL_FILE = REPO_ROOT / "harness" / "map_pool.txt"

PY312 = environ.get("LADDER_PYTHON", "/root/venv312/bin/python")

sys.path.insert(0, str(BOT_DIR))

from sc2 import maps
from sc2.data import PlayerType, Race
from sc2.player import AbstractPlayer
from sc2.sc2process import SC2Process


def find_start_port() -> int:
    """Pick a base so StartPort+1..+5 are all bindable."""
    for _ in range(200):
        base = random.randint(20000, 60000)
        try:
            socks = []
            for off in range(1, 6):
                s = socket.socket()
                s.bind(("127.0.0.1", base + off))
                socks.append(s)
            for s in socks:
                s.close()
            return base
        except OSError:
            for s in socks:
                s.close()
    raise RuntimeError("no free port range found")


def opponent_command(bot_dir: Path) -> tuple[list[str], Path]:
    """Build the launch command from the bot's ladderbots.json."""
    meta_path = bot_dir / "ladderbots.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        (name, info), = meta["Bots"].items()
        root = bot_dir / info.get("RootPath", ".")
        file_name = info["FileName"]
        bot_type = info["Type"].lower()
    else:  # fall back: python bot with run.py at root
        root, file_name, bot_type = bot_dir, "run.py", "python"

    if bot_type == "python":
        return [PY312, file_name], root
    if bot_type == "cpplinux":
        binary = root / file_name
        binary.chmod(0o755)
        return [str(binary)], root
    raise ValueError(f"unsupported bot type: {bot_type}")


async def run_match(opponent: dict, map_name: str, timeout: int) -> dict:
    opp_dir = BOTS_DIR / opponent["name"]
    opp_cmd, opp_cwd = opponent_command(opp_dir)

    record = {
        "mode": "versus",
        "opponent_name": opponent["name"],
        "opponent_race": opponent["race"],
        "opponent_type": opponent["type"],
        "opponent_elo": opponent.get("elo"),
        "map": map_name,
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    wall_start = time.time()

    async with SC2Process(fullscreen=False) as ctrl_a:
        async with SC2Process(fullscreen=False) as ctrl_b:
            await ctrl_a.ping()
            await ctrl_b.ping()
            # race here is a placeholder - create_game only encodes the
            # participant type; each bot declares its race at join_game
            players = [
                AbstractPlayer(PlayerType.Participant, Race.Protoss),
                AbstractPlayer(PlayerType.Participant, Race.Protoss),
            ]
            await ctrl_a.create_game(maps.get(map_name), players, realtime=False)

            start_port = find_start_port()
            common = ["--LadderServer", "127.0.0.1",
                      "--StartPort", str(start_port)]
            our_cmd = [PY312, "run.py", "--GamePort", str(ctrl_a._process._port),
                       "--OpponentId", opponent["name"], *common]
            their_cmd = [*opp_cmd, "--GamePort", str(ctrl_b._process._port),
                         "--OpponentId", "PhoenixBot", *common]

            log_dir = REPO_ROOT / "results" / "versus_logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%H%M%S")
            opp_log = open(log_dir / f"{opponent['name']}_{stamp}.log", "wb")

            ours = await asyncio.create_subprocess_exec(
                *our_cmd, cwd=BOT_DIR,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            theirs = await asyncio.create_subprocess_exec(
                *their_cmd, cwd=opp_cwd,
                stdout=opp_log, stderr=asyncio.subprocess.STDOUT)

            try:
                out, _ = await asyncio.wait_for(ours.communicate(), timeout=timeout)
                text = out.decode(errors="replace")
                (log_dir / f"PhoenixBot_{stamp}.log").write_text(text)
                m = re.search(r"Result\.(\w+)", text)
                record["result"] = m.group(1) if m else "Unknown"
                if record["result"] == "Unknown" and ours.returncode != 0:
                    record["result"] = "Error"
                    record["error"] = text[-800:]
            except asyncio.TimeoutError:
                record["result"] = "Error"
                record["error"] = f"wall timeout after {timeout}s"
                ours.kill()
            finally:
                if theirs.returncode is None:
                    theirs.kill()
                await theirs.wait()
                opp_log.close()

    record["wall_seconds"] = round(time.time() - wall_start, 1)
    return record


def load_opponents() -> list[dict]:
    if not MANIFEST.is_file():
        sys.exit(f"No manifest at {MANIFEST} - run harness/download_bots.py")
    return json.loads(MANIFEST.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--opponent", help="opponent bot name from the manifest")
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--map", default=None)
    parser.add_argument("--timeout", type=int, default=2400)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    opponents = load_opponents()
    if args.list:
        for o in sorted(opponents, key=lambda x: x.get("elo") or 0, reverse=True):
            print(f"{o['name']:<24} {o['race']} {o['type']:<9} "
                  f"elo={o.get('elo')} active={o.get('active')}")
        return

    by_name = {o["name"]: o for o in opponents}
    if args.opponent not in by_name:
        sys.exit(f"Unknown opponent {args.opponent!r} - use --list")
    opponent = by_name[args.opponent]

    map_pool = (MAP_POOL_FILE.read_text().split()
                if MAP_POOL_FILE.is_file() else [])
    for i in range(args.games):
        map_name = args.map or random.choice(map_pool)
        record = asyncio.run(run_match(opponent, map_name, args.timeout))
        record["git_sha"] = "versus"
        with open(HISTORY, "a") as f:
            f.write(json.dumps(record) + "\n")
        print(f"[{i + 1}/{args.games}] {record.get('result'):<8} "
              f"vs {opponent['name']} (elo {opponent.get('elo')}) "
              f"on {map_name} ({record['wall_seconds']}s wall)")
        if record.get("error"):
            print("    error:", record["error"][:300])


if __name__ == "__main__":
    main()
