"""Run a repo bot against downloaded AI Arena bots, exactly like the ladder.

For each match this launches two headless SC2 instances, creates a 2-slot
game on the first, then starts BOTH bots as external ladder-client
subprocesses (ours via <bot>/run.py --LadderServer, the opponent from its
extracted zip) that join with the standard StartPort port convention. This
exercises our real ladder entrypoint.

Usage:
    python harness/versus.py --opponent MicroMachine --games 2
    python harness/versus.py --bot griffin --opponent MicroMachine
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
BOTS_DIR = Path(environ.get("ARENA_BOTS_DIR", "/root/arena_bots"))
MANIFEST = REPO_ROOT / "results" / "opponents.json"
MAP_POOL_FILE = REPO_ROOT / "harness" / "map_pool.txt"

PY312 = environ.get("LADDER_PYTHON", "/root/venv312/bin/python")

# repo bots with a ladder-capable run.py: dir name -> ladder id
BOT_REGISTRY = {"phoenix": "PhoenixBot", "griffin": "GriffinBot",
                "athena": "AthenaBot", "aegis": "AegisBot"}
# overridden from --bot in main()
BOT_KEY = "phoenix"
BOT_DIR = REPO_ROOT / BOT_KEY
BOT_NAME = BOT_REGISTRY[BOT_KEY]

from aiohttp import WSMsgType, web
from sc2 import maps
from sc2.data import PlayerType, Race
from sc2.player import AbstractPlayer
from sc2.sc2process import SC2Process


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def start_relay(sc2_ws, port: int) -> web.AppRunner:
    """Proxy one bot's websocket onto an existing SC2 connection.

    SC2 accepts a single websocket client, and the match manager already
    holds it (it needed it for create_game). Real ladder managers solve
    this by proxying - bots connect to the manager's port and frames are
    relayed 1:1 over the manager's SC2 connection. GamePort therefore
    points at this relay, not at SC2 itself.
    """

    async def handler(request: web.Request) -> web.WebSocketResponse:
        bot_ws = web.WebSocketResponse(max_msg_size=0)
        await bot_ws.prepare(request)
        async for msg in bot_ws:
            if msg.type != WSMsgType.BINARY:
                break
            await sc2_ws.send_bytes(msg.data)
            resp = await sc2_ws.receive()
            if resp.type != WSMsgType.BINARY:
                break
            await bot_ws.send_bytes(resp.data)
        return bot_ws

    app = web.Application()
    app.router.add_route("GET", "/sc2api", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()
    return runner


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


def opponent_command(bot_dir: Path, bot_name: str) -> tuple[list[str], Path]:
    """Build the launch command from the bot's zip layout.

    Layouts seen in the wild: ladderbots.json at the root or one level
    down (Type spellings vary: Python, cppLinux, BinaryCpp); a plain
    python bot with run.py at the root; or just a bare executable named
    after the bot, possibly nested one directory deep.
    """
    candidates = [bot_dir / "ladderbots.json",
                  *sorted(bot_dir.glob("*/ladderbots.json"))]
    for meta_path in candidates:
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text())
        (name, info), = meta["Bots"].items()
        root = (meta_path.parent / info.get("RootPath", ".")).resolve()
        file_name = info["FileName"]
        bot_type = info["Type"].lower()
        if "python" in bot_type:
            return [PY312, file_name], root
        if "cpp" in bot_type or "binary" in bot_type:
            binary = root / file_name
            binary.chmod(0o755)
            return [str(binary)], root
        raise ValueError(f"unsupported bot type: {bot_type}")

    if (bot_dir / "run.py").is_file():
        return [PY312, "run.py"], bot_dir

    for binary in (bot_dir / bot_name, bot_dir / bot_name / bot_name):
        if binary.is_file():
            binary.chmod(0o755)
            return [str(binary)], binary.parent

    raise ValueError(f"no launch spec found in {bot_dir}")


async def run_match(opponent: dict, map_name: str, timeout: int) -> dict:
    opp_dir = BOTS_DIR / opponent["name"]
    opp_cmd, opp_cwd = opponent_command(opp_dir, opponent["name"])

    record = {
        "mode": "versus",
        "bot": BOT_KEY,
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

            # relay each bot onto the manager's SC2 connections
            proxy_a, proxy_b = free_port(), free_port()
            relay_a = await start_relay(ctrl_a._ws, proxy_a)
            relay_b = await start_relay(ctrl_b._ws, proxy_b)

            start_port = find_start_port()
            common = ["--LadderServer", "127.0.0.1",
                      "--StartPort", str(start_port)]
            our_cmd = [PY312, "run.py", "--GamePort", str(proxy_a),
                       "--OpponentId", opponent["name"], *common]
            their_cmd = [*opp_cmd, "--GamePort", str(proxy_b),
                         "--OpponentId", BOT_NAME, *common]

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
                # fast-fail: an opponent that dies in the first 25s never
                # joined - don't burn the full match timeout waiting
                try:
                    await asyncio.wait_for(theirs.wait(), timeout=25)
                    record["result"] = "Error"
                    record["error"] = (f"opponent exited at launch "
                                       f"(rc={theirs.returncode})")
                    ours.kill()
                    await ours.wait()
                    record["wall_seconds"] = round(time.time() - wall_start, 1)
                    return record
                except asyncio.TimeoutError:
                    pass

                out, _ = await asyncio.wait_for(ours.communicate(), timeout=timeout)
                text = out.decode(errors="replace")
                (log_dir / f"{BOT_NAME}_{stamp}.log").write_text(text)
                # anchor to real game results - the bot's own logging can
                # contain e.g. "EngagementResult.VICTORY_EMPHATIC"
                m = re.search(r"\bResult\.(Victory|Defeat|Tie)\b", text)
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
                await relay_a.cleanup()
                await relay_b.cleanup()

    record["wall_seconds"] = round(time.time() - wall_start, 1)
    return record


def load_opponents() -> list[dict]:
    """Manifest entries plus any extracted bot dirs missing from it.

    The manifest can be regenerated at any time (and bots leave the
    publicly-downloadable set), but an extracted bot in BOTS_DIR stays
    playable - synthesize an entry from its ladderbots.json when needed.
    """
    manifest = (json.loads(MANIFEST.read_text())
                if MANIFEST.is_file() else [])
    known = {o["name"] for o in manifest}
    for bot_dir in sorted(BOTS_DIR.iterdir()) if BOTS_DIR.is_dir() else []:
        if not bot_dir.is_dir() or bot_dir.name in known:
            continue
        entry = {"name": bot_dir.name, "race": "?", "type": "python",
                 "elo": None, "local_only": True}
        for meta_path in (bot_dir / "ladderbots.json",
                          *sorted(bot_dir.glob("*/ladderbots.json"))):
            if meta_path.is_file():
                try:
                    (name, info), = json.loads(
                        meta_path.read_text())["Bots"].items()
                    entry["race"] = info.get("Race", "?")[:1]
                    entry["type"] = info.get("Type", "python").lower()
                except (ValueError, KeyError):
                    pass
                break
        manifest.append(entry)
    return manifest


def main() -> None:
    global BOT_KEY, BOT_DIR, BOT_NAME

    parser = argparse.ArgumentParser()
    parser.add_argument("--bot", default="phoenix", choices=sorted(BOT_REGISTRY),
                        help="which repo bot to run")
    parser.add_argument("--opponent", help="opponent bot name from the manifest")
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--map", default=None)
    parser.add_argument("--timeout", type=int, default=2400)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    BOT_KEY = args.bot
    BOT_DIR = REPO_ROOT / BOT_KEY
    BOT_NAME = BOT_REGISTRY[BOT_KEY]

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

    # one history file per bot so concurrent runs never contend
    history = REPO_ROOT / "results" / f"history_{BOT_KEY}.jsonl"
    map_pool = (MAP_POOL_FILE.read_text().split()
                if MAP_POOL_FILE.is_file() else [])
    for i in range(args.games):
        map_name = args.map or random.choice(map_pool)
        record = asyncio.run(run_match(opponent, map_name, args.timeout))
        record["git_sha"] = "versus"
        with open(history, "a") as f:
            f.write(json.dumps(record) + "\n")
        print(f"[{i + 1}/{args.games}] {record.get('result'):<8} "
              f"vs {opponent['name']} (elo {opponent.get('elo')}) "
              f"on {map_name} ({record['wall_seconds']}s wall)")
        if record.get("error"):
            print("    error:", record["error"][:300])


if __name__ == "__main__":
    main()
