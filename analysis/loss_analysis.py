"""Deep loss analysis: why did the bot lose the battles, not just the game?

game_report answers "was macro ok?". This answers the next question -- what
happened in the FIGHTS. It reconstructs, for both players, army value/supply,
composition, and upgrades over time from unit births/deaths, finds the decisive
engagements (death spikes), and reports the state going into each: army balance,
composition matchup, and upgrade deficit -- then a root-cause summary.

    python analysis/loss_analysis.py <replay> [our_pid]   (default pid 1)

Costs are minerals+gas; army value is the sum over alive army units.
"""
import sys
import os
from collections import defaultdict, Counter

import principle_analyzer as pa  # sc2reader arena shim
import sc2reader

# resource cost (minerals, gas) for value; supply for army-supply.
COST = {
    # Protoss
    "Probe": (50, 0, 1), "Zealot": (100, 0, 2), "Stalker": (125, 50, 2),
    "Sentry": (50, 100, 2), "Adept": (100, 25, 2), "HighTemplar": (50, 150, 2),
    "DarkTemplar": (125, 125, 2), "Immortal": (275, 100, 4), "Colossus": (300, 200, 6),
    "Archon": (175, 275, 4), "Observer": (25, 75, 1), "WarpPrism": (250, 0, 2),
    "Phoenix": (150, 100, 2), "VoidRay": (250, 150, 4), "Oracle": (150, 150, 3),
    "Carrier": (350, 250, 6), "Tempest": (250, 175, 5), "Mothership": (400, 400, 8),
    # Zerg
    "Drone": (50, 0, 1), "Zergling": (25, 0, 1), "Baneling": (50, 25, 1),
    "Roach": (75, 25, 2), "Ravager": (100, 100, 3), "Hydralisk": (100, 50, 2),
    "LurkerMP": (150, 150, 3), "Mutalisk": (100, 100, 2), "Corruptor": (150, 100, 2),
    "BroodLord": (300, 250, 4), "Ultralisk": (300, 200, 6), "Infestor": (100, 150, 2),
    "Queen": (150, 0, 2), "Overlord": (100, 0, 0), "Overseer": (150, 50, 0),
    "SwarmHostMP": (100, 75, 3), "Viper": (100, 200, 3),
    # Terran
    "SCV": (50, 0, 1), "Marine": (50, 0, 1), "Marauder": (100, 25, 2),
    "Reaper": (50, 50, 1), "Ghost": (150, 125, 3), "Hellion": (100, 0, 2),
    "Hellbat": (100, 0, 2), "WidowMine": (75, 25, 2), "SiegeTank": (150, 125, 3),
    "Cyclone": (150, 100, 3), "Thor": (300, 200, 6), "VikingFighter": (150, 75, 2),
    "Medivac": (100, 100, 2), "Liberator": (150, 150, 3), "Banshee": (150, 100, 3),
    "Raven": (100, 200, 2), "Battlecruiser": (400, 300, 6),
}
WORKERS = {"Probe", "SCV", "Drone"}
NONARMY = WORKERS | {"Overlord", "Larva", "Egg", "Broodling", "MULE",
                     "Interceptor", "AutoTurret", "LocustMP", "Observer"}
TOWNHALLS = {"Nexus", "Hatchery", "Lair", "Hive", "CommandCenter",
             "OrbitalCommand", "PlanetaryFortress"}


def val(name):
    m, g, _ = COST.get(name, (0, 0, 0))
    return m + g


def is_army(name):
    return name in COST and name not in NONARMY


def mmss(s):
    return f"{int(s)//60}:{int(s) % 60:02d}"


def load(path):
    r = sc2reader.load_replay(path, load_level=3)
    units = {}  # unit_id -> [owner_pid, name, born, died]
    for e in r.tracker_events:
        if e.name in ("UnitBornEvent", "UnitInitEvent"):
            owner = getattr(e, "control_pid", None)
            name = getattr(getattr(e, "unit", None), "name", None)
            if owner and name:
                units.setdefault(e.unit_id, [owner, name, e.second, None])
        elif e.name == "UnitDiedEvent":
            if e.unit_id in units:
                units[e.unit_id][3] = e.second
    stats = defaultdict(list)  # pid -> [(sec, event)]
    upgrades = defaultdict(list)  # pid -> [(sec, name)]
    for e in r.tracker_events:
        if e.name == "PlayerStatsEvent":
            stats[e.pid].append(e)
        elif e.name == "UpgradeCompleteEvent":
            n = e.upgrade_type_name
            if not n.lower().startswith("spray") and "weapon" not in n.lower()[:1]:
                upgrades[e.pid].append((e.second, n))
    return r, units, stats, upgrades


