"""Analyze SC2 replays against the strategy_engine principles.

For each 1v1 replay, extract per-player timelines from sc2reader tracker events
(economy, supply, floating, investment split, trade efficiency, upgrades, base
timing), decide winner vs loser, and attribute the result to the principles the
winner followed / loser violated.

Usage:
    python analysis/principle_analyzer.py "path/to/*.SC2Replay"

Requires ``sc2reader`` (which needs ``mpyq``). On recent setuptools, ``mpyq``'s
setup.py fails to build; since it is a single pure-Python module you can vendor
it directly:
    pip download mpyq --no-deps --no-binary :all: -d /tmp/mpyq && \
        tar xzf /tmp/mpyq/mpyq-*.tar.gz -C /tmp/mpyq && \
        cp /tmp/mpyq/mpyq-*/mpyq.py "$(python -c 'import site;print(site.getsitepackages()[0])')/" && \
        pip install sc2reader --no-deps

See analysis/REPLAY_FINDINGS.md for a write-up of results on 65 pro games and
90 AI Arena bot games (the latter via aa_download.py + aa_analyze.py).
"""

import sys
import glob
from datetime import datetime, timezone

import sc2reader
from sc2reader import utils
from sc2reader.resources import Replay, GAME_SPEED_FACTOR

TOWNHALLS = {"Nexus", "CommandCenter", "Hatchery", "OrbitalCommand", "PlanetaryFortress"}
STD_RACES = {"Protoss", "Terran", "Zerg"}


