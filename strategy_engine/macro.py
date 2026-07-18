"""macro: production pressure and spending urgency.

Mirrors the macro-execution lessons in ``PRINCIPLES.md`` / ``RULES.md``. The rules
module fires *signals* ("you're floating minerals"); this module turns them into
*quantitative targets* a bot can act on directly: how many production buildings to
aim for, how hard to push spending, and whether to cut probes to force units out.

The core lesson from replay analysis (analysis/REPLAY_FINDINGS.md): bigger
economies that *float* lose to smaller economies that *spend*. So this module
escalates production targets and spend urgency as resources bank up -- a saturated
economy with 500 banked minerals should have more production than the same economy
at 100 minerals, because the unspent money is wasted otherwise.

Framework-agnostic: takes a ``GameState`` (plus the ``InvestmentAdvice`` for posture
context) and returns a ``MacroPlan``. Any bot -- python-sc2, ares-sc2, or a test
harness -- can consume it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .state import GameState
from .principles import InvestmentAdvice


@dataclass
class MacroPlan:
    """How much production to build and how hard to push spending."""

    target_production: int            # desired production building count
    spend_urgency: float              # 0..1 -- how hard to push spending
    force_train: bool                 # train from every idle producer now (cut probes)
    worker_cap: int                   # hard worker stop
    allow_parallel_build: int         # max production structures in flight at once
    base_target: int = 1              # how many bases we should be working toward now
    reasons: List[str] = field(default_factory=list)

    @property
    def floating(self) -> bool:
        """True when resources are banked hard enough to demand aggressive spending."""
        return self.spend_urgency >= 0.6


def recommend_macro(state: GameState, investment: InvestmentAdvice) -> MacroPlan:
    """How many production buildings, and how hard to spend.

    The base scaling (2 per base + 1) is what a saturated economy can sustain; a
    saturated economy gets more (convert the economy into army), and floating money
    raises the target further because unspent economy is wasted. Under threat we
    add more so army comes faster.
    """
    reasons: List[str] = []
    bases = max(1, state.base_count)
    workers = state.worker_count
    saturation = workers / max(1, 22 * bases)
    minutes = state.game_minutes

    # Expansion target (Principle 4): keep taking bases through the mid-late game
    # so a 2-base economy never has to fight a 4-base one. Time drives a steady
    # cadence (+1 base every ~4 min from 4:00); saturation pulls the next base
    # forward; being under threat holds us to at most one more than we have now.
    phase_target = 2 + max(0, int((minutes - 4) // 4))
    if saturation >= 0.85:
        phase_target = max(phase_target, bases + 1)
    if minutes < 2.0:
        phase_target = 1
    base_target = min(6, max(bases, phase_target))
    # Safety: don't out-expand the army. Reaching past the natural (3rd base on)
    # is only safe with an army to cover it -- expanding behind nothing walks the
    # Nexus into the next timing attack. Hold at the current count until the army
    # is there. The natural (2nd) is exempt; its defender's advantage covers it.
    if base_target > bases and bases >= 2 and state.army_supply < 4 * bases + 6:
        base_target = bases
        reasons.append(f"army {state.army_supply} too thin to expand safely: hold {bases}")

    # Base target: 2 per base + 1, the standard a saturated economy sustains.
    target = 2 * bases + 1

    # Saturated economy can support more -- convert the economy into army.
    if saturation >= 0.85:
        target += bases
        reasons.append(f"saturated ({saturation:.0%}): add production to convert economy")

    # Floating money raises the target -- unspent minerals are wasted.
    if state.minerals > 400:
        target += 1
        reasons.append(f"floating {state.minerals} minerals: add a production building")
    if state.minerals > 700:
        target += 2
        reasons.append("floating hard: add more production to stop the bleed")

    # Under threat: army production takes priority.
    if investment.posture == "safe":
        target += 2
        reasons.append("under threat: add army production")
    elif investment.posture == "aggressive":
        target += 1
        reasons.append("aggressive posture: add production to press")

    # Behind on the base target: leave minerals for the expansion instead of
    # sinking everything into army production (that is what keeps a bot on 2 bases
    # -- army spending drains the money the next base needs). Cap production so the
    # economy can afford to grow.
    if bases < base_target:
        target = min(target, 2 * bases + 2)
        reasons.append(f"on {bases} bases, target {base_target}: cap production, save to expand")

    target = max(2, min(target, 16))  # sane floor/ceiling

    # Spend urgency: escalates with banked resources.
    urgency = 0.0
    if state.minerals > 250:
        urgency = 0.3
    if state.minerals > 450:
        urgency = 0.55
    if state.minerals > 700:
        urgency = 0.85
    if state.vespene > 250:
        urgency = max(urgency, 0.4)
    if state.vespene > 400:
        urgency = max(urgency, 0.7)

    # Force-train when urgency is high and production sits idle -- cut probes for
    # a tick to get units out. The 'never stop probes' rule yields when floating.
    force_train = urgency >= 0.55 and state.idle_production > 0
    if force_train:
        reasons.append("high spend urgency + idle production: force units now")

    # Worker cap: ~22/bases + small surplus for transfers; hard-cap 80.
    worker_cap = min(80, 22 * bases + 4)

    # Allow parallel production construction when floating (so we don't serialize
    # our way out of a float one building at a time).
    allow_parallel = 1
    if state.minerals > 350:
        allow_parallel = 2
    if state.minerals > 700:
        allow_parallel = 3

    return MacroPlan(
        target_production=target,
        spend_urgency=round(urgency, 2),
        force_train=force_train,
        worker_cap=worker_cap,
        allow_parallel_build=allow_parallel,
        base_target=base_target,
        reasons=reasons,
    )
