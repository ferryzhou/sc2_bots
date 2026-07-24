"""Probe downloaded arena bots for launchability, without playing a game.

Launches a bot with versus.py's exact command/cwd/env, GamePort pointed at a
dummy websocket server that accepts /sc2api and reads forever without
replying. A bot that crashes on import/launch (missing deps, bad binary)
dies before connecting; a healthy one connects (or is still alive at the
window) and is classified runnable. In-game crashers can pass this probe --
that evidence only comes from real games (versus.py records them as Error).

    python harness/probe_bots.py              # probe every bot in BOTS_DIR
    python harness/probe_bots.py --name Aeolus
"""
import argparse
import asyncio
import json
import socket
import time
from pathlib import Path

from aiohttp import web

from versus import BOTS_DIR, opponent_command, opponent_env

WINDOW = 30
CONCURRENCY = 8


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def probe_async(name: str, log_dir: Path | None = None) -> tuple[bool, str]:
    """(runnable, detail) for one extracted bot in BOTS_DIR."""
    try:
        cmd, cwd = opponent_command(BOTS_DIR / name, name)
    except Exception as exc:  # noqa: BLE001
        return False, f"no launch spec: {exc}"

    connected = asyncio.Event()

    async def handler(request):
        ws = web.WebSocketResponse(max_msg_size=0)
        await ws.prepare(request)
        connected.set()
        async for _ in ws:
            pass
        return ws

    port = free_port()
    app = web.Application()
    app.router.add_route("GET", "/sc2api", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "127.0.0.1", port).start()

    log = (log_dir or Path("/tmp")) / f"probe_{name}.log"
    lf = open(log, "wb")
    start = time.time()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, "--GamePort", str(port), "--LadderServer", "127.0.0.1",
            "--StartPort", str(free_port()), "--OpponentId", "Probe",
            cwd=cwd, env=opponent_env(),
            stdout=lf, stderr=asyncio.subprocess.STDOUT)
    except Exception as exc:  # noqa: BLE001
        lf.close()
        await runner.cleanup()
        return False, f"spawn failed: {exc}"

    wait = asyncio.ensure_future(proc.wait())
    conn = asyncio.ensure_future(connected.wait())
    await asyncio.wait({wait, conn}, timeout=WINDOW,
                       return_when=asyncio.FIRST_COMPLETED)
    alive = proc.returncode is None
    if connected.is_set() or alive:
        ok, detail = True, ("connected" if connected.is_set()
                            else f"alive at {WINDOW}s without connecting")
    else:
        lf.flush()
        lines = [l.strip() for l in
                 log.read_text(errors="replace").splitlines() if l.strip()]
        ok = False
        detail = (f"exited rc={proc.returncode} in {time.time() - start:.0f}s: "
                  + (lines[-1][:160] if lines else "no output"))
    conn.cancel()
    if alive:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()
    lf.close()
    await runner.cleanup()
    return ok, detail


def probe(name: str) -> tuple[bool, str]:
    """Synchronous wrapper for one bot."""
    return asyncio.run(probe_async(name))


async def _probe_all(names: list[str]) -> list[dict]:
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(n):
        async with sem:
            ok, detail = await probe_async(n)
            return {"name": n, "runnable": ok, "detail": detail}

    return await asyncio.gather(*(one(n) for n in names))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--name", help="probe a single bot (default: all in BOTS_DIR)")
    args = p.parse_args()

    names = ([args.name] if args.name else
             sorted(d.name for d in BOTS_DIR.iterdir() if d.is_dir()))
    results = asyncio.run(_probe_all(names))
    ok = [r for r in results if r["runnable"]]
    print(f"{len(ok)}/{len(results)} launchable")
    for r in results:
        if not r["runnable"]:
            print(f"  BROKEN {r['name']}: {r['detail']}")
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
