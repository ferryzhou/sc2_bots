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
from .build_guides import BUILD_GUIDES, BuildExecutor, guides_for, get_build
from .advisor import StrategicAdvisor
from .macro import MacroPlan, recommend_macro
from .tactics import Tactics, recommend_tactics
from .composition import recommend_composition
from .spending import Want, plan_spend


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


def test_build_guides_loaded_and_reproducible() -> None:
    _check("build guides loaded from data", len(BUILD_GUIDES) >= 3)
    # every mapped step must carry a non-empty token; most steps map
    for b in BUILD_GUIDES.values():
        cov = b.coverage()
        _check(f"{b.id} has steps", cov["total"] > 0)
        _check(f"{b.id} is mostly reproducible", cov["fraction"] >= 0.8)
        for a in b.actions:
            if a.reproducible:
                _check(f"{b.id} step {a.index} has a token", bool(a.token))


def test_build_guide_reproduce_in_order() -> None:
    b = next((g for g in BUILD_GUIDES.values() if g.id == 184161), None)
    if b is None:
        b = list(BUILD_GUIDES.values())[0]
    ex = BuildExecutor(b)
    have: dict = {}
    first_tokens = []
    guard = 0
    while not ex.is_complete(have) and guard < 200:
        a = ex.next_action(have)
        key = a.token or a.name
        if len(first_tokens) < 3:
            first_tokens.append(key)
        have[key] = have.get(key, 0) + 1
        guard += 1
    _check("executor completes the scripted build", ex.is_complete(have))
    _check("executor reproduces steps in order",
           first_tokens == [(a.token or a.name)
                            for a in ex.actions[:3]])
    # is_due gates on supply/time targets
    a0 = ex.actions[0]
    _check("action not due before its supply",
           not BuildExecutor.is_due(a0, supply=(a0.at_supply or 99) - 5, seconds=0)
           if a0.at_supply else True)


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


def test_macro_scales_with_economy_and_float() -> None:
    # Early game: 1 base, low workers -> small target, low urgency.
    early = GameState(worker_count=14, base_count=1, minerals=100, production_structures=1)
    inv_early = recommend_investment(early)
    m_early = recommend_macro(early, inv_early)
    _check("early game: small target", m_early.target_production <= 5)
    _check("early game: low urgency", m_early.spend_urgency < 0.3)
    _check("early game: no force train", not m_early.force_train)

    # Saturated + floating: should demand much more production and force-train.
    big = GameState(worker_count=70, base_count=3, minerals=800,
                    production_structures=5, idle_production=2)
    inv_big = recommend_investment(big)
    m_big = recommend_macro(big, inv_big)
    _check("saturated + floating: target well above base",
           m_big.target_production >= 10)
    _check("floating hard: high urgency", m_big.spend_urgency >= 0.8)
    _check("idle production + high urgency: force train", m_big.force_train)
    _check("floating: allow parallel build", m_big.allow_parallel_build >= 2)
    _check("floating flag set when urgency high", m_big.floating)


def test_macro_worker_cap_scales_with_bases() -> None:
    one_base = GameState(worker_count=10, base_count=1, minerals=100)
    three_base = GameState(worker_count=60, base_count=3, minerals=100)
    m1 = recommend_macro(one_base, recommend_investment(one_base))
    m3 = recommend_macro(three_base, recommend_investment(three_base))
    _check("worker cap grows with bases", m3.worker_cap > m1.worker_cap)
    _check("worker cap hard-capped at 80", m3.worker_cap <= 80)


def test_macro_threat_adds_production() -> None:
    safe = GameState(worker_count=40, base_count=2, minerals=200)
    threatened = GameState(worker_count=40, base_count=2, minerals=200,
                           enemy_army_moving_out=True)
    m_safe = recommend_macro(safe, recommend_investment(safe))
    m_threat = recommend_macro(threatened, recommend_investment(threatened))
    _check("under threat: more production target",
           m_threat.target_production > m_safe.target_production)


