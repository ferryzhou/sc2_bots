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
from .defense import DefensePlan, assess_defense
from .information import EnemyEstimate, project_enemy
from .macro import MacroPlan, recommend_macro
from .tactics import Tactics, recommend_tactics
from .composition import CompositionAdvice, recommend_composition


@dataclass
class Advice:
    efficiency: Efficiency
    engagement: EngagementAdvice
    investment: InvestmentAdvice
    timing: PowerTiming
    classification: Classification
    counter: CounterStance
    defense: DefensePlan
    harass: HarassAdvice
    enemy_estimate: EnemyEstimate
    rule_hits: List[RuleHit]
    macro: MacroPlan
    tactics: Tactics
    composition: CompositionAdvice

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
            f"macro:      target_prod={self.macro.target_production} "
            f"urgency={self.macro.spend_urgency:.2f}"
            f"{' FORCE' if self.macro.force_train else ''}",
            f"tactics:    focus_fire={self.tactics.focus_fire} "
            f"retreat<{self.tactics.retreat_threshold:.0%} "
            f"priority={self.tactics.target_priority}"
            f"{' PRESERVE' if self.tactics.preserve_units else ''}",
        ]
        comp = self.composition
        if comp.need_splash or comp.need_anti_air or comp.escalate_tech:
            needs = [n for n, on in (("splash", comp.need_splash),
                                     ("anti-air", comp.need_anti_air),
                                     ("escalate", comp.escalate_tech)) if on]
            lines.append(f"composition: {', '.join(needs)} "
                         f"(cap unit share {comp.max_unit_share:.0%})")
        if self.defense.emergency:
            d = self.defense
            lines.append(
                f"DEFENSE:    emergency -- static x{d.static_defense}, "
                f"army-first{', PULL WORKERS' if d.pull_workers else ''}"
                f"{', get detection' if d.need_detection else ''}")
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
        investment = recommend_investment(state)
        engagement = assess_engagement(enemy_view)
        timing = power_timing(enemy_view)
        return Advice(
            efficiency=assess_efficiency(state),
            engagement=engagement,
            investment=investment,
            timing=timing,
            classification=classification,
            counter=counter_stance(classification),
            defense=assess_defense(enemy_view),
            harass=harass_advice(enemy_view),
            enemy_estimate=estimate,
            rule_hits=evaluate_rules(state),
            macro=recommend_macro(state, investment),
            tactics=recommend_tactics(state, engagement, timing),
            composition=recommend_composition(enemy_view),
        )

    def advise_bot(self, bot, enemy_memory: dict | None = None) -> Advice:
        """Convenience: snapshot a python-sc2 bot, then advise."""
        return self.advise(GameState.from_bot(bot, enemy_memory))
