"""information: dead-reckoning the enemy from a stale sighting.

Mirrors ``INFORMATION.md``. Scouting decays -- the moment you look away your
picture ages. Rather than snap straight to ``UNKNOWN`` when the last scout is
stale, project the enemy forward from the last sighting plus the elapsed time and
their known production capacity, as a *floor* estimate with decaying confidence.

The advisor uses ``project_enemy`` to run classification / timing / engagement on
this estimate when scouting is stale, so recommendations degrade gracefully
instead of going blind. Own-side rules (including "keep scouting") still run on
the real state, so a projection never masks the need to re-scout.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional, Tuple

from .state import GameState

# Conservative "could-have" growth rates for dead-reckoning (tunable).
_ARMY_SUPPLY_PER_PROD_PER_MIN = 4.0  # supply each production building could add / min
_WORKERS_PER_MIN = 10               # workers they could add / min
_CONFIDENCE_DECAY_SECONDS = 180.0   # confidence -> low over ~3 minutes


@dataclass
class EnemyEstimate:
    army_supply: Optional[float]
    worker_count: Optional[int]
    base_count: Optional[int]
    production_structures: Optional[int]
    confidence: float          # 0..1, decays with staleness
    is_fresh: bool             # True if from current scouting, False if projected
    notes: List[str] = field(default_factory=list)

    @property
    def has_data(self) -> bool:
        return self.army_supply is not None or self.base_count is not None


def estimate_enemy(state: GameState) -> EnemyEstimate:
    """Best current guess of enemy strength: fresh scouting, or a projection.

    Returns an empty estimate (no data, zero confidence) if the enemy has never
    been seen. If the last sighting is fresh, returns it as-is. Otherwise
    dead-reckons the last sighting forward as a floor.
    """
    never_seen = state.enemy_base_count is None and state.last_scouted_time is None
    if never_seen:
        return EnemyEstimate(None, None, None, None, 0.0, False, ["enemy never scouted"])

    last_t = state.last_scouted_time if state.last_scouted_time is not None else state.game_time
    elapsed = max(0.0, state.game_time - last_t)
    confidence = max(0.1, 1.0 - elapsed / _CONFIDENCE_DECAY_SECONDS)

    if elapsed <= 45.0:
        return EnemyEstimate(
            state.enemy_army_supply, state.enemy_worker_count, state.enemy_base_count,
            state.enemy_production_structures, confidence, True, ["fresh scouting"],
        )

    minutes = elapsed / 60.0
    prod = state.enemy_production_structures or 1
    army = state.enemy_army_supply
    if army is not None:
        army = round(army + prod * _ARMY_SUPPLY_PER_PROD_PER_MIN * minutes, 1)
    workers = state.enemy_worker_count
    if workers is not None:
        cap = 22 * (state.enemy_base_count or 2)
        workers = min(cap, workers + int(_WORKERS_PER_MIN * minutes))
    return EnemyEstimate(
        army, workers, state.enemy_base_count, prod, confidence, False,
        [f"dead-reckoned {minutes:.1f}min forward from last sighting (floor estimate, "
         f"confidence {confidence:.0%})"],
    )


def project_enemy(state: GameState) -> Tuple[GameState, EnemyEstimate]:
    """Return (state_for_enemy_reads, estimate).

    When scouting is fresh or the enemy was never seen, returns the original state
    unchanged. When it is stale but we have a prior sighting, returns a copy with
    the enemy fields replaced by the projection (and ``last_scouted_time`` bumped
    so downstream reads treat the estimate as usable) -- this is what lets
    classification / timing / engagement degrade gracefully instead of going to
    ``UNKNOWN``. The original state should still drive own-side rules.
    """
    est = estimate_enemy(state)
    if est.is_fresh or not est.has_data:
        return state, est
    projected = replace(
        state,
        enemy_army_supply=est.army_supply if est.army_supply is not None else state.enemy_army_supply,
        enemy_worker_count=est.worker_count,
        enemy_base_count=est.base_count,
        enemy_production_structures=est.production_structures,
        last_scouted_time=state.game_time,
    )
    return projected, est
