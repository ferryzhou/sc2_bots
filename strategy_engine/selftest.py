"""Self-test / demo for strategy_engine -- runnable without SC2.

    python -m strategy_engine.selftest

Exercises the modules against representative game states and asserts the
strategic model produces sensible recommendations, then prints an example digest.
"""

from __future__ import annotations

from .state import GameState
from .principles import (
    Investment,
    PowerTiming,
    TradeVerdict,
    recommend_investment,
    power_timing,
    assess_efficiency,
)
from .strategy import Archetype, classify_opponent, counter_stance
from .harassment import harass_advice
from .combat import Engagement, assess_engagement
from .defense import assess_defense
from .information import estimate_enemy, project_enemy
from .rules import evaluate_rules
from .openings import (
    OPENINGS,
    Placement,
    OpeningExecutor,
    classify_opening,
    openings_for_race,
    best_opening,
    get_opening,
    verify_opening,
)
from .advisor import StrategicAdvisor


def _check(name: str, cond: bool) -> None:
    print(f"  [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def test_investment_prefers_economy_when_undersaturated() -> None:
    st = GameState(game_time=180, worker_count=14, base_count=1, production_structures=1, supply_left=5)
    adv = recommend_investment(st)
    _check("undersaturated -> economy is top priority", adv.top == Investment.ECONOMY)


def test_investment_supply_gate_first() -> None:
    st = GameState(worker_count=14, base_count=1, production_structures=2, supply_left=2, supply_cap=30)
    adv = recommend_investment(st)
    _check("about to be supply blocked -> supply first", adv.top == Investment.SUPPLY)


def test_investment_army_under_threat() -> None:
    st = GameState(worker_count=30, base_count=2, supply_left=8, enemy_army_moving_out=True)
    adv = recommend_investment(st)
    _check("under threat -> army first, posture safe",
           adv.top == Investment.ARMY and adv.posture == "safe")


def test_power_timing() -> None:
    now = GameState(army_supply=20, base_count=1, enemy_army_supply=10, enemy_base_count=1)
    later = GameState(army_supply=10, base_count=3, enemy_army_supply=10, enemy_base_count=1)
    unknown = GameState(army_supply=10)
    _check("army lead -> ahead now", power_timing(now) == PowerTiming.AHEAD_NOW)
    _check("economy lead -> ahead later", power_timing(later) == PowerTiming.AHEAD_LATER)
    _check("no scouting -> unknown", power_timing(unknown) == PowerTiming.UNKNOWN)


def test_efficiency_trading() -> None:
    up = GameState(value_killed=2000, value_lost=800)
    down = GameState(value_killed=600, value_lost=1500)
    unknown = GameState(value_killed=0, value_lost=0)
    _check("kill more than lost -> trading up",
           assess_efficiency(up).verdict == TradeVerdict.TRADING_UP)
    _check("trading up -> should seek fights", assess_efficiency(up).should_seek_fights)
    _check("lose more than killed -> trading down",
           assess_efficiency(down).verdict == TradeVerdict.TRADING_DOWN)
    _check("trading down -> should avoid fights", assess_efficiency(down).should_avoid_fights)
    _check("no fights yet -> unknown",
           assess_efficiency(unknown).verdict == TradeVerdict.UNKNOWN)


def test_efficiency_idle_waste() -> None:
    st = GameState(value_killed=1000, value_lost=500, minerals=800, idle_production=2)
    _check("floating money / idle production -> idle_waste flagged",
           assess_efficiency(st).idle_waste)


def test_engagement_favorable() -> None:
    st = GameState(army_supply=30, enemy_army_supply=20)
    _check("bigger army -> engage", assess_engagement(st).verdict == Engagement.ENGAGE)


def test_engagement_unfavorable_avoid() -> None:
    st = GameState(army_supply=12, enemy_army_supply=24)
    _check("much smaller army in the open -> avoid",
           assess_engagement(st).verdict == Engagement.AVOID)


def test_engagement_defend_at_home() -> None:
    st = GameState(army_supply=16, enemy_army_supply=20, fighting_at_home=True,
                   have_terrain_advantage=True)
    v = assess_engagement(st).verdict
    _check("behind but defender's advantage -> engage or defend, not avoid",
           v in (Engagement.DEFEND, Engagement.ENGAGE))


def test_engagement_upgrade_edge_flips_it() -> None:
    even = GameState(army_supply=20, enemy_army_supply=20, upgrades_done=0, enemy_upgrades=0)
    upg = GameState(army_supply=20, enemy_army_supply=20, upgrades_done=6, enemy_upgrades=0)
    _check("equal armies, no upgrades -> not a clear engage",
           assess_engagement(even).verdict != Engagement.ENGAGE)
    _check("equal armies but big upgrade edge -> engage",
           assess_engagement(upg).verdict == Engagement.ENGAGE)


def test_engagement_unknown_without_scouting() -> None:
    _check("no enemy army info -> unknown",
           assess_engagement(GameState(army_supply=20)).verdict == Engagement.UNKNOWN)


def test_engagement_trading_down_vetoes() -> None:
    st = GameState(army_supply=26, enemy_army_supply=20, value_killed=400, value_lost=1200)
    _check("favorable size but trading down -> don't engage",
           assess_engagement(st).verdict != Engagement.ENGAGE)


def test_estimate_fresh_and_never_seen() -> None:
    fresh = GameState(game_time=300, last_scouted_time=290,
                      enemy_base_count=3, enemy_army_supply=20)
    e = estimate_enemy(fresh)
    _check("fresh sighting -> is_fresh", e.is_fresh and e.army_supply == 20)
    never = GameState(game_time=200)
    _check("never seen -> no data, zero confidence",
           not estimate_enemy(never).has_data and estimate_enemy(never).confidence == 0.0)


def test_estimate_dead_reckons_forward() -> None:
    st = GameState(game_time=360, last_scouted_time=240,  # 2 min stale
                   enemy_base_count=3, enemy_army_supply=20,
                   enemy_production_structures=4, enemy_worker_count=40)
    e = estimate_enemy(st)
    _check("stale sighting -> projected (not fresh)", not e.is_fresh)
    _check("projected army grew above last sighting", e.army_supply > 20)
    _check("confidence decayed below 1", e.confidence < 1.0)


def test_advisor_degrades_gracefully_when_stale() -> None:
    # A sighting 2 minutes ago: without projection this would classify UNKNOWN.
    st = GameState(game_time=360, last_scouted_time=240,
                   army_supply=25, enemy_base_count=3, enemy_army_supply=6,
                   enemy_worker_count=50, enemy_production_structures=2)
    advice = StrategicAdvisor().advise(st)
    _check("stale enemy read is projected, not UNKNOWN",
           advice.classification.archetype != Archetype.UNKNOWN)
    _check("advice flags the read as projected", not advice.enemy_estimate.is_fresh)
    # but we should still be told to re-scout
    _check("stale state still triggers the scout rule",
           any(h.rule == "scout" for h in advice.rule_hits))


def test_classify_cheese() -> None:
    st = GameState(
        game_time=150, last_scouted_time=150,
        enemy_base_count=1, enemy_worker_count=10, enemy_proxy=True,
        enemy_army_moving_out=True,
    )
    _check("one base + proxy + early aggression -> cheese",
           classify_opponent(st).archetype == Archetype.CHEESE_ALLIN)


def test_defense_plan_on_rush() -> None:
    # Scouted 4-gate / one-base aggression -> emergency defense from the library.
    st = GameState(game_time=110, last_scouted_time=105, army_supply=2,
                   enemy_base_count=1, enemy_production_structures=3, enemy_gas_count=0)
    d = assess_defense(st)
    _check("rush read -> emergency", d.emergency)
    _check("rush -> wants static defense", d.static_defense >= 1)
    _check("rush -> army before economy", d.prioritize_army and d.hold_position)


def test_defense_pull_workers_when_breached() -> None:
    st = GameState(game_time=120, last_scouted_time=118, army_supply=1,
                   enemy_base_count=1, enemy_production_structures=4,
                   enemy_army_supply=8, enemy_army_moving_out=True)
    _check("breached with no army -> pull workers", assess_defense(st).pull_workers)


def test_no_defense_emergency_when_safe() -> None:
    # Standard macro opponent, we have an army -> no emergency.
    st = GameState(game_time=420, last_scouted_time=410, army_supply=30,
                   enemy_base_count=3, enemy_worker_count=50, enemy_army_supply=20,
                   enemy_production_structures=2)
    _check("safe macro game -> no defense emergency", not assess_defense(st).emergency)


def test_detect_four_gate_from_partial_scout() -> None:
    # Regression: a realistic early scout of a 4-gate zealot all-in used to be
    # misread as "standard" (see analysis of the lishimin loss). It must now be
    # caught as aggression from partial info.
    scouted = GameState(game_time=135, last_scouted_time=130, army_supply=2,
                        enemy_base_count=1, enemy_worker_count=16,
                        enemy_production_structures=3, enemy_gas_count=0)
    c = classify_opponent(scouted)
    _check("scout @2:00 (1 base, 3 gates, no gas) -> timing attack",
           c.archetype == Archetype.TIMING_ATTACK)
    _check("4-gate read yields a defensive counter",
           counter_stance(c).posture == "defensive")

    moving = GameState(game_time=200, last_scouted_time=195, army_supply=5,
                       enemy_base_count=1, enemy_production_structures=3,
                       enemy_army_moving_out=True)
    _check("one base + army moving out -> timing attack",
           classify_opponent(moving).archetype == Archetype.TIMING_ATTACK)


def test_detect_proxy_without_base_scout() -> None:
    # A proxy / warp-in pylon near our base must raise an all-in alarm even when
    # we never scouted the enemy's base (used to return UNKNOWN).
    st = GameState(game_time=210, army_supply=5, enemy_proxy=True)
    c = classify_opponent(st)
    _check("proxy near home without a base scout -> cheese/all-in",
           c.archetype == Archetype.CHEESE_ALLIN)
    _check("proxy alarm yields a defensive counter",
           counter_stance(c).posture == "defensive")


def test_no_false_alarm_on_standard_opener() -> None:
    # A normal one-base opening about to expand must NOT be flagged as an all-in.
    st = GameState(game_time=150, last_scouted_time=148, army_supply=4,
                   enemy_base_count=1, enemy_worker_count=18,
                   enemy_production_structures=1, enemy_gas_count=1)
    _check("normal 1-base-into-expand -> standard, not an all-in",
           classify_opponent(st).archetype == Archetype.STANDARD)


def test_classify_greedy_and_counter() -> None:
    st = GameState(
        game_time=240, last_scouted_time=240, army_supply=12,
        enemy_base_count=3, enemy_worker_count=50, enemy_army_supply=4,
        enemy_production_structures=2,
    )
    cls = classify_opponent(st)
    _check("3 bases + light army -> greedy", cls.archetype == Archetype.GREEDY_ECO)


def test_classify_unknown_without_scouting() -> None:
    st = GameState(game_time=200)  # never scouted
    _check("no scouting -> unknown archetype",
           classify_opponent(st).archetype == Archetype.UNKNOWN)


def test_harass_greedy_opponent() -> None:
    st = GameState(
        army_supply=15, has_harass_units=True,
        enemy_army_supply=5, enemy_base_count=3,
        last_scouted_time=0, game_time=0,
    )
    _check("harass units vs greedy enemy -> should harass",
           harass_advice(st).should_harass)


def test_harass_defense() -> None:
    st = GameState(incoming_harass=True, undefended_expansions=1)
    adv = harass_advice(st)
    _check("incoming harass -> should defend with warning against over-commit",
           adv.should_defend and any("over-commit" in w for w in adv.warnings))


def test_rules_fire() -> None:
    st = GameState(worker_count=5, base_count=1, production_structures=1, supply_left=1)
    ids = {h.rule for h in evaluate_rules(st)}
    _check("low workers -> build_worker rule fires", "build_worker" in ids)
    _check("low supply -> build_supply rule fires", "build_supply" in ids)
    _check("never scouted -> scout rule fires", "scout" in ids)


def test_openings_registry_loaded() -> None:
    _check("openings registry loaded from data", len(OPENINGS) >= 6)
    for race in ("Protoss", "Terran", "Zerg"):
        _check(f"{race} has at least one opening", len(openings_for_race(race)) >= 1)
    _check("best Protoss opening is the standard gate-expand",
           best_opening("Protoss").name == "protoss_gate_expand")


def test_openings_classify() -> None:
    # greedy Zerg hatch-before-pool
    fam = classify_opening("Zerg",
                           [("Hatchery", 95, "natural"), ("SpawningPool", 130, "main")],
                           first_gas=105, expand_time=95)
    _check("hatch-before-pool classifies as hatch_first", fam == "zerg_hatch_first")
    # forward pylon+gateway = proxy
    fam = classify_opening("Protoss",
                           [("Pylon", 48, "forward"), ("Gateway", 80, "forward")],
                           first_gas=None, expand_time=None)
    _check("forward buildings classify as proxy", fam == "protoss_proxy")
    # standard rax-expand
    fam = classify_opening("Terran",
                           [("Barracks", 75, "ramp_wall"), ("CommandCenter", 180, "natural")],
                           first_gas=91, expand_time=180)
    _check("terran natural in window -> rax_expand", fam == "terran_rax_expand")


def test_openings_reproduce() -> None:
    op = best_opening("Protoss")
    ex = OpeningExecutor(op)
    have: dict = {}
    order = []
    # walk the whole build; first step should be the first modal structure
    guard = 0
    while not ex.is_complete(have) and guard < 50:
        step = ex.next_step(have)
        order.append(step.structure)
        have[step.structure] = have.get(step.structure, 0) + 1
        guard += 1
    _check("executor reproduces the modal order",
           order[:3] == [s.structure for s in op.steps[:3]])
    _check("executor completes the opening", ex.is_complete(have))
    _check("executor progress is 1.0 when complete", ex.progress(have) == 1.0)
    # placements are usable zones
    first = op.steps[0]
    _check("first step carries a placement zone", isinstance(first.placement, Placement))


def test_openings_verify() -> None:
    op = get_opening("zerg_hatch_first")
    # a telemetry that follows the opening -> few/no major deviations
    good = {
        "buildings": [{"t": s.at_second or 60, "s": s.structure,
                       "zone": s.placement.value} for s in op.steps],
        "economy": {m: {k: (b["median"] if (b := op.economy[m].get(k)) else 0)
                        for k in ("workers", "supply", "mins_rate")}
                    for m in op.economy},
        "units": {},
    }
    devs = verify_opening(op, good)
    majors = [d for d in devs if d.severity == "major"]
    _check("following the opening yields no MAJOR deviations", not majors)
    # a pool-rush telemetry checked against hatch_first -> flags a missing hatch
    bad = {"buildings": [{"t": 39, "s": "SpawningPool", "zone": "main"}],
           "economy": {}, "units": {}}
    devs = verify_opening(op, bad)
    _check("wrong opening flags a missing structure",
           any(d.category == "missing" for d in devs))


def test_advisor_end_to_end() -> None:
    st = GameState(
        game_time=240, last_scouted_time=235,
        worker_count=28, base_count=2, minerals=250, vespene=120,
        supply_used=60, supply_cap=70, supply_left=10,
        army_supply=18, production_structures=4, upgrade_structures=1,
        enemy_base_count=3, enemy_worker_count=48, enemy_army_supply=6,
        enemy_production_structures=2, has_harass_units=True,
        value_killed=1800, value_lost=700,
    )
    advice = StrategicAdvisor().advise(st)
    _check("advisor returns an efficiency read", advice.efficiency is not None)
    _check("advisor returns a classification", advice.classification is not None)
    _check("advisor summary is non-empty", len(advice.summary()) > 0)
    print("\n--- example advice digest ---")
    print(advice.summary())
    print("-----------------------------")


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"running {len(tests)} strategy_engine checks...\n")
    for t in tests:
        print(t.__name__)
        t()
    print(f"\nall {len(tests)} checks passed.")


if __name__ == "__main__":
    main()
