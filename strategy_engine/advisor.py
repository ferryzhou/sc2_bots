"""advisor: tie the modules into one recommendation a bot queries each step.

A bot builds a ``GameState`` (directly or via ``GameState.from_bot``), calls
``StrategicAdvisor.advise(state)``, and reads a single ``Advice`` object covering
investment priority, opponent classification and counter, power timing, harass
advice, and the concrete rules that fired.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .state import GameState
from .principles import (
    InvestmentAdvice,
    PowerTiming,
    Efficiency,
    recommend_investment,
    power_timing,
    assess_efficiency,
)
from .strategy import (
    Classification,
    CounterStance,
    classify_opponent,
    counter_stance,
)
from .rules import RuleHit, evaluate_rules
from .harassment import HarassAdvice, harass_advice
from .combat import EngagementAdvice, assess_engagement
from .information import EnemyEstimate, project_enemy


@dataclass
class Advice:
    efficiency: Efficiency
    engagement: EngagementAdvice
    investment: InvestmentAdvice
    timing: PowerTiming
    classification: Classification
    counter: CounterStance
    harass: HarassAdvice
    enemy_estimate: EnemyEstimate
    rule_hits: List[RuleHit]

    def summary(self) -> str:
        """A compact human-readable digest, handy for logging from a bot."""
        # Efficiency leads: replay analysis makes it the strongest single signal.
        eff = self.efficiency
        lines = [
            f"efficiency: {eff.verdict.value} (trade {eff.trade_ratio:.2f})"
            + ("  [idle resources!]" if eff.idle_waste else ""),
            f"engagement: {self.engagement.verdict.value} (ratio {self.engagement.effective_ratio:.2f})",
            f"posture:    {self.investment.posture}",
            f"invest:     {' > '.join(i.value for i in self.investment.priority)}",
            f"timing:     {self.timing.value}",
            f"opponent:   {self.classification.archetype.value} "
            f"({self.classification.confidence:.0%})",
            f"counter:    {self.counter.posture}",
        ]
        est = self.enemy_estimate
        if est.has_data and not est.is_fresh:
            lines.append(f"enemy read:  projected (dead-reckoned, conf {est.confidence:.0%})")
        if self.harass.should_harass:
            lines.append("harass:     yes -- " + "; ".join(self.harass.harass_reasons))
        if self.harass.should_defend:
            lines.append("anti-harass: " + "; ".join(self.harass.defend_reasons))
        if self.rule_hits:
            lines.append("rules:      " + ", ".join(h.action for h in self.rule_hits))
        return "\n".join(lines)


class StrategicAdvisor:
    """Stateless facade over the strategy modules.

    Stateless by design: pass a fresh ``GameState`` each call. Any memory (e.g.
    accumulated scouting) lives on the bot and is folded into the state.
    """

    def advise(self, state: GameState) -> Advice:
        # Enemy-facing reads run on a dead-reckoned projection when scouting is
        # stale, so they degrade gracefully instead of going UNKNOWN. Own-side
        # rules (including "keep scouting") run on the real state.
        enemy_view, estimate = project_enemy(state)
        classification = classify_opponent(enemy_view)
        return Advice(
            efficiency=assess_efficiency(state),
            engagement=assess_engagement(enemy_view),
            investment=recommend_investment(state),
            timing=power_timing(enemy_view),
            classification=classification,
            counter=counter_stance(classification),
            harass=harass_advice(enemy_view),
            enemy_estimate=estimate,
            rule_hits=evaluate_rules(state),
        )

    def advise_bot(self, bot, enemy_memory: dict | None = None) -> Advice:
        """Convenience: snapshot a python-sc2 bot, then advise."""
        return self.advise(GameState.from_bot(bot, enemy_memory))