def test_macro_base_target_grows_through_the_game() -> None:
    # army_supply set so the "don't out-expand the army" safety gate is satisfied.
    early = GameState(game_time=180, worker_count=20, base_count=1, minerals=100)
    mid = GameState(game_time=600, worker_count=44, base_count=2, minerals=100,
                    army_supply=30)
    late = GameState(game_time=1000, worker_count=60, base_count=3, minerals=100,
                     army_supply=40)
    m_early = recommend_macro(early, recommend_investment(early))
    m_mid = recommend_macro(mid, recommend_investment(mid))
    m_late = recommend_macro(late, recommend_investment(late))
    _check("base target grows into mid game", m_mid.base_target >= 3)
    _check("base target keeps growing late", m_late.base_target > m_mid.base_target)
    _check("base target never below current bases",
           m_early.base_target >= 1 and m_late.base_target >= 3)
    # behind the base target -> production is capped so minerals are left to expand
    m_behind = recommend_macro(mid, recommend_investment(mid))
    _check("behind base target caps production to save for the expo",
           m_behind.target_production <= 2 * 2 + 2)


def test_macro_does_not_expand_behind_a_thin_army() -> None:
    # saturated 2-base economy but almost no army -> hold at 2, don't walk a Nexus
    # into a timing attack. With an army to cover it, the 3rd is allowed.
    thin = GameState(game_time=540, worker_count=44, base_count=2, minerals=100,
                     army_supply=4)
    covered = GameState(game_time=540, worker_count=44, base_count=2, minerals=100,
                        army_supply=24)
    m_thin = recommend_macro(thin, recommend_investment(thin))
    m_covered = recommend_macro(covered, recommend_investment(covered))
    _check("thin army: hold base target at current", m_thin.base_target == 2)
    _check("covered army: allow the next base", m_covered.base_target >= 3)


def test_spending_priority_and_starvation() -> None:
    # bank 350: a blocking 400 Nexus is unaffordable, so a soft probe below it is
    # starved (banking toward the Nexus) -- the opening starvation fix.
    wants = [Want("NEXUS", 400, 0, blocking=True), Want("PROBE", 50, 0, blocking=False)]
    _check("blocking Nexus starves the probe while banking",
           plan_spend(350, 0, wants) == [])
    # bank 450: Nexus affordable, and the probe spends the surplus above it.
    _check("probe spends only the surplus above the Nexus",
           plan_spend(450, 0, wants) == ["NEXUS", "PROBE"])
    # a soft want unaffordable does NOT block a cheaper want below it.
    soft_wants = [Want("COLOSSUS", 300, 200, blocking=False),
                  Want("STALKER", 125, 50, blocking=True)]
    _check("a soft unaffordable want doesn't block lower wants",
           plan_spend(150, 60, soft_wants) == ["STALKER"])
    # gas is reserved independently of minerals.
    gas_wants = [Want("STORM", 0, 200, blocking=True), Want("ZEALOT", 100, 0, blocking=False)]
    _check("gas reservation doesn't block a mineral-only want",
           plan_spend(500, 100, gas_wants) == ["ZEALOT"])


def test_composition_transitions_tech_late() -> None:
    # early: no transition, no cap
    early = GameState(game_time=180, vespene=50, enemy_race="Zerg")
    c_early = recommend_composition(early)
    _check("early: no tech escalation", not c_early.escalate_tech)
    _check("early: no unit-share cap", c_early.max_unit_share == 1.0)
    # late vs Zerg with air + floating gas: splash, anti-air, escalate, and a cap
    late = GameState(game_time=1200, vespene=800, enemy_race="Zerg",
                     enemy_has_air=True, enemy_massing_light=True,
                     composition_favorable=False)
    c_late = recommend_composition(late)
    _check("late: need splash vs a ground flood", c_late.need_splash)
    _check("late: need anti-air vs air", c_late.need_anti_air)
    _check("late: escalate tech", c_late.escalate_tech)
    _check("late: cap the mono-unit share", c_late.max_unit_share < 1.0)
    # floating gas alone (past the opening) triggers escalation
    floated = GameState(game_time=600, vespene=500)
    _check("floating gas past the opening escalates",
           recommend_composition(floated).escalate_tech)


