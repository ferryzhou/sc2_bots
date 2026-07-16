"""Opponent intel: resolve the ladder's --OpponentId (a stable game_display_id
UUID, or a bot name locally) to a known profile and recommend a counter-strategy.

    from opponent_intel import recommend_for
    rec = recommend_for(self.opponent_id)
    initial = rec.hydra_strategy   # HydraBot's counter strategy
    stance  = rec.stance           # race-agnostic stance for any bot
"""
from opponent_intel.intel import (
    Recommendation,
    recommend_for,
    resolve,
    known_count,
)
from opponent_intel import classify

__all__ = [
    "Recommendation",
    "recommend_for",
    "resolve",
    "known_count",
    "classify",
]
