"""Compatibility patches for running under the 4.10 headless Linux client.

Import for side effects before creating the bot.
"""

from sc2.constants import CREATION_ABILITY_FIX
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

# On community-patched ladder maps played under the 4.10 linux client, a rich
# assimilator under construction reports the modern client's unit type id,
# which python-sc2's enum resolves to TROOPERMENGSKACGLUESCREENDUMMY (the
# proto name is still 'AssimilatorRich'). 4.10 game data has no creation
# ability for that id, so burnysc2's _abilities_count_and_build_progress
# raises AttributeError and the bot instantly loses. Register the same fix
# that ASSIMILATORRICH already has. (REFINERYRICH resolves correctly and has
# an upstream fix, so the Terran rich-gas path is already covered; this patch
# is kept in case an id-shifted variant shows up on other patched maps.)
CREATION_ABILITY_FIX.setdefault(
    UnitTypeId.TROOPERMENGSKACGLUESCREENDUMMY, AbilityId.PROTOSSBUILD_ASSIMILATOR
)
