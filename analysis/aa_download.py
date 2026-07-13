"""Download recent AI Arena replays for the top bots of the active competition.

Requires an AI Arena API token in the ``AA_API_TOKEN`` environment variable
(get one at https://aiarena.net/profile/token/).

    AA_API_TOKEN=... python analysis/aa_download.py [out_dir] [n_per_bot] [n_bots]

Writes ``<out_dir>/*.SC2Replay`` plus ``<out_dir>/aa_meta.json`` (match id ->
winner/bot names), which aa_analyze.py consumes. Defaults: out_dir=replays_aa,
8 games each from the top 12 bots of the current standard (game_mode 1) ladder.
"""
import os
import sys
import json
import urllib.request

TOKEN = os.environ.get("AA_API_TOKEN")
if not TOKEN:
    sys.exit("set AA_API_TOKEN (see https://aiarena.net/profile/token/)")

OUT = sys.argv[1] if len(sys.argv) > 1 else "replays_aa"
PER_BOT = int(sys.argv[2]) if len(sys.argv) > 2 else 8
N_BOTS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
os.makedirs(OUT, exist_ok=True)


def api(path):
    req = urllib.request.Request(
        "https://aiarena.net/api/" + path, headers={"Authorization": "Token " + TOKEN}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def top_bots():
    """Top-ELO bots of the current open standard (game_mode 1) competition."""
    comps = api("competitions/?format=json&status=open")["results"]
    comp = next((c for c in comps if c.get("game_mode") == 1), comps[0])
    print(f"competition: {comp['id']} {comp['name']}")
    parts = api(f"competition-participations/?format=json&competition={comp['id']}&ordering=-elo")
    return [p["bot"] for p in parts["results"][:N_BOTS]]


meta = {}
seen = set()
downloaded = 0
for bot in top_bots():
    per = 0
    for m in api(f"matches/?format=json&bot={bot}&ordering=-id")["results"]:
        if per >= PER_BOT:
            break
        mid = m["id"]
        if mid in seen:
            continue
        seen.add(mid)
        res = m.get("result") or {}
        rf = res.get("replay_file")
        if not rf or res.get("replay_file_has_been_cleaned"):
            continue
        if res.get("type") not in ("Player1Win", "Player2Win"):
            continue
        b1, b2 = res.get("bot1_name", "?"), res.get("bot2_name", "?")
        dest = os.path.join(OUT, f"aa_{mid}_{b1}_vs_{b2}.SC2Replay")
        if not os.path.exists(dest):
            try:
                urllib.request.urlretrieve(rf, dest)
            except Exception as e:
                print("  failed:", e)
                continue
        if os.path.getsize(dest) > 1000:
            meta[str(mid)] = {"type": res["type"], "b1": b1, "b2": b2}
            downloaded += 1
            per += 1
            print(f"  [{downloaded}] {b1} vs {b2}")

json.dump(meta, open(os.path.join(OUT, "aa_meta.json"), "w"))
print(f"\ndownloaded {downloaded} replays + meta to {OUT}")