def patch_sc2reader_for_arena():
    """Tolerate AI Arena arena-client replays, which omit ``cache_handles``.

    Stock sc2reader crashes in ``load_details`` on ``cache_handles[0]`` for these
    replays. This wrapper falls back to sane defaults (region us, LotV) when the
    handles are missing, leaving normal ladder replays untouched. Called on import
    so both this tool and ``aa_analyze.py`` benefit. AA replays also carry a few
    game-event types sc2reader 1.9 can't parse, so analyze them at load_level=3
    (tracker events only) -- see aa_analyze.py.
    """
    _orig = Replay.load_details

    def load_details(self):
        if "replay.details" in self.raw_data:
            details = self.raw_data["replay.details"]
        elif "replay.details.backup" in self.raw_data:
            details = self.raw_data["replay.details.backup"]
        else:
            return
        if details.get("cache_handles"):
            return _orig(self)
        self.map_name = details["map_name"]
        self.region = "us"
        self.map_hash = None
        self.map_file = None
        self.expansion = "LotV"
        self.windows_timestamp = details["file_time"]
        self.unix_timestamp = utils.windows_to_unix(self.windows_timestamp)
        self.end_time = datetime.fromtimestamp(self.unix_timestamp, timezone.utc)
        if details["utc_adjustment"] < 10 ** 7 * 60 * 60 * 24:
            self.time_zone = details["utc_adjustment"] / (10 ** 7 * 60 * 60)
        else:
            self.time_zone = (details["utc_adjustment"] - details["file_time"]) / (
                10 ** 7 * 60 * 60
            )
        self.game_length = self.length
        self.real_length = utils.Length(
            seconds=int(self.length.seconds
                        // GAME_SPEED_FACTOR[self.expansion].get(self.speed, 1.0))
        )
        self.start_time = datetime.fromtimestamp(
            self.unix_timestamp - self.real_length.seconds, timezone.utc
        )
        self.date = self.end_time

    Replay.load_details = load_details


patch_sc2reader_for_arena()


def analyze_replay(path):
    r = sc2reader.load_replay(path, load_level=4)
    humans = [p for p in r.players if not p.is_observer]
    # Filter to standard 1v1 with a decisive result.
    if len(humans) != 2:
        return None
    if any(str(p.play_race) not in STD_RACES for p in humans):
        return None
    results = sorted(str(p.result) for p in humans)
    if results != ["Loss", "Win"]:
        return None
    if r.game_length.seconds < 180:
        return None

    stats = {p.pid: [] for p in humans}
    upgrades = {p.pid: [] for p in humans}
    bases = {p.pid: set() for p in humans}
    pid_of = {p.pid: p for p in humans}

    for e in r.tracker_events:
        n = e.name
        if n == "PlayerStatsEvent" and e.pid in stats:
            stats[e.pid].append(e)
        elif n == "UpgradeCompleteEvent" and getattr(e, "pid", None) in upgrades:
            name = e.upgrade_type_name
            # skip trivial/automatic upgrades
            if not name.lower().startswith(("spray", "sprayterran", "sprayzerg", "sprayprotoss")):
                upgrades[e.pid].append((e.second, name))
        elif n in ("UnitBornEvent", "UnitInitEvent"):
            cpid = getattr(e, "control_pid", None)
            if cpid in bases and e.unit.name in TOWNHALLS:
                bases[cpid].add(e.unit_id)

    per_player = {}
    for p in humans:
        s = stats[p.pid]
        if not s:
            return None
        # sample near-final and mid metrics
        final = s[-1]
        peak_workers = max(e.workers_active_count for e in s)
        # supply-block time: samples where capped (food_used == food_made < 200)
        block_samples = sum(
            1 for e in s
            if e.food_made < 200 and e.food_used >= e.food_made > 0
        )
        interval = max(1, (s[-1].second - s[0].second) / max(1, len(s) - 1))
        block_seconds = block_samples * interval
        # floating (banked) resources, averaged
        avg_bank = sum(e.minerals_current + e.vespene_current for e in s) / len(s)
        peak_bank = max(e.minerals_current + e.vespene_current for e in s)
        # cumulative trade efficiency
        killed = final.minerals_killed + final.vespene_killed
        lost = final.minerals_lost + final.vespene_lost
        # income (final collection rate)
        income = final.minerals_collection_rate + final.vespene_collection_rate
        # investment split (current spend)
        army_inv = final.minerals_used_current_army + final.vespene_used_current_army
        eco_inv = final.minerals_used_current_economy + final.vespene_used_current_economy
        tech_inv = final.minerals_used_current_technology + final.vespene_used_current_technology
        # worker-loss events (harassment proxy): drops in worker count between samples
        worker_losses = 0
        for a, b in zip(s, s[1:]):
            d = a.workers_active_count - b.workers_active_count
            if d >= 3:  # lost 3+ workers in one ~10s window
                worker_losses += d

        per_player[p.pid] = dict(
            name=p.name,
            race=str(p.play_race),
            result=str(p.result),
            peak_workers=peak_workers,
            final_workers=final.workers_active_count,
            bases=len(bases[p.pid]),
            block_seconds=round(block_seconds),
            avg_bank=round(avg_bank),
            peak_bank=round(peak_bank),
            killed=killed,
            lost=lost,
            trade_ratio=round(killed / lost, 2) if lost else float("inf"),
            income=round(income),
            army_inv=army_inv,
            eco_inv=eco_inv,
            tech_inv=tech_inv,
            upgrades=len(upgrades[p.pid]),
            worker_losses=worker_losses,
        )

    winner = next(pp for pp in per_player.values() if pp["result"] == "Win")
    loser = next(pp for pp in per_player.values() if pp["result"] == "Loss")
    verdicts = attribute(winner, loser)
    return dict(
        map=r.map_name,
        length_min=round(r.game_length.seconds / 60, 1),
        matchup=f"{winner['race'][0]}v{loser['race'][0]}",
        winner=winner,
        loser=loser,
        verdicts=verdicts,
    )


def attribute(w, l):
    """Compare winner vs loser on each principle; return matched observations."""
    v = []

    def pct(a, b):
        return (a - b) / b * 100 if b else 0.0

    # Economy (workers / income) -- "economy is the foundation"
    if w["peak_workers"] > l["peak_workers"] + 3 or w["income"] > l["income"] * 1.1:
        v.append(("economy", "MATCH",
                  f"winner out-economied: peak workers {w['peak_workers']} vs {l['peak_workers']}, "
                  f"income {w['income']} vs {l['income']}"))
    elif l["peak_workers"] > w["peak_workers"] + 3:
        v.append(("economy", "COUNTER",
                  f"loser had the bigger economy (workers {l['peak_workers']} vs {w['peak_workers']}) "
                  "but still lost -- economy alone did not decide it"))

    # Supply management -- "don't get supply blocked"
    if l["block_seconds"] > w["block_seconds"] + 15:
        v.append(("supply", "MATCH",
                  f"loser wasted more time supply-blocked ({l['block_seconds']}s vs {w['block_seconds']}s)"))

    # Floating -- "spend your resources"
    if l["avg_bank"] > w["avg_bank"] * 1.4 and l["avg_bank"] > 400:
        v.append(("dont_float", "MATCH",
                  f"loser floated more resources (avg bank {l['avg_bank']} vs {w['avg_bank']})"))

    # Trade efficiency -- "win trades"
    if w["trade_ratio"] > l["trade_ratio"] * 1.15:
        v.append(("efficiency", "MATCH",
                  f"winner traded better: killed/lost {w['trade_ratio']} vs {l['trade_ratio']}"))
    elif l["trade_ratio"] > w["trade_ratio"] * 1.15:
        v.append(("efficiency", "COUNTER",
                  f"loser had the better trade ratio ({l['trade_ratio']} vs {w['trade_ratio']}) "
                  "yet lost -- likely lost the decisive engagement or died to a timing"))

    # Upgrades -- "upgrades matter"
    if w["upgrades"] > l["upgrades"]:
        v.append(("upgrades", "MATCH",
                  f"winner was more upgraded ({w['upgrades']} vs {l['upgrades']} upgrades)"))

    # Expansions -- "expand"
    if w["bases"] > l["bases"]:
        v.append(("expand", "MATCH",
                  f"winner took more bases ({w['bases']} vs {l['bases']})"))

    # Harassment -- worker losses
    if l["worker_losses"] > w["worker_losses"] + 5:
        v.append(("harassment", "MATCH",
                  f"loser lost more workers to harass ({l['worker_losses']} vs {w['worker_losses']}) "
                  "-- harassment hit the economy leg"))
    elif w["worker_losses"] > l["worker_losses"] + 5:
        v.append(("harassment", "NOTE",
                  f"winner lost more workers ({w['worker_losses']} vs {l['worker_losses']}) "
                  "but still won -- absorbed the harass"))

    return v


def main():
    paths = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "replays/pro_*.SC2Replay"))
    games = []
    for path in paths:
        try:
            g = analyze_replay(path)
        except Exception as ex:
            print(f"skip {path}: {ex}", file=sys.stderr)
            continue
        if g:
            games.append(g)
    print(f"Analyzed {len(games)} standard 1v1 games\n")
    for g in games:
        w, l = g["winner"], g["loser"]
        print(f"=== {g['matchup']} on {g['map']} ({g['length_min']}min) ===")
        print(f"  WIN  {w['name']:<14} workers {w['peak_workers']:>3} bases {w['bases']} "
              f"upg {w['upgrades']:>2} trade {w['trade_ratio']} bank {w['avg_bank']:>4} block {w['block_seconds']:>3}s")
        print(f"  LOSS {l['name']:<14} workers {l['peak_workers']:>3} bases {l['bases']} "
              f"upg {l['upgrades']:>2} trade {l['trade_ratio']} bank {l['avg_bank']:>4} block {l['block_seconds']:>3}s")
        for principle, tag, note in g["verdicts"]:
            print(f"    [{tag:<7}] {principle}: {note}")
        print()

    # aggregate
    from collections import Counter
    agg = Counter()
    for g in games:
        for principle, tag, _ in g["verdicts"]:
            agg[(principle, tag)] += 1
    print("=== AGGREGATE (principle, verdict): count ===")
    for (principle, tag), c in sorted(agg.items(), key=lambda x: -x[1]):
        print(f"  {principle:<12} {tag:<7} {c}/{len(games)}")


if __name__ == "__main__":
    main()