def test_tactics_favorable_focus_fire() -> None:
    from .combat import assess_engagement
    st = GameState(army_supply=30, enemy_army_supply=18)
    eng = assess_engagement(st)
    from .principles import power_timing
    t = recommend_tactics(st, eng, power_timing(st))
    _check("favorable fight: focus fire on", t.focus_fire)
    _check("favorable fight: not preserving", not t.preserve_units)
    _check("favorable fight: low retreat threshold", t.retreat_threshold <= 0.3)


def test_tactics_avoid_preserves_units() -> None:
    from .combat import assess_engagement
    from .principles import power_timing
    st = GameState(army_supply=10, enemy_army_supply=25)  # badly outnumbered
    eng = assess_engagement(st)
    t = recommend_tactics(st, eng, power_timing(st))
    _check("avoid: preserve units", t.preserve_units)
    _check("avoid: kite low hp", t.kite_low_hp)
    _check("avoid: high retreat threshold", t.retreat_threshold >= 0.5)


def test_tactics_trading_down_retreats_early() -> None:
    from .combat import assess_engagement
    from .principles import power_timing
    st = GameState(army_supply=20, enemy_army_supply=20,
                   value_killed=400, value_lost=1200)  # trading down
    eng = assess_engagement(st)
    t = recommend_tactics(st, eng, power_timing(st))
    _check("trading down: kite low hp", t.kite_low_hp)
    _check("trading down: preserve units", t.preserve_units)
    _check("trading down: retreat threshold high", t.retreat_threshold >= 0.6)


def test_tactics_target_priority_by_composition() -> None:
    from .combat import assess_engagement
    from .principles import power_timing
    # mass light enemy (Zerg ling flood): closest first
    st = GameState(army_supply=20, enemy_army_supply=15, enemy_massing_light=True)
    eng = assess_engagement(st)
    t = recommend_tactics(st, eng, power_timing(st))
    _check("mass light: target closest", t.target_priority == "closest")
    # enemy air: prioritize air
    st_air = GameState(army_supply=20, enemy_army_supply=15, enemy_has_air=True)
    eng_air = assess_engagement(st_air)
    t_air = recommend_tactics(st_air, eng_air, power_timing(st_air))
    _check("enemy air: target air", t_air.target_priority == "air")


def test_advisor_includes_macro_and_tactics() -> None:
    st = GameState(
        game_time=360, worker_count=60, base_count=3, minerals=500,
        supply_used=120, supply_cap=140, supply_left=20,
        army_supply=30, production_structures=5, idle_production=1,
        enemy_base_count=3, enemy_army_supply=20, last_scouted_time=350,
    )
    advice = StrategicAdvisor().advise(st)
    _check("advice includes MacroPlan", isinstance(advice.macro, MacroPlan))
    _check("advice includes Tactics", isinstance(advice.tactics, Tactics))
    _check("macro target is sensible", advice.macro.target_production >= 5)
    _check("tactics has a target priority", advice.tactics.target_priority in
           ("closest", "expensive", "support", "air"))
    _check("summary mentions macro and tactics", "macro:" in advice.summary()
           and "tactics:" in advice.summary())


