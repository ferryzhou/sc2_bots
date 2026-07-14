"""Objective performance stats for an AI Arena bot: overall W/L, by-opponent,
by-opponent-race. Usage: botstats.py <bot_id> <bot_name> [n_matches]"""
import os, sys, json, time, urllib.request, collections

TOKEN = os.environ["AA_API_TOKEN"]
BID = int(sys.argv[1]); BNAME = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 400
SD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stats")
os.makedirs(SD, exist_ok=True)


def api(path):
    req = urllib.request.Request("https://aiarena.net/api/" + path,
                                 headers={"Authorization": "Token " + TOKEN})
    for a in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception:
            if a == 4:
                raise
            time.sleep(2 ** a)


race_cache = {}
def race_of(name):
    if name in race_cache:
        return race_cache[name]
    try:
        d = api(f"bots/?format=json&name={urllib.parse.quote(name)}")
        r = d["results"][0]["plays_race"]["label"] if d["results"] else "?"
    except Exception:
        r = "?"
    race_cache[name] = r
    return r

import urllib.parse
matches = []
url = f"matches/?format=json&bot={BID}&limit=50"
while url and len(matches) < N:
    d = api(url)
    matches.extend(d["results"])
    nxt = d["next"]
    url = nxt.split("/api/")[1] if nxt else None

opp = collections.defaultdict(lambda: {"W": 0, "L": 0, "o": 0})
W = L = o = 0
p1w = p2w = 0
crash = 0
reps = {"W": [], "L": []}
for m in matches:
    r = m.get("result")
    if not r:
        continue
    b1, b2 = r["bot1_name"], r["bot2_name"]
    if BNAME not in (b1, b2):
        continue
    them = b2 if b1 == BNAME else b1
    we_p1 = (b1 == BNAME)
    t = r["type"]; win = r["winner"]
    if t in ("Player1Win", "Player2Win"):
        won = (win == BID)
        (opp[them].__setitem__("W", opp[them]["W"]+1) if won else opp[them].__setitem__("L", opp[them]["L"]+1))
        if won: W += 1
        else: L += 1
        if r.get("replay_file") and len(reps["W" if won else "L"]) < 40:
            reps["W" if won else "L"].append({"opp": them, "match": m["id"], "rep": r["replay_file"], "steps": r.get("game_steps")})
    elif "Crash" in t or "TimeOut" in t:
        crash += 1
        cp1 = t.startswith("Player1")
        wecrash = (cp1 == we_p1)
        if wecrash: L += 1; opp[them]["L"] += 1
        else: W += 1; opp[them]["W"] += 1
    else:
        o += 1; opp[them]["o"] += 1

tot = W + L
print(f"\n{BNAME} (id {BID}): {len(matches)} recent matches parsed")
print(f"  RECORD: {W}W - {L}L  ({100*W/max(1,tot):.1f}%)  [+{o} draws/other, {crash} crash/timeout incl above]")

# by race
byrace = collections.defaultdict(lambda: [0, 0])
for name, rec in opp.items():
    rc = race_of(name)
    byrace[rc][0] += rec["W"]; byrace[rc][1] += rec["L"]
print("\n  vs each race:")
for rc in ("T", "P", "Z", "R", "?"):
    if rc in byrace:
        w, l = byrace[rc]
        print(f"    vs {rc}: {w}-{l} ({100*w/max(1,w+l):.0f}%)")

# hardest opponents (most losses) and best (most wins), min 2 games
print("\n  toughest opponents (lose most):")
tough = sorted(opp.items(), key=lambda kv: (kv[1]["L"]-kv[1]["W"], kv[1]["L"]), reverse=True)
for name, rec in tough[:12]:
    if rec["L"] >= 1:
        print(f"    {name:<22} {rec['W']}-{rec['L']}  ({race_of(name)})")
print("\n  best matchups (win most):")
best = sorted(opp.items(), key=lambda kv: (kv[1]["W"]-kv[1]["L"], kv[1]["W"]), reverse=True)
for name, rec in best[:10]:
    if rec["W"] >= 1:
        print(f"    {name:<22} {rec['W']}-{rec['L']}  ({race_of(name)})")

json.dump({"record": {"W": W, "L": L, "o": o}, "byrace": {k: v for k, v in byrace.items()},
           "opp": {k: v for k, v in opp.items()}, "reps": reps},
          open(f"{SD}/{BNAME}.json", "w"), indent=1)
print(f"\n  saved {BNAME}.json ({sum(len(v) for v in reps.values())} replay urls)")
