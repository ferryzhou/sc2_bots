"""Convert ingested spawningtool builds into ares build-runner openings.

AegisBot (ares-sc2) runs step-by-step openings from ``aegis/terran_builds.yml``
in the ares build-runner DSL: each line is ``<supply> <TOKEN> [@ <TARGET>]``,
where ares upper-cases TOKEN and resolves it as ``UnitTypeId[TOKEN]`` /
``UpgradeId[TOKEN]`` (exactly the tokens in ``strategy_engine.build_guides``) or a
special keyword (SUPPLY, GAS, EXPAND, ORBITAL, CORE, GATE, WORKER).

This turns a build_guides JSON into that DSL so pro builds become first-class
AegisBot openings. Structures/units that ares has a placement/morph keyword for
(supply-at-wall, gas-on-geyser, expand-at-next-base, orbital-morph) use the
keyword; everything else emits the raw token ares resolves directly.

    python analysis/spawningtool_to_ares.py 203108 203133 ...   # -> yaml on stdout
    python analysis/spawningtool_to_ares.py --write aegis/terran_builds.yml 203108 ...

``--write`` appends the generated builds under the file's ``Builds:`` section.
"""
import argparse
import json
import os
import sys

BG_DIR = os.path.join(os.path.dirname(__file__), "..", "strategy_engine",
                      "data", "build_guides")

# spawningtool token -> ares keyword (placement / morph / race-agnostic). Anything
# not here emits its raw token, which ares resolves via UnitTypeId[TOKEN].
TO_KEYWORD = {
    "SUPPLYDEPOT": "supply", "PYLON": "supply", "OVERLORD": "supply",
    "REFINERY": "gas", "ASSIMILATOR": "gas", "EXTRACTOR": "gas",
    "COMMANDCENTER": "expand", "NEXUS": "expand", "HATCHERY": "expand",
    "ORBITALCOMMAND": "orbital",
    "CYBERNETICSCORE": "core", "GATEWAY": "gate",
    "SCV": "worker", "PROBE": "worker", "DRONE": "worker",
}
RACE_PREFIX = {"Terran": "st_t", "Protoss": "st_p", "Zerg": "st_z"}


def _slug(title):
    keep = "".join(c if c.isalnum() else "_" for c in title)
    return "_".join(w for w in keep.split("_") if w)[:40]


def convert(build, max_supply=None, max_steps=40):
    """Return (name, ares_lines) for a build_guides dict."""
    prefix = RACE_PREFIX.get(build.get("race"), "st")
    name = f"{prefix}_{_slug(build.get('title', str(build['id'])))}"
    # need the token mapping from the library
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from strategy_engine.build_guides import NAME_TO_UNIT, NAME_TO_UPGRADE, _base_name

    lines, kept = [], 0
    last_supply = 12
    for s in build["steps"]:
        if s["action"] == "note":
            continue
        supply = s.get("supply") or last_supply
        last_supply = supply
        if max_supply and supply > max_supply:
            break
        if kept >= max_steps:
            break
        base = _base_name(s["name"])
        if s["action"] == "research":
            tok = NAME_TO_UPGRADE.get(base)
        else:
            tok = NAME_TO_UNIT.get(base)
        if not tok:
            continue  # unmapped (ability/annotation) -- skip, not reproducible
        emit = TO_KEYWORD.get(tok, tok)
        for _ in range(max(1, s.get("count", 1))):
            lines.append(f"            - {supply} {emit}")
            kept += 1
    return name, lines


def yaml_block(build, name, lines):
    src = build.get("source", "")
    mu = build.get("matchup") or build.get("race")
    head = (f"    # {build.get('title', '')} [{mu}]\n"
            f"    # source: {src}\n"
            f"    {name}:\n"
            f"        ConstantWorkerProductionTill: 40\n"
            f"        OpeningBuildOrder:\n")
    return head + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--write", help="terran_builds.yml to append Builds into")
    ap.add_argument("--max-supply", type=int, default=None)
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--race", default=None, help="only convert this race")
    args = ap.parse_args()

    blocks, names = [], []
    for bid in args.ids:
        path = os.path.join(BG_DIR, f"{bid}.json")
        if not os.path.isfile(path):
            print(f"# skip {bid}: not ingested", file=sys.stderr)
            continue
        build = json.load(open(path))
        if args.race and build.get("race") != args.race:
            continue
        name, lines = convert(build, args.max_supply, args.max_steps)
        if not lines:
            print(f"# skip {bid}: no reproducible steps", file=sys.stderr)
            continue
        blocks.append(yaml_block(build, name, lines))
        names.append(name)

    out = "\n".join(blocks)
    if args.write:
        with open(args.write, "a") as f:
            f.write("\n" + out)
        print(f"appended {len(names)} builds to {args.write}: {', '.join(names)}",
              file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
