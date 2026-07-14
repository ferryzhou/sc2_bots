"""combat: the should-engage decision.

Mirrors ``COMBAT.md``. A battle is decided less by raw supply than by how much of
each army's damage lands, so this weighs relative army strength together with the
structural and situational levers from the docs: tech/upgrade edge (efficiency
bought in advance), terrain, defender's advantage, reinforcements, composition,
and unmet detection needs. It also folds in the trade trend from
``assess_efficiency`` -- if we are already trading down, don't feed more.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .state import GameState
from .principles import assess_efficiency, TradeVerdict


class Engagement(Enum):
    ENGAGE = "engage"    # favorable -- seek/take the fight
    DEFEND = "defend"    # hold at home; defender's advantage covers a deficit
    AVOID = "avoid"      # unfavorable -- disengage, don't feed, find a better spot
    UNKNOWN = "unknown"  # no enemy army info -- scout before committing


@dataclass
class EngagementAdvice:
    verdict: Engagement
    effective_ratio: float  # our effective strength / enemy effective strength
    reasons: List[str] = field(default_factory=list)

    @property
    def should_engage(self) -> bool:
        return self.verdict == Engagement.ENGAGE


def _upgrade_multiplier(state: GameState) -> float:
    """Structural efficiency bought in advance: an upgrade edge raises trade value.

    ~4% per net upgrade, clamped to [0.7, 1.4] so it modulates without dominating.
    """
    if state.enemy_upgrades is None:
        return 1.0
    diff = state.upgrades_done - state.enemy_upgrades
    return max(0.7, min(1.4, 1.0 + 0.04 * diff))


def assess_engagement(state: GameState) -> EngagementAdvice:
    """Decide whether the current fight is favorable.

    Effective strength = army supply x upgrade edge x situational multipliers.
    A ratio comfortably above 1 means engage; well below means avoid (or hold, if
    defender's advantage at home covers the gap). Trading down vetoes engaging.
    """
    if state.enemy_army_supply is None:
        return EngagementAdvice(
            Engagement.UNKNOWN, 1.0,
            ["no scouted enemy army -- scout before committing to a fight"],
        )

    reasons: List[str] = []
    our = max(0.1, state.army_supply)
    their = max(0.1, state.enemy_army_supply)

    upg = _upgrade_multiplier(state)
    if upg > 1.0:
        reasons.append(f"upgrade edge x{upg:.2f} (efficiency bought in advance)")
    elif upg < 1.0:
        reasons.append(f"upgrade deficit x{upg:.2f}")

    mult = 1.0
    if state.composition_favorable is True:
        mult *= 1.2
        reasons.append("composition counters theirs (+)")
    elif state.composition_favorable is False:
        mult *= 0.8
        reasons.append("composition is countered (-)")
    if state.have_terrain_advantage:
        mult *= 1.15
        reasons.append("terrain/surround advantage (+)")
    if state.positional_disadvantage:
        mult *= 0.8
        reasons.append("bad position -- up a ramp / open / surrounded (-)")
    if state.fighting_at_home:
        mult *= 1.15
        reasons.append("defender's advantage at home (+)")
    if state.reinforcements_close:
        mult *= 1.1
        reasons.append("reinforcements close (+)")
    if (state.enemy_has_cloak or state.enemy_has_air) and not state.have_detection:
        mult *= 0.8
        reasons.append("enemy cloak/air without our detection (-)")

    ratio = (our * upg * mult) / their

    trading_down = assess_efficiency(state).verdict == TradeVerdict.TRADING_DOWN

    if ratio >= 1.1 and not trading_down:
        verdict = Engagement.ENGAGE
        reasons.append(f"effective ratio {ratio:.2f}: favorable -- take the fight")
    elif ratio <= 0.9:
        if state.fighting_at_home and ratio >= 0.7:
            verdict = Engagement.DEFEND
            reasons.append(f"effective ratio {ratio:.2f}: behind, but hold at home")
        else:
            verdict = Engagement.AVOID
            reasons.append(f"effective ratio {ratio:.2f}: unfavorable -- disengage")
    else:  # roughly even
        if trading_down:
            verdict = Engagement.AVOID
            reasons.append("even fight but trading down -- find a better engagement")
        elif state.fighting_at_home:
            verdict = Engagement.DEFEND
            reasons.append(f"even ratio {ratio:.2f}: hold at home rather than coinflip away")
        else:
            verdict = Engagement.AVOID
            reasons.append(f"even ratio {ratio:.2f}: don't take a coinflip in the open")

    return EngagementAdvice(verdict, round(ratio, 2), reasons)
