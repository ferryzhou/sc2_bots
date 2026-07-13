"""Self-test / demo for strategy_engine -- runnable without SC2.

    python -m strategy_engine.selftest

Exercises the modules against representative game states and asserts the
strategic model produces sensible recommendations, then prints an example digest.
"""

from __future__ import annotations

from .state import GameState
from .principles import Investment, PowerTiming, recommend_investment, power_timing
from .strategy import Archetype, classify_opponent
from .harassment import harass_advice
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
    )
    advice = StrategicAdvisor().advise(st)
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
