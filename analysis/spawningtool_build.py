"""Ingest a published build order from spawningtool.com into a reproducible spec.

Unlike the replay-mined openings (statistical averages of structure placement),
a spawningtool *build guide* is an exact, human-authored order -- structures,
units, and upgrades with supply/time triggers, e.g.

    https://lotv.spawningtool.com/build/184161/   "Serral's Safe Macro Opener"

The build steps live in a clean ``<table class="build-table">``: each row is
``<td>supply</td><td>time</td><td><span class="Building|Unit|Upgrade">name</span>
</td><td>note</td>``. This fetches a build by id and parses it into the JSON the
reusable ``strategy_engine.build_guides`` library loads.

    python analysis/spawningtool_build.py <build_id> [<build_id> ...]

Writes strategy_engine/data/build_guides/<id>.json. Proxy-aware.
"""
import html
import json
import os
import re
import sys
import urllib.request

URL = "https://lotv.spawningtool.com/build/{}/"
UA = "Mozilla/5.0 (build-study)"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "strategy_engine",
                       "data", "build_guides")

ROW_RE = re.compile(
    r"<td[^>]*>\s*((?:&nbsp;)*\s*[\d]+)\s*</td>"        # supply
    r"\s*<td[^>]*>\s*((?:&nbsp;)*\s*[\d:]+)?\s*</td>"    # time (maybe blank)
    r"\s*<td[^>]*>.*?<span class=\"(Building|Unit|Upgrade)\">([^<]+)</span>"
    r".*?</td>"                                          # type + name
    r"\s*<td[^>]*>(.*?)</td>",                           # note
    re.DOTALL)

TYPE_ACTION = {"Building": "build", "Unit": "train", "Upgrade": "research"}


def _clean(s):
    return html.unescape(re.sub(r"&nbsp;|\s+", " ", s or "")).strip()


def _time_seconds(t):
    t = _clean(t)
    m = re.match(r"(\d+):(\d+)", t)
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def _name_count(raw):
    name = _clean(raw)
    m = re.search(r"\s*x\s*(\d+)$", name)
    if m:
        return name[:m.start()].strip(), int(m.group(1))
    return name, 1


def fetch(build_id):
    req = urllib.request.Request(URL.format(build_id), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


RACE_MARKERS = {
    "Zerg": {"Drone", "Overlord", "Zergling", "Hatchery", "Spawning Pool",
             "Queen", "Baneling", "Roach", "Lair", "Extractor"},
    "Terran": {"SCV", "Marine", "Supply Depot", "Barracks", "Command Center",
               "Refinery", "Orbital Command", "Reaper", "Marauder", "Factory"},
    "Protoss": {"Probe", "Zealot", "Pylon", "Gateway", "Nexus", "Assimilator",
                "Cybernetics Core", "Stalker", "Adept", "Forge"},
}


def _infer_race(steps):
    score = {r: 0 for r in RACE_MARKERS}
    for s in steps:
        for r, marks in RACE_MARKERS.items():
            if s["name"] in marks:
                score[r] += 1
    best = max(score, key=score.get)
    return best if score[best] else None


def _header(page, steps=None):
    title = _clean((re.search(r"<title>([^<]+)</title>", page) or [None, ""])[1])
    title = re.sub(r"^\s*spawning\s*tool\s*:?\s*", "", title, flags=re.I)
    title = re.sub(r"\s*[-|]\s*spawningtool.*$", "", title, flags=re.I).strip()
    # matchup like ZvT / PvZ / TvP in the title or anywhere on the page
    mu = (re.search(r"\b([PTZ]v[PTZX])\b", title)
          or re.search(r"\b([PTZ]v[PTZX])\b", page) or [None, None])[1]
    race = {"P": "Protoss", "T": "Terran", "Z": "Zerg"}.get(mu[0]) if mu else None
    if race is None and steps:
        race = _infer_race(steps)
    return title, race, mu


def parse(build_id, page):
    # isolate the build table to avoid matching unrelated tables
    tbl = re.search(r"<table[^>]*class=\"build-table\".*?</table>", page, re.DOTALL)
    body = tbl.group(0) if tbl else page
    steps = []
    for i, m in enumerate(ROW_RE.finditer(body)):
        supply, time_raw, kind, name_raw, note = m.groups()
        name, count = _name_count(name_raw)
        # spawningtool renders generic annotations (a chrono boost, a worker
        # pull, a scout) as a "Unit" span literally named "Action" -- these are
        # not buildable entities, so tag them as notes, not build steps.
        action = "note" if re.match(r"Action\b", name) else TYPE_ACTION[kind]
        steps.append({
            "i": i,
            "supply": int(_clean(supply)) if _clean(supply).isdigit() else None,
            "t": _time_seconds(time_raw),
            "action": action,
            "name": name,
            "count": count,
            "note": _clean(re.sub(r"<[^>]+>", "", note)),
        })
    title, race, matchup = _header(page, steps)
    return {"id": int(build_id), "title": title, "race": race,
            "matchup": matchup, "source": URL.format(build_id), "steps": steps}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    os.makedirs(OUT_DIR, exist_ok=True)
    for bid in sys.argv[1:]:
        page = fetch(bid)
        build = parse(bid, page)
        path = os.path.abspath(os.path.join(OUT_DIR, f"{bid}.json"))
        with open(path, "w") as f:
            json.dump(build, f, indent=2)
        print(f"{build['title']} [{build['matchup']}] -- {len(build['steps'])} "
              f"steps -> {path}")


if __name__ == "__main__":
    main()
