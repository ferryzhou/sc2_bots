"""composition: what army to build -- and when to transition tech.

Mirrors the army-composition lessons in ``STRATEGY.md`` / ``COMBAT.md``. The
engagement/tactics modules decide *whether* and *how* to fight; this module
decides *what to build* so the fight is winnable in the first place.

The failure it targets (analysis of Aiur vs VeryHard Zerg): a bot with a solved
economy maxes on a single gateway unit (mass Stalker), banks the gas it can't
spend, and feeds that narrow army into the enemy's teched-up army (BroodLord +
Infestor + mass ground) at 0.1 trades. A mono-unit army has no answer to a
diversified one. Past the opening you must **transition tech** -- add splash for
the ground flood, anti-air for their air, and stop pumping more of the same unit.

Framework-agnostic and race-neutral: it names *abstract* needs (splash, anti-air,
escalate, diversify), and the bot translates them into its race's units
(Protoss: Colossus/Storm for splash, Void Ray/Tempest for air, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .state import GameState


@dataclass
class CompositionAdvice:
    """What the army needs -- abstract, for the bot to translate into units."""

    need_splash: bool = False      # enemy massing light/clustered ground -> want AoE
    need_anti_air: bool = False    # enemy fields air -> want anti-air
    escalate_tech: bool = False    # past the opening + floating/stalemate -> add tech tiers
    max_unit_share: float = 1.0    # cap any single unit type at this fraction of the army
    reasons: List[str] = field(default_factory=list)


def recommend_composition(state: GameState) -> CompositionAdvice:
    """Recommend an army composition / tech-transition posture.

    Splash answers a light or clustered ground army; anti-air answers their air.
    Escalation fires once we're past the opening and either banking gas (a narrow
    army can't spend it -- the tell of a stalled composition) or our composition
    is not countering theirs. When escalating we cap any single unit's share so
    the bot is forced to diversify into the tech it just unlocked.
    """
    minutes = state.game_minutes
    reasons: List[str] = []

    need_splash = bool(state.enemy_massing_light)
    if need_splash:
        reasons.append("enemy massing light: build splash (AoE)")
    elif state.enemy_race == "Zerg" and minutes >= 9:
        # Zerg's late game floods ground (ling/hydra/baneling); want AoE by default
        need_splash = True
        reasons.append("late vs Zerg: build splash for the ground flood")

    need_anti_air = bool(state.enemy_has_air)
    if need_anti_air:
        reasons.append("enemy fields air: add anti-air")

    # Escalate: past the opening, and either floating gas (a narrow army can't
    # spend it) or our comp isn't favorable / they have air we can't answer.
    floating_gas = state.vespene >= 400
    stalemate = state.composition_favorable is False
    escalate_tech = minutes >= 8 and (floating_gas or stalemate or need_anti_air)
    if escalate_tech:
        why = ("floating gas behind a narrow army" if floating_gas
               else "composition unfavorable" if stalemate
               else "enemy teching up")
        reasons.append(f"escalate tech + diversify: {why}")

    # Force diversification while escalating: no single unit past ~55% of the army.
    max_unit_share = 0.55 if escalate_tech else 1.0

    return CompositionAdvice(
        need_splash=need_splash,
        need_anti_air=need_anti_air,
        escalate_tech=escalate_tech,
        max_unit_share=max_unit_share,
        reasons=reasons,
    )
