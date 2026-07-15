"""strategies: the five high-level Zerg strategies, cheese -> turtle.

A ``StrategyProfile`` is a *declarative* description of one point on the
economy/army spectrum: how many drones to saturate to, what army to build, how
far to expand, how much to defend, and when to commit. It contains **no code and
no low-level rules** -- just the knobs. The planner turns a profile plus the live
game state into a concrete execution plan, and the selector decides which profile
to run (and switches between them mid-game).

The five profiles live in ``zerg_strategies.yml`` (the "strategies library") so
they can be tuned or extended without touching code. This module loads that file
into ``StrategyProfile`` objects and maps each profile onto the strategy_engine
spectrum (CHEESE_ALLIN .. TURTLE) so the selector can reason about them
generically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId


class Stance(Enum):
    """Where a strategy sits on the cheese->turtle spectrum.

    Deliberately mirrors strategy_engine.Archetype so the selector can line our
    own posture up against the *opponent's* archetype and its recommended
    counter with no ad-hoc mapping table.
    """

    CHEESE = "cheese"        # all army, no economy -- one-base all-in
    TIMING = "timing"        # army-heavy early pressure into a follow-up
    STANDARD = "standard"    # balanced macro
    GREEDY = "greedy"        # economy-first, out-expand, punish later
    TURTLE = "turtle"        # defend + tech to a strong late game

    @property
    def rank(self) -> int:
        order = [Stance.CHEESE, Stance.TIMING, Stance.STANDARD,
                 Stance.GREEDY, Stance.TURTLE]
        return order.index(self)


@dataclass
class StrategyProfile:
    """One high-level strategy. Pure data -- the planner interprets it."""

    name: str
    stance: Stance
    # economy
    drones_per_base: int = 20
    max_drones: int = 66
    queens_per_base: int = 1
    gas_per_base: int = 2
    expand_to: int = 3
    # army: desired composition as unit -> weight (planner normalises)
    army: Dict[U, float] = field(default_factory=dict)
    tech: List[U] = field(default_factory=list)          # extra units to unlock
    upgrades: List[UpgradeId] = field(default_factory=list)
    # defense (static structures at the most-forward base)
    spines_per_base: float = 0.0
    spores_per_base: float = 0.0
    # aggression / timing
    attack_supply: float = 40.0        # army supply to commit an attack
    regroup_supply: float = 10.0       # fall back below this
    harass: bool = False
    all_in: bool = False               # commit everything, don't defend/expand
    opening_only: bool = False         # can only be *chosen* in the opening

    @property
    def army_units(self) -> List[U]:
        """Every unit the strategy wants to be able to produce."""
        return list(dict.fromkeys(list(self.army.keys()) + list(self.tech)))


# --------------------------------------------------------------------------- #
# Loading the library from YAML.
# --------------------------------------------------------------------------- #
_STANCE_BY_NAME = {s.value: s for s in Stance}


def _resolve_unit(name: str) -> Optional[U]:
    try:
        return U[name.upper()]
    except KeyError:
        return None


def _resolve_upgrade(name: str) -> Optional[UpgradeId]:
    try:
        return UpgradeId[name.upper()]
    except KeyError:
        return None


def _profile_from_dict(name: str, d: dict) -> StrategyProfile:
    army: Dict[U, float] = {}
    for unit_name, weight in (d.get("army") or {}).items():
        unit = _resolve_unit(unit_name)
        if unit is not None:
            army[unit] = float(weight)
    tech = [u for u in (_resolve_unit(n) for n in d.get("tech") or []) if u]
    upgrades = [
        up for up in (_resolve_upgrade(n) for n in d.get("upgrades") or []) if up
    ]
    stance = _STANCE_BY_NAME[d["stance"]]
    return StrategyProfile(
        name=name,
        stance=stance,
        drones_per_base=int(d.get("drones_per_base", 20)),
        max_drones=int(d.get("max_drones", 66)),
        queens_per_base=int(d.get("queens_per_base", 1)),
        gas_per_base=int(d.get("gas_per_base", 2)),
        expand_to=int(d.get("expand_to", 3)),
        army=army,
        tech=tech,
        upgrades=upgrades,
        spines_per_base=float(d.get("spines_per_base", 0.0)),
        spores_per_base=float(d.get("spores_per_base", 0.0)),
        attack_supply=float(d.get("attack_supply", 40.0)),
        regroup_supply=float(d.get("regroup_supply", 10.0)),
        harass=bool(d.get("harass", False)),
        all_in=bool(d.get("all_in", False)),
        opening_only=bool(d.get("opening_only", False)),
    )


DEFAULT_LIBRARY = Path(__file__).resolve().parent.parent / "zerg_strategies.yml"


def load_library(path: Optional[Path] = None) -> Dict[str, StrategyProfile]:
    """Load the strategy library, keyed by profile name."""
    path = path or DEFAULT_LIBRARY
    data = yaml.safe_load(Path(path).read_text())
    profiles = {
        name: _profile_from_dict(name, d)
        for name, d in data["strategies"].items()
    }
    return profiles


def by_stance(library: Dict[str, StrategyProfile]) -> Dict[Stance, StrategyProfile]:
    """Index the library by stance (first profile wins if several share one)."""
    out: Dict[Stance, StrategyProfile] = {}
    for prof in library.values():
        out.setdefault(prof.stance, prof)
    return out