def alive_army(units, pid, t):
    """(value, supply, Counter(comp)) of pid's army alive at time t."""
    v = s = 0
    comp = Counter()
    for owner, name, born, died in units.values():
        if owner != pid or not is_army(name):
            continue
        if born <= t and (died is None or died > t):
            v += val(name)
            s += COST.get(name, (0, 0, 0))[2]
            comp[name] += 1
    return v, s, comp


def stat_at(stats, pid, t, field, default=0):
    v = default
    for e in stats[pid]:
        if e.second <= t:
            v = getattr(e, field, default)
        else:
            break
    return v


def bases_at(units, pid, t):
    """Townhalls alive at time t (morphs keep their unit_id, so counted once)."""
    return sum(1 for owner, name, born, died in units.values()
               if owner == pid and name in TOWNHALLS
               and born <= t and (died is None or died > t))


def deaths_in(units, pid, t0, t1):
    """(value, Counter) of pid's army units that died in (t0, t1]."""
    v = 0
    comp = Counter()
    for owner, name, born, died in units.values():
        if owner == pid and is_army(name) and died is not None and t0 < died <= t1:
            v += val(name)
            comp[name] += 1
    return v, comp


def collected_by(stats, pid, t):
    """(minerals, gas) accumulated by pid up to time t, integrating income rate.

    PlayerStatsEvent fires periodically; collection_rate is per-minute, so each
    interval contributes rate * dt / 60. Approximates total resources mined.
    """
    tot_m = tot_g = 0.0
    prev = None
    for e in stats[pid]:
        if e.second > t:
            break
        if prev is not None:
            dt = e.second - prev.second
            tot_m += getattr(prev, "minerals_collection_rate", 0) * dt / 60.0
            tot_g += getattr(prev, "vespene_collection_rate", 0) * dt / 60.0
        prev = e
    return tot_m, tot_g


def army_value_made(units, pid, t):
    """Cumulative army value pid ever produced up to time t (alive + dead)."""
    return sum(val(name) for owner, name, born, died in units.values()
               if owner == pid and is_army(name) and born <= t)


