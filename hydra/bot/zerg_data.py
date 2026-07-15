"""zerg_data: a declarative model of the Zerg tech tree and unit roster.

This is the single source of Zerg-specific knowledge in the bot. Everything the
executors do -- what to morph a unit from, which structures a unit needs, which
tech tier (Lair/Hive) is required, how to build the prerequisites -- is read from
these tables rather than hard-coded as if/else chains. To teach the bot a new
unit you add a row here; no executor changes.

The point (per the project's "avoid hard-coded low-level and ad-hoc rules" goal)
is that strategy is expressed as *what to build* (composition, tech targets) and
this table mechanically resolves *how* to build it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U


class Tier(Enum):
    """Tech tier a base must reach. Ordered so comparisons work."""

    HATCHERY = 0
    LAIR = 1
    HIVE = 2


# --------------------------------------------------------------------------- #
# Structures: what each tech/production building itself requires, and how it is
# produced (a drone build vs. a morph from an existing structure).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class StructureSpec:
    needs: List[U] = field(default_factory=list)   # prerequisite structures
    tier: Tier = Tier.HATCHERY                      # base tier required
    morph_from: Optional[U] = None                  # if set, morphed not built
    morph_ability: Optional[AbilityId] = None


STRUCTURES: Dict[U, StructureSpec] = {
    U.SPAWNINGPOOL: StructureSpec(needs=[U.HATCHERY]),
    U.EVOLUTIONCHAMBER: StructureSpec(needs=[U.HATCHERY]),
    U.ROACHWARREN: StructureSpec(needs=[U.SPAWNINGPOOL]),
    U.BANELINGNEST: StructureSpec(needs=[U.SPAWNINGPOOL]),
    U.LAIR: StructureSpec(
        needs=[U.SPAWNINGPOOL], morph_from=U.HATCHERY,
        morph_ability=AbilityId.UPGRADETOLAIR_LAIR,
    ),
    U.HYDRALISKDEN: StructureSpec(needs=[U.LAIR], tier=Tier.LAIR),
    U.LURKERDENMP: StructureSpec(needs=[U.HYDRALISKDEN], tier=Tier.LAIR),
    U.SPIRE: StructureSpec(needs=[U.LAIR], tier=Tier.LAIR),
    U.INFESTATIONPIT: StructureSpec(needs=[U.LAIR], tier=Tier.LAIR),
    U.HIVE: StructureSpec(
        needs=[U.INFESTATIONPIT], tier=Tier.LAIR, morph_from=U.LAIR,
        morph_ability=AbilityId.UPGRADETOHIVE_HIVE,
    ),
    U.GREATERSPIRE: StructureSpec(
        needs=[U.SPIRE], tier=Tier.HIVE, morph_from=U.SPIRE,
        morph_ability=AbilityId.UPGRADETOGREATERSPIRE_GREATERSPIRE,
    ),
    U.ULTRALISKCAVERN: StructureSpec(needs=[U.HIVE], tier=Tier.HIVE),
    U.SPINECRAWLER: StructureSpec(needs=[U.SPAWNINGPOOL]),
    U.SPORECRAWLER: StructureSpec(needs=[U.SPAWNINGPOOL]),
}


# --------------------------------------------------------------------------- #
# Units: supply, and how each is produced. "larva" units are trained from a
# larva; "morph" units are morphed from a base unit (which is itself a larva
# unit). Each carries the structure that unlocks it and the tier it needs.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class UnitSpec:
    supply: float
    needs: List[U] = field(default_factory=list)    # unlocking structures
    tier: Tier = Tier.HATCHERY
    morph_from: Optional[U] = None                  # None -> trained from larva
    morph_ability: Optional[AbilityId] = None
    is_detector: bool = False
    is_air: bool = False


UNITS: Dict[U, UnitSpec] = {
    # larva line
    U.DRONE: UnitSpec(1, needs=[U.HATCHERY]),
    U.OVERLORD: UnitSpec(0, needs=[U.HATCHERY]),
    U.ZERGLING: UnitSpec(0.5, needs=[U.SPAWNINGPOOL]),
    U.ROACH: UnitSpec(2, needs=[U.ROACHWARREN]),
    U.HYDRALISK: UnitSpec(2, needs=[U.HYDRALISKDEN], tier=Tier.LAIR),
    U.MUTALISK: UnitSpec(2, needs=[U.SPIRE], tier=Tier.LAIR, is_air=True),
    U.CORRUPTOR: UnitSpec(2, needs=[U.SPIRE], tier=Tier.LAIR, is_air=True),
    U.INFESTOR: UnitSpec(2, needs=[U.INFESTATIONPIT], tier=Tier.LAIR),
    U.ULTRALISK: UnitSpec(6, needs=[U.ULTRALISKCAVERN], tier=Tier.HIVE),
    # queen is trained from a hatchery (not larva); handled specially
    U.QUEEN: UnitSpec(2, needs=[U.SPAWNINGPOOL]),
    # morph line
    U.BANELING: UnitSpec(
        0.5, needs=[U.BANELINGNEST], morph_from=U.ZERGLING,
        morph_ability=AbilityId.MORPHZERGLINGTOBANELING_BANELING,
    ),
    U.RAVAGER: UnitSpec(
        3, needs=[U.ROACHWARREN], morph_from=U.ROACH,
        morph_ability=AbilityId.MORPHTORAVAGER_RAVAGER,
    ),
    U.LURKERMP: UnitSpec(
        3, needs=[U.LURKERDENMP], tier=Tier.LAIR, morph_from=U.HYDRALISK,
        morph_ability=AbilityId.MORPH_LURKER,
    ),
    U.BROODLORD: UnitSpec(
        4, needs=[U.GREATERSPIRE], tier=Tier.HIVE, morph_from=U.CORRUPTOR,
        morph_ability=AbilityId.MORPHTOBROODLORD_BROODLORD, is_air=True,
    ),
    U.OVERSEER: UnitSpec(
        0, needs=[U.LAIR], tier=Tier.LAIR, morph_from=U.OVERLORD,
        morph_ability=AbilityId.MORPH_OVERSEER, is_detector=True, is_air=True,
    ),
}

# Structures that provide detection (in addition to the Overseer unit).
DETECTOR_STRUCTURES = {U.SPORECRAWLER}

# Anti-air static defense / anti-air capable units, for the react-to-air rule.
ANTIAIR_UNITS = {U.HYDRALISK, U.MUTALISK, U.CORRUPTOR, U.QUEEN}


def all_prerequisite_structures(units: List[U]) -> List[U]:
    """Ordered, de-duplicated list of every structure needed to build ``units``.

    Walks each unit's unlocking structures and their transitive structure
    prerequisites. The result is ordered so that a structure never appears
    before something it depends on -- the executor can build straight down the
    list. Lair/Hive tier morphs are represented as structures here too, so
    "needs Lair" naturally shows up as an item to satisfy.
    """
    ordered: List[U] = []
    seen: set = set()

    def visit(struct: U) -> None:
        if struct in seen or struct == U.HATCHERY:
            return
        seen.add(struct)
        spec = STRUCTURES.get(struct)
        if spec:
            for dep in spec.needs:
                visit(dep)
        ordered.append(struct)

    for unit in units:
        spec = UNITS.get(unit)
        if not spec:
            continue
        for struct in spec.needs:
            visit(struct)
    return ordered


def tier_required(units: List[U]) -> Tier:
    """Highest base tier any of ``units`` needs (Hatchery/Lair/Hive)."""
    tier = Tier.HATCHERY
    for unit in units:
        spec = UNITS.get(unit)
        if spec and spec.tier.value > tier.value:
            tier = spec.tier
    for struct in all_prerequisite_structures(units):
        spec = STRUCTURES.get(struct)
        if spec and spec.tier.value > tier.value:
            tier = spec.tier
    return tier
