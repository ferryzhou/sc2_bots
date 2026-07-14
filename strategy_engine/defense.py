"""defense: the library's answer to "we're being rushed -- what do we do?"

Keeps the *decision* (are we under an all-in, and how hard to defend) in the
strategy library so bots don't hard-code it. A bot reads the ``DefensePlan`` and
translates the abstract measures (static defense, prioritize army, hold, pull
workers) into its own race's concrete actions.

Mirrors the defensive half of ``STRATEGY.md`` / ``COMBAT.md``: survive the all-in
on defender's advantage, then punish the dead economy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .state import GameState
from .strategy import classify_opponent, Archetype


@dataclass
class DefensePlan:
    emergency: bool          # under a rush/all-in that needs an immediate response
    static_defense: int      # how many static-defense structures we should have up
    prioritize_army: bool    # army/defense before economy and expansion
    hold_position: bool      # keep the army home -- do not move out
    pull_workers: bool       # base is breached -- pull workers into the fight
    need_detection: bool     # cloak/burrow threat and no detection on hand
    reasons: List[str] = field(default_factory=list)


def assess_defense(state: GameState) -> DefensePlan:
    """Recommend a defensive response from the scouted threat and our strength.

    Emergency = an all-in/rush is detected (or aggression is visible from home)
    and we are not clearly ahead in army to absorb it. Severity scales the static
    defense; a breached base with too little army triggers a worker pull.
    """
    cls = classify_opponent(state)
    arch = cls.archetype
    minutes = state.game_minutes
    reasons: List[str] = []

    detected_allin = arch in (Archetype.CHEESE_ALLIN, Archetype.TIMING_ATTACK)
    home_aggression = state.enemy_proxy or (state.enemy_army_moving_out and minutes < 6.0)

    # Are we clearly strong enough to just fight it with the army we have?
    enemy_army = state.enemy_army_supply if state.enemy_army_supply is not None else 8.0
    outmatched = state.army_supply < enemy_army * 1.2

    emergency = (detected_allin or home_aggression) and (minutes < 7.0) and outmatched
    if emergency:
        if detected_allin:
            reasons.append(f"all-in read ({arch.value}) while we're not ahead in army")
        if home_aggression:
            reasons.append("aggression visible from home")

    # Severity -> how much static defense to want up. Replay analysis of Protoss
    # wins vs. rushes (analysis/REPLAY_FINDINGS.md) shows 2-4 cannons is the hold.
    static = 0
    if emergency:
        static = 2
        if arch == Archetype.CHEESE_ALLIN:
            static += 1
        if state.enemy_army_moving_out:
            static += 1
        if state.enemy_proxy:
            static += 1
        static = min(static, 4)

    # Base breached and army can't hold it alone -> pull workers.
    breached = state.enemy_army_moving_out and minutes < 7.0
    pull_workers = breached and state.army_supply < enemy_army * 0.75
    if pull_workers:
        reasons.append("base breached with too little army -- pull workers to hold")

    need_detection = state.enemy_has_cloak and not state.have_detection
    if need_detection:
        reasons.append("cloak/burrow threat without detection")

    return DefensePlan(
        emergency=emergency,
        static_defense=static,
        prioritize_army=emergency,
        hold_position=emergency,
        pull_workers=pull_workers,
        need_detection=need_detection,
        reasons=reasons,
    )
