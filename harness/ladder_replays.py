"""Download our bot's recent ladder match replays from aiarena.net.

As the bot owner we can fetch the replay_file of matches we played,
which makes every ladder loss a locally-analyzable artifact even when
the opponent's bot zip is not downloadable.

Usage:
    AIARENA_API_TOKEN=... python harness/ladder_replays.py \
        --bot-id 772 --losses-only --limit 12
"""

import argparse
import json
import sys
import time
import urllib.request
from os import environ
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "results" / "ladder_replays"


def api(url: str, token: str | None, tries: int = 4):
    headers = {"Authorization": f"Token {token}"} if token else {}
    req = urllib.request.Request(url, headers=headers)
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            # media URLs (replay files) reject the Authorization header
            if exc.code == 400 and token:
                return api(url, None, tries)
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot-id", default="772")
    parser.add_argument("--bot-ladder-name", default="lishimin")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--losses-only", action="store_true")
    args = parser.parse_args()

    token = environ.get("AIARENA_API_TOKEN")
    if not token:
        sys.exit("Set AIARENA_API_TOKEN")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parts = json.loads(api(
        f"https://aiarena.net/api/match-participations/"
        f"?bot={args.bot_id}&ordering=-match&limit=60", token))

    manifest = []
    for p in parts.get("results", []):
        if len(manifest) >= args.limit:
            break
        if not p.get("result"):
            continue
        if args.losses_only and p["result"] != "loss":
            continue
        match = json.loads(api(
            f"https://aiarena.net/api/matches/{p['match']}/", token))
        res = match.get("result") or {}
        created = res.get("created") or ""
        if not created.startswith("2026"):
            break  # older seasons from here on
        replay_url = res.get("replay_file")
        if not replay_url:
            continue
        opp = (res.get("bot1_name")
               if res.get("bot2_name") == args.bot_ladder_name
               else res.get("bot2_name"))
        dest = OUT_DIR / f"{p['result']}_{opp}_{p['match']}.SC2Replay"
        if not dest.is_file():
            dest.write_bytes(api(replay_url, token))
        entry = {
            "match": p["match"], "opponent": opp, "result": p["result"],
            "cause": p.get("result_cause"), "when": created,
            "game_steps": res.get("game_steps"), "file": dest.name,
        }
        manifest.append(entry)
        print(f"{p['result']:<5} vs {opp:<22} {created[:16]} "
              f"~{round((res.get('game_steps') or 0) / 22.4 / 60, 1)}min "
              f"-> {dest.name}")

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"\n{len(manifest)} replays in {OUT_DIR}")


if __name__ == "__main__":
    main()
