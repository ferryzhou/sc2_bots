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
from .strategy import Archetype, classify_opponent
from .harassment import harass_advice
from .combat import Engagement, assess_engagement
from .rules import evaluate_rules
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


def test_classify_cheese() -> None:
    st = GameState(
        game_time=150, last_scouted_time=150,
        enemy_base_count=1, enemy_worker_count=10, enemy_proxy=True,
        enemy_army_moving_out=True,
    )
    _check("one base + proxy + early aggression -> cheese",
           classify_opponent(st).archetype == Archetype.CHEESE_ALLIN)


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
