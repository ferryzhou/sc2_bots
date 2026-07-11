"""Download publicly-downloadable bots from aiarena.net for local testing.

Downloads python and cpplinux bot zips (the types runnable natively on
Linux) into BOTS_DIR, extracts each into its own folder, and writes a
manifest (results/opponents.json) with name, type, race and current-season
Elo so gauntlets can pick opponents by strength.

Usage:
    AIARENA_API_TOKEN=... python harness/download_bots.py [--limit N]
"""

import argparse
import io
import json
import shutil
import sys
import zipfile
from os import environ
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
BOTS_DIR = Path(environ.get("ARENA_BOTS_DIR", "/root/arena_bots"))
MANIFEST = REPO_ROOT / "results" / "opponents.json"
RUNNABLE_TYPES = {"python", "cpplinux"}
CURRENT_COMPETITION = 36
MIN_FREE_GB = 4.0


def api_get(session, url):
    r = session.get(url, timeout=120)
    r.raise_for_status()
    return r.json()


def free_gb() -> float:
    return shutil.disk_usage("/").free / 1e9


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                        help="max bots to download (default: all runnable)")
    args = parser.parse_args()

    token = environ.get("AIARENA_API_TOKEN")
    if not token:
        sys.exit("Set AIARENA_API_TOKEN")
    s = requests.Session()
    s.headers["Authorization"] = f"Token {token}"

    # current-season elo per bot id
    elo_by_bot: dict[int, dict] = {}
    url = (f"https://aiarena.net/api/competition-participations/"
           f"?competition={CURRENT_COMPETITION}&limit=100")
    while url:
        d = api_get(s, url)
        for p in d["results"]:
            elo_by_bot[p["bot"]] = {
                "elo": p.get("elo"),
                "division": p.get("division_num"),
                "active": p.get("active"),
            }
        url = d.get("next")
    print(f"loaded {len(elo_by_bot)} current-season participations")

    # all downloadable bots
    bots = []
    url = "https://aiarena.net/api/bots/?bot_zip_publicly_downloadable=true&limit=100"
    while url:
        d = api_get(s, url)
        bots += d["results"]
        url = d.get("next")
    runnable = [b for b in bots if b["type"] in RUNNABLE_TYPES]
    # strongest first so a partial download still gets useful opponents
    runnable.sort(key=lambda b: (elo_by_bot.get(b["id"], {}).get("elo") or 0),
                  reverse=True)
    if args.limit:
        runnable = runnable[: args.limit]
    print(f"{len(bots)} downloadable, {len(runnable)} runnable "
          f"({'+'.join(sorted(RUNNABLE_TYPES))})")

    BOTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, b in enumerate(runnable):
        name = b["name"]
        dest = BOTS_DIR / name
        entry = {
            "name": name,
            "id": b["id"],
            "type": b["type"],
            "race": b["plays_race"]["label"],
            **elo_by_bot.get(b["id"], {}),
        }
        if dest.is_dir():
            manifest.append(entry)
            continue
        if free_gb() < MIN_FREE_GB:
            print(f"stopping: less than {MIN_FREE_GB}GB free")
            break
        try:
            r = s.get(b["bot_zip"], timeout=300)
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(dest)
            entry["zip_mb"] = round(len(r.content) / 1e6, 1)
            manifest.append(entry)
            print(f"[{i + 1}/{len(runnable)}] {name} "
                  f"({entry['type']}, {entry['race']}, elo={entry.get('elo')}, "
                  f"{entry['zip_mb']}MB)")
        except Exception as exc:  # noqa: BLE001
            print(f"[{i + 1}/{len(runnable)}] {name} FAILED: {exc}")

    # merge with the existing manifest: keep entries for bots that are no
    # longer publicly downloadable but are still extracted locally
    if MANIFEST.is_file():
        try:
            fresh_names = {e["name"] for e in manifest}
            for old in json.loads(MANIFEST.read_text()):
                if (old["name"] not in fresh_names
                        and (BOTS_DIR / old["name"]).is_dir()):
                    manifest.append({**old, "local_only": True})
        except (ValueError, KeyError):
            pass

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1))
    print(f"\n{len(manifest)} opponents ready in {BOTS_DIR}")
    print(f"manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
