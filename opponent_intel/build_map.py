"""Generate opponent_map.json: opponent identity (game_display_id UUID + name)
-> our profile + play-style classification.

In-game a bot only receives the opponent's `game_display_id` (a stable UUID) via
`--OpponentId`; the name is never passed. This builds the lookup table so a bot
can turn that UUID back into "who is this and what do they do". Our local harness
(harness/versus.py) passes the opponent's NAME as --OpponentId instead, so the
table is also indexed by lowercased name — the resolver accepts either form.

    AA_API_TOKEN=... python opponent_intel/build_map.py

Reads the profiled bots from bot_profiles/data/*.json, fetches each one's
game_display_id from the AI Arena API, classifies its STYLE, and writes
opponent_intel/opponent_map.json.
"""
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "bot_profiles"))

from opponent_intel.classify import classify_style  # noqa: E402

TOKEN = os.environ.get("AA_API_TOKEN")
if not TOKEN:
    sys.exit("set AA_API_TOKEN")

# STYLE strings live in the profile generator (single source of truth).
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location(
    "_genobj", os.path.join(ROOT, "bot_profiles", "_generate_objective.py"))
_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_gen)
STYLE = _gen.STYLE


def api(path):
    req = urllib.request.Request("https://aiarena.net/api/" + path,
                                 headers={"Authorization": "Token " + TOKEN})
    for a in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            if a == 5:
                return None
            time.sleep(min(2 ** a, 20))


# collect profiled bots from the batch data files
bots = {}  # name -> meta
for f in ("topbot_data.json", "topbot_data2.json", "topbot_data3.json"):
    p = os.path.join(ROOT, "bot_profiles", "data", f)
    if not os.path.exists(p):
        continue
    for name, e in json.load(open(p)).items():
        bots[name] = e["meta"]

out_bots = {}
names = {}
done = 0
for name, meta in bots.items():
    b = api(f"bots/{meta['id']}/?format=json")
    if not b:
        print(f"  meta fail: {name}", file=sys.stderr)
        continue
    uuid = b["game_display_id"]
    style = STYLE.get(name, "")
    opp_style = classify_style(style, meta.get("race", ""))
    out_bots[uuid] = {
        "name": name,
        "race": meta.get("race", "?"),
        "elo": meta.get("elo"),
        "style": style,
        "opp_style": opp_style,
    }
    names[name.lower()] = uuid
    done += 1
    print(f"[{done}/{len(bots)}] {name:<22} {uuid} {opp_style}", file=sys.stderr)

result = {
    "meta": {
        "source": "aiarena.net API game_display_id + bot_profiles classification",
        "note": "In-game --OpponentId is the opponent's game_display_id (UUID), "
                "stable per bot. Indexed by UUID and by lowercased name.",
        "count": len(out_bots),
    },
    "bots": out_bots,
    "names": names,
}
with open(os.path.join(HERE, "opponent_map.json"), "w") as f:
    json.dump(result, f, indent=1, sort_keys=True)
print(f"WROTE opponent_map.json ({len(out_bots)} bots)", file=sys.stderr)
