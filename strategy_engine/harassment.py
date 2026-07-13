"""harassment: harass and anti-harass decisions.

Mirrors the harassment sections of the docs. Harassment attacks the *investment*
(economy, tech, production) rather than trading in a main fight. Two directions:
whether to harass (and how much to commit), and whether/how to defend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .state import GameState


@dataclass
class HarassAdvice:
    should_harass: bool
    harass_reasons: List[str] = field(default_factory=list)
    should_defend: bool = False
    defend_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def harass_advice(state: GameState) -> HarassAdvice:
    """Decide whether to harass and whether to shore up against harassment.

    Attacking side: harass is worthwhile when we have mobile units to spare and
    the enemy is greedy (thin army) or we want to cover our own transition.
    Defending side: cover vulnerable spots, but never over-commit to chasing.
    """
    advice = HarassAdvice(should_harass=False)

    # --- Attacking: should we harass? ---------------------------------------
    if state.has_harass_units:
        enemy_greedy = (
            state.enemy_army_supply is not None
            and state.enemy_army_supply + 3 < state.army_supply
        )
        enemy_many_bases = (
            state.enemy_base_count is not None and state.enemy_base_count >= 3
        )
        if enemy_greedy or enemy_many_bases:
            advice.should_harass = True
            advice.harass_reasons.append(
                "enemy is greedy/economic -- harass the thin-army window to kill "
                "workers or force pulls at low commitment"
            )
        # Harass to cover our own greed while the enemy is occupied.
        if state.worker_count < 0.85 * 22 * state.base_count and not state.incoming_harass:
            advice.should_harass = True
            advice.harass_reasons.append(
                "harass to buy tempo for our own expand/tech behind the pressure"
            )
        if advice.should_harass:
            advice.warnings.append(
                "commit only a small mobile detachment -- retreat when defense "
                "arrives; judge by return (workers killed, tech delayed)"
            )

    # --- Defending: are we exposed to harassment? ---------------------------
    if state.incoming_harass:
        advice.should_defend = True
        advice.defend_reasons.append(
            "raiders inbound/in base: pull threatened workers, then resume mining"
        )
    if state.undefended_expansions > 0:
        advice.should_defend = True
        advice.defend_reasons.append(
            f"{state.undefended_expansions} base(s) without defense/detection -- "
            "pre-place static defense at vulnerable spots"
        )
    if state.enemy_has_air or state.enemy_has_cloak:
        advice.should_defend = True
        advice.defend_reasons.append(
            "enemy air/cloak scouted -- get detection/anti-air covering worker "
            "lines before the raid lands"
        )
    if advice.should_defend:
        advice.warnings.append(
            "do not over-commit: keep a small holding force, never chase raiders "
            "with the main army or let harass stall your macro"
        )

    return advice
