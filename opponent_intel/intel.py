"""In-game opponent intel: resolve the ladder's --OpponentId to a known profile
and recommend a strategy.

Usage inside a bot (e.g. in on_start, after the ladder sets self.opponent_id):

    from opponent_intel import recommend_for
    rec = recommend_for(self.opponent_id)          # opponent_id may be a UUID or a name
    logger.info(rec.summary())
    initial_strategy = rec.hydra_strategy          # for HydraBot
    stance = rec.stance                            # race-agnostic, for any bot

`recommend_for` never raises and never needs the network: it loads the static
opponent_map.json shipped alongside this module. An unknown/None opponent id
yields a safe default recommendation (opp_style="unknown").
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

from opponent_intel import classify

_HERE = os.path.dirname(os.path.abspath(__file__))
_MAP_PATH = os.path.join(_HERE, "opponent_map.json")

try:
    with open(_MAP_PATH) as _f:
        _MAP = json.load(_f)
except Exception:  # missing/corrupt map -> resolver still works, just no hits
    _MAP = {"bots": {}, "names": {}}

_BOTS = _MAP.get("bots", {})
_NAMES = _MAP.get("names", {})


@dataclass(frozen=True)
class Recommendation:
    opponent_id: str | None      # the raw id we were given (UUID or name)
    known: bool                  # did we resolve it to a profiled bot?
    name: str                    # opponent name if known, else "<unknown>"
    race: str                    # opponent race if known, else "?"
    opp_style: str               # one of classify.OPP_STYLES
    style: str                   # the human-readable profile style string
    hydra_strategy: str          # HydraBot's counter (one of its 5 strategies)
    stance: str                  # race-agnostic stance (see classify.STANCE)
    reason: str                  # why this counter

    def summary(self) -> str:
        who = f"{self.name} [{self.race}]" if self.known else f"unknown ({self.opponent_id})"
        return (f"opponent={who} style={self.opp_style} -> "
                f"hydra={self.hydra_strategy} stance={self.stance} ({self.reason})")


def resolve(opponent_id: str | None) -> dict | None:
    """Return the profile entry for a ladder OpponentId (UUID) or a bot name,
    or None if we have no prior on it. Case-insensitive for names."""
    if not opponent_id:
        return None
    key = opponent_id.strip()
    if key in _BOTS:                       # exact UUID (ladder)
        return _BOTS[key]
    uuid = _NAMES.get(key.lower())         # name (local harness / manual)
    if uuid:
        return _BOTS.get(uuid)
    return None


def recommend_for(opponent_id: str | None) -> Recommendation:
    """Resolve an OpponentId and recommend a counter-strategy. Never raises."""
    entry = resolve(opponent_id)
    if entry is None:
        opp_style = "unknown"
        return Recommendation(
            opponent_id=opponent_id, known=False, name="<unknown>", race="?",
            opp_style=opp_style, style="",
            hydra_strategy=classify.hydra_strategy(opp_style),
            stance=classify.stance(opp_style),
            reason=classify.explain(opp_style),
        )
    opp_style = entry.get("opp_style", "unknown")
    return Recommendation(
        opponent_id=opponent_id, known=True,
        name=entry.get("name", "?"), race=entry.get("race", "?"),
        opp_style=opp_style, style=entry.get("style", ""),
        hydra_strategy=classify.hydra_strategy(opp_style),
        stance=classify.stance(opp_style),
        reason=classify.explain(opp_style),
    )


def known_count() -> int:
    return len(_BOTS)
