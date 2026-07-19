"""strategy_engine: the SC2 strategic model as bot behavior.

This package turns the strategy docs at the repo root into runnable behavior,
one module per layer of the docs:

- ``state``       -- ``GameState``, a framework-agnostic snapshot of the game
                     (plus a best-effort adapter from a python-sc2 ``BotAI``).
- ``principles``  -- the economy / army / tech investment tension and timing
                     (mirrors ``PRINCIPLES.md``).
- ``strategy``    -- opponent classification and counter stances
                     (mirrors ``STRATEGY.md``).
- ``rules``       -- concrete, checkable rules as predicate functions
                     (mirrors ``RULES.md``).
- ``harassment``  -- harass and anti-harass decisions
                     (mirrors the harassment sections of the docs).
- ``advisor``     -- ties the modules together into a single recommendation a
                     bot can query each step.

Nothing here imports ``sc2`` at module load, so the package can be imported and
unit-tested without StarCraft II or python-sc2 installed. The optional
``GameState.from_bot`` adapter imports ``sc2`` lazily only when called.
"""

from .state import GameState
from .principles import (
    Investment,
    InvestmentAdvice,
    PowerTiming,
    TradeVerdict,
    Efficiency,
    recommend_investment,
    power_timing,
    assess_efficiency,
)
from .strategy import Archetype, Classification, classify_opponent, counter_stance
from .rules import Rule, RuleHit, evaluate_rules
from .harassment import HarassAdvice, harass_advice
from .combat import Engagement, EngagementAdvice, assess_engagement
from .defense import DefensePlan, assess_defense
from .information import EnemyEstimate, estimate_enemy, project_enemy
from .openings import (
    Placement,
    BuildStep,
    Opening,
    OpeningExecutor,
    Deviation,
    OPENINGS,
    classify_opening,
    openings_for_race,
    get_opening,
    best_opening,
    verify_opening,
)
from .build_guides import (
    ScriptedBuild,
    BuildAction,
    BuildExecutor,
    BUILD_GUIDES,
    guides_for,
    get_build,
)
from .advisor import StrategicAdvisor, Advice
from .macro import MacroPlan, recommend_macro
from .tactics import Tactics, recommend_tactics
from .composition import CompositionAdvice, recommend_composition
from .spending import Want, plan_spend

__all__ = [
    "GameState",
    "Investment",
    "InvestmentAdvice",
    "PowerTiming",
    "TradeVerdict",
    "Efficiency",
    "recommend_investment",
    "power_timing",
    "assess_efficiency",
    "Archetype",
    "Classification",
    "classify_opponent",
    "counter_stance",
    "Rule",
    "RuleHit",
    "evaluate_rules",
    "HarassAdvice",
    "harass_advice",
    "Engagement",
    "EngagementAdvice",
    "assess_engagement",
    "DefensePlan",
    "assess_defense",
    "EnemyEstimate",
    "estimate_enemy",
    "project_enemy",
    "Placement",
    "BuildStep",
    "Opening",
    "OpeningExecutor",
    "Deviation",
    "OPENINGS",
    "classify_opening",
    "openings_for_race",
    "get_opening",
    "best_opening",
    "verify_opening",
    "ScriptedBuild",
    "BuildAction",
    "BuildExecutor",
    "BUILD_GUIDES",
    "guides_for",
    "get_build",
    "StrategicAdvisor",
    "Advice",
    "MacroPlan",
    "recommend_macro",
    "Tactics",
    "recommend_tactics",
    "CompositionAdvice",
    "recommend_composition",
    "Want",
    "plan_spend",
]
