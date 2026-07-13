"""rules: the concrete, checkable rules from ``RULES.md`` as predicates.

Each rule is a small pure function ``GameState -> RuleHit | None``. A hit means
the rule fired and carries a concrete recommendation the bot can act on. Numbers
match the defaults in ``RULES.md`` and are easy to tune here in one place.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from .state import GameState


@dataclass
class RuleHit:
    rule: str          # short id, e.g. "build_worker"
    action: str        # what to do
    detail: str        # why, with the numbers that triggered it


Rule = Callable[[GameState], Optional[RuleHit]]


# --- 1. Never stop producing workers ---------------------------------------
def rule_build_worker(state: GameState) -> Optional[RuleHit]:
    ideal = 22 * state.base_count
    if state.worker_count < ideal:
        return RuleHit(
            "build_worker",
            "train a worker",
            f"workers {state.worker_count} < ideal {ideal} (~22 per base)",
        )
    return None


# --- 2. Don't get supply blocked -------------------------------------------
def rule_build_supply(state: GameState) -> Optional[RuleHit]:
    threshold = 2 + 2 * state.production_structures
    if state.supply_cap >= 200:
        return None
    if state.supply_left <= threshold and state.pending_supply == 0:
        return RuleHit(
            "build_supply",
            "build a supply structure",
            f"supply_left {state.supply_left} <= threshold {threshold}, none pending",
        )
    return None


# --- 3. Spend your resources -- don't float --------------------------------
def rule_stop_floating(state: GameState) -> Optional[RuleHit]:
    if state.minerals > 400:
        return RuleHit(
            "stop_floating_minerals",
            "add production or expand",
            f"floating minerals {state.minerals} > 400",
        )
    if state.vespene > 300:
        return RuleHit(
            "stop_floating_gas",
            "spend gas on tech/upgrades or gas-heavy units",
            f"floating gas {state.vespene} > 300",
        )
    return None


# --- 4. Expand -------------------------------------------------------------
def rule_expand(state: GameState) -> Optional[RuleHit]:
    saturated = state.worker_count >= 0.9 * 22 * state.base_count
    safe = not (state.enemy_army_moving_out or state.incoming_harass)
    if saturated and safe:
        return RuleHit(
            "expand",
            "take a new base",
            f"near saturation ({state.worker_count} workers on {state.base_count} bases) and safe",
        )
    return None


# --- 5. Scout constantly ---------------------------------------------------
def rule_scout(state: GameState) -> Optional[RuleHit]:
    if state.scouting_stale:
        return RuleHit(
            "scout",
            "send/refresh a scout",
            "no fresh scouting information (never scouted or >45s stale)",
        )
    return None


# --- 6. Keep production saturated ------------------------------------------
def rule_add_production(state: GameState) -> Optional[RuleHit]:
    if state.idle_production == 0 and state.minerals > 300 and state.production_structures >= 1:
        return RuleHit(
            "add_production",
            "add a production building",
            f"no idle production but floating minerals {state.minerals}",
        )
    if state.idle_production > 0:
        return RuleHit(
            "use_production",
            "queue units -- production is idle",
            f"{state.idle_production} production building(s) idle with money",
        )
    return None


# --- 10. Tech and upgrades -------------------------------------------------
def rule_start_upgrades(state: GameState) -> Optional[RuleHit]:
    if state.base_count >= 2 and state.upgrades_in_progress == 0 and state.upgrade_structures >= 1:
        return RuleHit(
            "start_upgrades",
            "start an attack/armor upgrade",
            "natural is up and an upgrade structure is idle",
        )
    if state.idle_upgrade_structures > 0:
        return RuleHit(
            "use_upgrade_structure",
            "start research -- upgrade structure idle",
            f"{state.idle_upgrade_structures} upgrade structure(s) idle with gas",
        )
    return None


def rule_react_to_tech(state: GameState) -> Optional[RuleHit]:
    if state.enemy_has_cloak:
        return RuleHit(
            "get_detection",
            "build detection now",
            "enemy cloak/burrow tech scouted -- prepare detection before it lands",
        )
    if state.enemy_has_air:
        return RuleHit(
            "get_antiair",
            "add anti-air",
            "enemy air tech scouted -- prepare anti-air before it lands",
        )
    return None


ALL_RULES: List[Rule] = [
    rule_build_worker,
    rule_build_supply,
    rule_stop_floating,
    rule_expand,
    rule_scout,
    rule_add_production,
    rule_start_upgrades,
    rule_react_to_tech,
]


def evaluate_rules(state: GameState, rules: Optional[List[Rule]] = None) -> List[RuleHit]:
    """Run every rule and return the ones that fired, in rule order."""
    rules = rules if rules is not None else ALL_RULES
    hits: List[RuleHit] = []
    for rule in rules:
        hit = rule(state)
        if hit is not None:
            hits.append(hit)
    return hits
