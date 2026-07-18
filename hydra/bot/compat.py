"""Compatibility patches for the 4.10 headless Linux client.

python-sc2's ``already_pending()`` (which the executors call constantly) reads
each in-production unit's *creation ability* from the game data. Some unit-type
ids in the 4.10 client's game data have a ``None`` creation ability -- "rich"
resource buildings on gold bases, and various modern-client dummy ids that the
old data doesn't fully describe. The lookup then does ``None.exact_id`` and
crashes the whole bot mid-game with ``AttributeError`` (observed at ~15:00 in a
game HydraBot was winning).

python-sc2 keeps a ``CREATION_ABILITY_FIX`` override table and phoenix patches
one such id statically. This does it robustly instead: at game start it scans the
*loaded* game data and registers a harmless creation ability for **every** id
whose creation ability is missing, so the crash can't happen on any map. Call
``patch_creation_abilities(bot)`` from ``on_start`` (the game data is available
by then).
"""

from __future__ import annotations

from loguru import logger
from sc2.constants import CREATION_ABILITY_FIX
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

# A harmless placeholder ability: the value is only used as a Counter key for
# already_pending bookkeeping on these dummy/rich ids, which the bot never
# queries, so any valid AbilityId is safe.
_PLACEHOLDER = getattr(AbilityId, "NULL_NULL", None) or next(iter(AbilityId))


def patch_creation_abilities(bot) -> int:
    """Register a placeholder creation ability for every unit-type id whose
    game-data creation ability is missing. Returns how many were patched."""
    fixed = 0
    units = getattr(getattr(bot, "game_data", None), "units", {}) or {}
    for uid, data in units.items():
        try:
            type_id = UnitTypeId(uid)
        except ValueError:
            continue
        if type_id in CREATION_ABILITY_FIX:
            continue
        try:
            missing = data.creation_ability is None
        except Exception:  # noqa: BLE001 - be defensive against odd data entries
            missing = True
        if missing:
            CREATION_ABILITY_FIX[type_id] = _PLACEHOLDER
            fixed += 1
    if fixed:
        logger.info(f"compat: patched {fixed} unit ids with no creation ability")
    return fixed
