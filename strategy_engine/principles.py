"""principles: the economy / army / tech investment tension and timing.

Mirrors ``PRINCIPLES.md``. Two exports:

- ``recommend_investment(state)`` -- where the next resources should lean, across
  the three competing claims (economy, army, tech/upgrades), given safety.
- ``power_timing(state)`` -- are we stronger now or later, relative to the enemy?
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from .state import GameState


class Investment(Enum):
    """The three competing claims on every resource, plus supply as a gate."""

    SUPPLY = "supply"      # unblock production first -- a hard prerequisite
    ECONOMY = "economy"    # workers, expansions -- stronger later
    ARMY = "army"          # units now -- stronger now
    TECH = "tech"          # tech/upgrades -- stronger later, unlocks options


class PowerTiming(Enum):
    AHEAD_NOW = "ahead_now"        # use the lead before it expires
    AHEAD_LATER = "ahead_later"    # survive until the investment pays off
    EVEN = "even"
    UNKNOWN = "unknown"            # not enough scouting to say


@dataclass
class InvestmentAdvice:
    priority: List[Investment]  # ordered, highest priority first
    reasons: List[str]
    posture: str  # "safe" | "standard" | "greedy" | "aggressive"

    @property
    def top(self) -> Investment:
        return self.priority[0]


def _worker_saturation(state: GameState) -> float:
    """Fraction of the ideal worker count we have (~22 per base)."""
    ideal = max(1, 22 * state.base_count)
    return state.worker_count / ideal


def recommend_investment(state: GameState) -> InvestmentAdvice:
    """Order the investment claims by what the game state most needs next.

    Encodes the core tension: economy and tech are bets on *later* that leave you
    thinner *now*; army is strength now. Supply is a gate that comes before all of
    them (idle production is wasted resources).
    """
    reasons: List[str] = []
    priority: List[Investment] = []

    # 1. Supply is a hard gate -- being blocked wastes everything downstream.
    supply_threshold = 2 + 2 * state.production_structures
    if state.supply_left <= supply_threshold and state.supply_cap < 200:
        priority.append(Investment.SUPPLY)
        reasons.append(
            f"supply_left {state.supply_left} <= threshold {supply_threshold}: "
            "unblock production before spending elsewhere"
        )

    saturation = _worker_saturation(state)
    under_threat = state.enemy_army_moving_out or state.incoming_harass

    # 2. Posture from the economy-vs-army tension, gated by safety (greed risk).
    if under_threat:
        posture = "safe"
        priority += [Investment.ARMY, Investment.SUPPLY, Investment.ECONOMY, Investment.TECH]
        reasons.append("enemy pressure detected: invest in army/defense now, delay greed")
    elif saturation < 0.85:
        # Economy not yet paying off; workers are the highest-return investment
        # while it is safe to take them.
        posture = "greedy" if saturation < 0.6 else "standard"
        priority += [Investment.ECONOMY, Investment.ARMY, Investment.TECH]
        reasons.append(
            f"worker saturation {saturation:.0%} < 100%: economy is the best "
            "return while safe"
        )
    else:
        # Saturated and safe: convert the economy into army and tech.
        posture = "standard"
        priority += [Investment.ARMY, Investment.TECH, Investment.ECONOMY]
        reasons.append("saturated and safe: convert economy into army and tech")

    # 3. Tech/upgrade nudge: if upgrade structures sit idle with gas, raise tech.
    if state.idle_upgrade_structures > 0 or (state.vespene > 300 and state.upgrades_in_progress == 0):
        if Investment.TECH in priority:
            priority.remove(Investment.TECH)
        # place tech right after any supply gate
        insert_at = 1 if priority and priority[0] == Investment.SUPPLY else 0
        priority.insert(insert_at, Investment.TECH)
        reasons.append("idle upgrade capacity or floating gas: spend on tech/upgrades")

    # De-duplicate while preserving order.
    seen = set()
    ordered = []
    for inv in priority:
        if inv not in seen:
            ordered.append(inv)
            seen.add(inv)
    # Ensure all four claims appear so callers always get a full ordering.
    for inv in (Investment.ECONOMY, Investment.ARMY, Investment.TECH, Investment.SUPPLY):
        if inv not in seen:
            ordered.append(inv)
            seen.add(inv)

    return InvestmentAdvice(priority=ordered, reasons=reasons, posture=posture)


def power_timing(state: GameState) -> PowerTiming:
    """Are we stronger now or later, relative to the enemy?

    "Ahead now" = more army on the field; "ahead later" = more economy that will
    out-produce. The practical read from ``PRINCIPLES.md``: if ahead now, use it;
    if ahead later, survive until then.
    """
    if state.enemy_army_supply is None and state.enemy_base_count is None:
        return PowerTiming.UNKNOWN

    army_edge = 0.0
    if state.enemy_army_supply is not None:
        army_edge = state.army_supply - state.enemy_army_supply

    eco_edge = 0
    if state.enemy_base_count is not None:
        eco_edge = state.base_count - state.enemy_base_count

    # Meaningful army lead now.
    if army_edge >= 4 and eco_edge <= 0:
        return PowerTiming.AHEAD_NOW
    # Economy lead that pays off later, without a current army lead.
    if eco_edge >= 1 and army_edge <= 2:
        return PowerTiming.AHEAD_LATER
    if army_edge >= 4 and eco_edge >= 1:
        # Ahead on both -- treat as "now" so the lead gets used before it fades.
        return PowerTiming.AHEAD_NOW
    return PowerTiming.EVEN