def test_production_saturates_and_balances() -> None:
    from .production import ProductionState, plan_production, desired_gateways

    # facility count tracks mineral income: ~1500/min -> ~5 gates (1500/300).
    _check("gate target scales with income",
           desired_gateways(ProductionState(0, 0, 1500, 0, 0, bases=3, gateways=0,
                                            robos=0, stargates=0, ready_gateways=0,
                                            ready_robos=0, ready_stargates=0)) == 5)
    # capped at 2/base so gateways can't out-run the minerals that feed them
    # (over-building mineral sinks is what left gas floating).
    _check("gate target capped by bases",
           desired_gateways(ProductionState(0, 0, 5000, 0, 0, bases=1, gateways=0,
                                            robos=0, stargates=0, ready_gateways=0,
                                            ready_robos=0, ready_stargates=0)) == 2)
    # gas-sink facilities scale with GAS income so a fat gas bank gets spent:
    # ~1000 gas/min -> ~5 robo+stargate, split between them.
    from strategy_engine.production import desired_robos, desired_stargates
    gassy = ProductionState(0, 0, 2000, 1000, 0, bases=6, gateways=0, robos=0,
                            stargates=0, ready_gateways=0, ready_robos=0,
                            ready_stargates=0,
                            have_tech=frozenset({"ROBOTICSFACILITY", "STARGATE"}))
    _check("robo count grows with gas income", desired_robos(gassy, None) >= 3)
    _check("stargate count grows with gas income", desired_stargates(gassy, None) >= 3)

    # 3 ready warpgates, gas floating (900 gas, minerals to match): drain gas ->
    # all Stalkers, and add gateways toward the income target we don't yet have.
    st = ProductionState(minerals=600, vespene=900, mineral_income=1500,
                         vespene_income=600, supply_left=20, bases=3, gateways=3,
                         robos=0, stargates=0, ready_gateways=3, ready_robos=0,
                         ready_stargates=0, have_tech=frozenset({"CYBERNETICSCORE"}))
    plan = plan_production(st, comp=None)
    _check("floating gas -> gateways make the gas unit (Stalker)",
           plan.gateway_units == ["STALKER", "STALKER", "STALKER"])
    _check("adds gateways toward the income target", plan.add_gateways == 2)
    # only what we can afford NOW is issued (200 min -> a single Stalker); the rest
    # comes next step as income flows. Saturation is across steps, not one batch.
    st_poor = ProductionState(minerals=200, vespene=900, mineral_income=1500,
                              vespene_income=600, supply_left=20, bases=3, gateways=3,
                              robos=0, stargates=0, ready_gateways=3, ready_robos=0,
                              ready_stargates=0, have_tech=frozenset({"CYBERNETICSCORE"}))
    _check("issues only what's affordable now",
           plan_production(st_poor).gateway_units == ["STALKER"])

    # minerals piling, gas dry: make the pure-mineral unit (Zealot), no gas spent.
    st2 = ProductionState(minerals=900, vespene=20, mineral_income=1600,
                          vespene_income=50, supply_left=20, bases=3, gateways=6,
                          robos=0, stargates=0, ready_gateways=2, ready_robos=0,
                          ready_stargates=0, have_tech=frozenset({"CYBERNETICSCORE"}))
    _check("floating minerals -> Zealots (no gas)",
           plan_production(st2).gateway_units == ["ZEALOT", "ZEALOT"])

    # supply-capped: only 2 supply left fits exactly one 2-supply unit, not two.
    st3 = ProductionState(minerals=1000, vespene=1000, mineral_income=1500,
                          vespene_income=500, supply_left=2, bases=3, gateways=6,
                          robos=0, stargates=0, ready_gateways=3, ready_robos=0,
                          ready_stargates=0, have_tech=frozenset({"CYBERNETICSCORE"}))
    _check("supply cap limits the batch", len(plan_production(st3).gateway_units) == 1)

    # robo claims gas first and makes an Observer when detection is needed.
    st4 = ProductionState(minerals=1000, vespene=400, mineral_income=1500,
                          vespene_income=300, supply_left=20, bases=3, gateways=6,
                          robos=1, stargates=0, ready_gateways=0, ready_robos=1,
                          ready_stargates=0, need_observer=True,
                          have_tech=frozenset({"CYBERNETICSCORE", "ROBOTICSFACILITY"}))
    _check("robo builds an observer when detection is needed",
           plan_production(st4).robo_units == ["OBSERVER"])


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"running {len(tests)} strategy_engine checks...\n")
    for t in tests:
        print(t.__name__)
        t()
    print(f"\nall {len(tests)} checks passed.")


if __name__ == "__main__":
    main()