def main():
    path = sys.argv[1]
    ours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    theirs = 2 if ours == 1 else 1
    r, units, stats, upgrades = load(path)
    length = int(r.game_length.seconds)

    print(f"# Loss analysis: {os.path.basename(path)}  ({r.map_name}, {r.game_length})")
    print(f"# our pid={ours}, enemy pid={theirs}\n")
    marks_all = list(range(60, length + 1, 60))

    # 0) head-to-head ECONOMY. Ratios (us/enemy): workers, mining speed (income
    # rate) and accumulated resources mined -- worker parity can hide a resource
    # deficit (fewer bases / less gas / lower saturation).
    print("--- economy: us vs enemy (absolute; ratios us/enemy) ---")
    print("time  | supply(army) workers bases |   minerals(bank/min)   gas(bank/min)  "
          "| sup  wkr  mine-spd  mined")
    eco_behind = None
    for t in marks_all:
        su1 = int(stat_at(stats, ours, t, "food_used"))
        su2 = int(stat_at(stats, theirs, t, "food_used"))
        w1 = int(stat_at(stats, ours, t, "workers_active_count"))
        w2 = int(stat_at(stats, theirs, t, "workers_active_count"))
        as1, as2 = max(0, su1 - w1), max(0, su2 - w2)     # army supply = total - workers
        b1, b2 = bases_at(units, ours, t), bases_at(units, theirs, t)
        m1b = int(stat_at(stats, ours, t, "minerals_current"))
        m1r = int(stat_at(stats, ours, t, "minerals_collection_rate"))
        m2b = int(stat_at(stats, theirs, t, "minerals_current"))
        m2r = int(stat_at(stats, theirs, t, "minerals_collection_rate"))
        g1b = int(stat_at(stats, ours, t, "vespene_current"))
        g1r = int(stat_at(stats, ours, t, "vespene_collection_rate"))
        g2b = int(stat_at(stats, theirs, t, "vespene_current"))
        g2r = int(stat_at(stats, theirs, t, "vespene_collection_rate"))
        sur = (su1 / su2) if su2 else 1.0                 # total supply ratio
        ratio = (w1 / w2) if w2 else 1.0
        inc1, inc2 = m1r + g1r, m2r + g2r                 # mining speed = income rate
        spd = (inc1 / inc2) if inc2 else 1.0
        cm1, cg1 = collected_by(stats, ours, t)
        cm2, cg2 = collected_by(stats, theirs, t)
        mined = ((cm1 + cg1) / (cm2 + cg2)) if (cm2 + cg2) else 1.0
        flag = ""
        if w2 and w1 < 0.85 * w2:
            flag = "  <-- workers behind"
            if eco_behind is None:
                eco_behind = t
        print(f"{mmss(t):>5} | {su1:>3}({as1:>3}) v {su2:>3}({as2:>3}) {w1:>3} v {w2:<3} {b1} v {b2} | "
              f"{m1b:>4}/{m1r:<4} v {m2b:>4}/{m2r:<4}  "
              f"{g1b:>4}/{g1r:<4} v {g2b:>4}/{g2r:<4} | "
              f"{sur:>4.2f} {ratio:>4.2f} {spd:>5.2f}   {mined:>4.2f}{flag}")
    pw1 = max((int(stat_at(stats, ours, t, "workers_active_count")) for t in marks_all), default=0)
    pw2 = max((int(stat_at(stats, theirs, t, "workers_active_count")) for t in marks_all), default=0)
    print(f"  peak workers: us {pw1} vs enemy {pw2} | "
          f"economy first fell behind ~ {mmss(eco_behind) if eco_behind else 'never'}\n")

    # 0b) accumulated resources mined + army value produced (cumulative, over time)
    print("--- accumulated: total mined vs army value produced ---")
    print("time  |   resources mined (min+gas=tot)      | army value made  ratio | share to army")
    print("      |   us (m/g/tot)     enemy (m/g/tot)    |   us  v enemy    (u/e)  |  us    enemy")
    for t in marks_all:
        m1, g1 = collected_by(stats, ours, t)
        m2, g2 = collected_by(stats, theirs, t)
        a1, a2 = army_value_made(units, ours, t), army_value_made(units, theirs, t)
        tot1, tot2 = m1 + g1, m2 + g2
        sh1 = a1 / tot1 if tot1 else 0
        sh2 = a2 / tot2 if tot2 else 0
        mr = (a1 / a2) if a2 else (9.9 if a1 else 1.0)   # army value produced ratio
        mflag = "  <-- army production behind" if mr < 0.85 else ""
        print(f"{mmss(t):>5} | {int(m1):>5}/{int(g1):<4}/{int(tot1):<5} "
              f"{int(m2):>5}/{int(g2):<4}/{int(tot2):<5} | "
              f"{a1:>5} v {a2:<5} {mr:>4.2f} | {sh1:>4.0%}  {sh2:>4.0%}{mflag}")
    fm1, fg1 = collected_by(stats, ours, length)
    fm2, fg2 = collected_by(stats, theirs, length)
    fa1, fa2 = army_value_made(units, ours, length), army_value_made(units, theirs, length)
    ft1, ft2 = fm1 + fg1, fm2 + fg2
    print(f"  TOTAL mined:  us {int(ft1)} ({int(fm1)}m/{int(fg1)}g)  "
          f"vs enemy {int(ft2)} ({int(fm2)}m/{int(fg2)}g)  ratio {ft1/ft2 if ft2 else 0:.2f}")
    print(f"  TOTAL army value produced: us {fa1} vs enemy {fa2}  ratio {fa1/fa2 if fa2 else 0:.2f}"
          f"  |  invested in army: us {fa1/ft1 if ft1 else 0:.0%} vs enemy {fa2/ft2 if ft2 else 0:.0%}\n")

    # 1) army value / supply timeline, with the fight that minute inline. val =
    # army value ratio (us/enemy), sup = army supply ratio (they can diverge --
    # cheap melee fills supply without value).
    print("time  | our army (val/sup)  enemy army (val/sup) | val  sup | upg u/e | this-min fight: lost u/e (trade)")
    marks = list(range(60, length + 1, 60))
    behind_since = None
    for t in marks:
        ov, os_, _ = alive_army(units, ours, t)
        ev, es_, _ = alive_army(units, theirs, t)
        ratio = (ov / ev) if ev else (9.9 if ov else 1.0)
        sratio = (os_ / es_) if es_ else (9.9 if os_ else 1.0)
        oup = sum(1 for s, _ in upgrades[ours] if s <= t)
        eup = sum(1 for s, _ in upgrades[theirs] if s <= t)
        lost1, _ = deaths_in(units, ours, t - 60, t)
        lost2, _ = deaths_in(units, theirs, t - 60, t)
        battle = ""
        if max(lost1, lost2) >= 200:  # a real fight happened this minute
            trade = (lost2 / lost1) if lost1 else 9.9
            mark = "BATTLE" if max(lost1, lost2) >= 700 else "skirm "
            battle = f" | {mark} lost {lost1:>4}/{lost2:<4} trade {trade:>4.2f}"
        flag = ""
        if ev > 0 and ov < 0.7 * ev:
            flag = "  <-- army deficit"
            if behind_since is None:
                behind_since = t
        print(f"{mmss(t):>5} | {ov:>6}/{os_:<3}        {ev:>6}/{es_:<3}       "
              f"| {ratio:>4.2f} {sratio:>4.2f} | {oup:>2}/{eup:<2}{battle}{flag}")

    # 2) decisive engagements: 30s buckets where our army lost the most value
    print("\n--- engagements (our army value lost, 30s buckets) ---")
    buckets = []
    for t0 in range(0, length, 30):
        lv, lc = deaths_in(units, ours, t0, t0 + 30)
        ev_, ec = deaths_in(units, theirs, t0, t0 + 30)
        if lv >= 300 or ev_ >= 300:
            buckets.append((t0, lv, lc, ev_, ec))
    buckets.sort(key=lambda b: -(b[1]))
    for t0, lv, lc, ev_, ec in buckets[:6]:
        ov, os_, ocomp = alive_army(units, ours, t0)
        env, es_, ecomp = alive_army(units, theirs, t0)
        trade = (ev_ / lv) if lv else 9.9
        print(f"\n  {mmss(t0)}-{mmss(t0+30)}: we lost {lv} ({_fmt(lc)}); "
              f"they lost {ev_} ({_fmt(ec)})  trade={trade:.2f}")
        print(f"     going in -- us: {ov}v/{os_}s {_fmt(ocomp)}")
        print(f"                enemy: {env}v/{es_}s {_fmt(ecomp)}")

    # 3) composition + upgrades summary
    peak_t = max(marks, key=lambda t: alive_army(units, ours, t)[0]) if marks else length
    ov, os_, ocomp = alive_army(units, ours, peak_t)
    env, es_, ecomp = alive_army(units, theirs, peak_t)
    print(f"\n--- our peak army @ {mmss(peak_t)} ({ov}v/{os_}s) ---")
    print(f"  us:    {_fmt(ocomp)}")
    print(f"  enemy: {_fmt(ecomp)}")
    print(f"  our upgrades:   {[n for _, n in upgrades[ours]]}")
    print(f"  enemy upgrades: {[n for _, n in upgrades[theirs]]}")

    # 4) totals
    tot_lost, _ = deaths_in(units, ours, 0, length)
    tot_killed, _ = deaths_in(units, theirs, 0, length)
    print(f"\n--- game trade totals ---")
    print(f"  army value we lost: {tot_lost} | enemy army value we killed: {tot_killed}"
          f"  (overall trade {tot_killed/max(1,tot_lost):.2f})")
    print(f"  first fell behind on army ~ {mmss(behind_since) if behind_since else 'never'}")


def _fmt(counter):
    return ", ".join(f"{n}x{name}" for name, n in counter.most_common(6)) or "-"


if __name__ == "__main__":
    main()
