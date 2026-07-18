"""tactics: combat micro posture -- focus fire, kiting, retreat, target priority.

Mirrors ``COMBAT.md``. The engagement module decides *whether* to fight; this
module decides *how* -- concentrate fire to reduce enemy DPS, retreat damaged
units to preserve value, prioritize targets, and gather into a ball before
committing so we don't feed units in piecemeal.

Framework-agnostic: returns a tactical posture any bot can translate into unit
orders. The bot still issues the actual sc2 orders (targeting, move, abilities)
because those are API-specific; the *decision* of which posture to adopt comes
from here so all bots share the same combat brain. A bot that ignores this and
pure a-moves will lose even fights to an opponent that focus-fires and kites --
this is the gap between a macro bot and a competitive one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .state import GameState
from .principles import PowerTiming, TradeVerdict, assess_efficiency
from .combat import Engagement, EngagementAdvice


@dataclass
class Tactics:
    """Combat micro posture: how to fight the current engagement."""

    focus_fire: bool = True                # concentrate fire to kill units fast
    target_priority: str = "closest"       # "closest" | "expensive" | "support" | "air"
    kite_low_hp: bool = False              # retreat units below retreat_threshold
    retreat_threshold: float = 0.33        # hp fraction below which to pull back
    preserve_units: bool = False           # avoid trades; keep the army for later
    concentrate_before_commit: bool = True  # gather into a ball before attacking
    commit_ratio: float = 0.6              # fraction of army gathered before committing
    use_abilities: bool = True             # cast race abilities (force field, blink, etc.)
    reasons: List[str] = field(default_factory=list)


def recommend_tactics(state: GameState, engagement: EngagementAdvice,
                      timing: PowerTiming) -> Tactics:
    """Decide the combat posture: aggressive focus-fire or careful preservation.

    The posture flows from the engagement verdict, the power timing, and the trade
    trend. When we're ahead now or the fight is favorable, focus-fire to close out
    the kill (reduce their DPS fastest). When we're ahead later or avoiding,
    preserve units -- kite back damaged ones, don't take coinflip trades. Trading
    down always raises the retreat threshold so we stop feeding value into a
    losing fight.
    """
    t = Tactics()
    eng = engagement.verdict
    trade = assess_efficiency(state).verdict

    # --- Preserve / avoid posture -------------------------------------------
    if eng == Engagement.AVOID or timing == PowerTiming.AHEAD_LATER:
        t.preserve_units = True
        t.kite_low_hp = True
        t.retreat_threshold = 0.5
        t.concentrate_before_commit = True
        t.commit_ratio = 0.75  # gather more before committing -- don't feed piecemeal
        t.reasons.append("avoiding fights: preserve units, retreat damaged, gather fully")

    # --- Trading down: stop feeding value -----------------------------------
    if trade == TradeVerdict.TRADING_DOWN:
        t.kite_low_hp = True
        t.retreat_threshold = 0.6
        t.preserve_units = True
        t.reasons.append("trading down: retreat damaged units early to stop the bleed")

    # --- Favorable fight: focus fire to close out ---------------------------
    if eng == Engagement.ENGAGE or timing == PowerTiming.AHEAD_NOW:
        t.focus_fire = True
        t.preserve_units = False
        t.retreat_threshold = 0.25  # fight to the death -- every shot lands
        t.reasons.append("favorable fight: focus fire to drop enemy DPS fast")

    # --- Defending at home: use abilities, hold the line --------------------
    if state.fighting_at_home:
        t.use_abilities = True
        t.commit_ratio = 0.5  # commit sooner -- defender's advantage covers us
        t.reasons.append("fighting at home: use abilities, commit sooner (defender's advantage)")

    # --- Target priority by enemy composition -------------------------------
    if state.enemy_massing_light:
        t.target_priority = "closest"
        t.reasons.append("enemy massing light: kill closest first to break the surround")
    elif state.enemy_has_air:
        t.target_priority = "air"
        t.reasons.append("enemy has air: prioritize anti-air before it kills us")
    elif engagement.effective_ratio >= 1.2:
        t.target_priority = "expensive"
        t.reasons.append("ahead: focus expensive targets to maximize value killed")

    return t
