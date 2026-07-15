"""micro: unit-level combat control -- focus fire and kiting.

Principle #9, "micro to multiply your army": a controlled army out-trades an
a-moved one of the same size. This keeps the control **modular and table-driven**
rather than scattering ad-hoc rules through the army executor -- a unit's
behaviour follows from its *role* (ranged vs. melee), looked up in a small table,
so changing or adding micro is a table edit.

Two levers, both cheap and robust in python-sc2 (no pathing grid needed):

* **Focus fire.** The whole army converges fire on one priority target (something
  that shoots back, lowest effective HP first) so damage concentrates and kills
  land instead of spreading thinly -- the single biggest trade-efficiency win.
* **Kiting.** A ranged unit that out-ranges the nearest threat and is mid-reload
  steps back instead of standing still, so it takes free hits off melee chasers.
"""

from __future__ import annotations

from typing import List, Optional

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.unit import Unit

# Role table: ranged units kite while reloading; melee units just commit. Both
# focus-fire. Editing these sets is how you re-classify a unit's micro.
RANGED = {U.ROACH, U.RAVAGER, U.HYDRALISK, U.MUTALISK, U.CORRUPTOR,
          U.QUEEN, U.BROODLORD}
MELEE = {U.ZERGLING, U.BANELING, U.ULTRALISK}


def _hittable(unit: Unit, enemy: Unit) -> bool:
    return unit.can_attack_air if enemy.is_flying else unit.can_attack_ground


def army_focus(army: List[Unit], enemies: List[Unit]) -> Optional[Unit]:
    """One concentrate-fire target for the whole army: prefer things that can
    shoot back, then the lowest effective HP (finish kills)."""
    def score(e: Unit):
        return (0 if e.can_attack else 1, round(e.health + e.shield))

    # only consider enemies at least some of our units can actually hit
    targetable = [e for e in enemies if any(_hittable(u, e) for u in army)]
    if not targetable:
        return None
    return min(targetable, key=score)


def _in_range(unit: Unit, target: Unit) -> bool:
    rng = unit.air_range if target.is_flying else unit.ground_range
    return unit.distance_to(target) <= rng + unit.radius + target.radius


def command_unit(unit: Unit, focus: Unit, enemies: List[Unit], fallback,
                 kite: bool = True) -> None:
    """Micro a single unit toward the focus target (or fallback if none).

    ``kite=False`` makes ranged units hold ground and focus-fire instead of
    stepping back -- used on defence, where giving ground walks the enemy into
    the base.
    """
    if focus is None or not _hittable(unit, focus):
        # nothing this unit can shoot -- advance on the position
        unit.attack(fallback if not hasattr(focus, "position") else focus.position)
        return

    ranged = unit.type_id in RANGED and kite
    if ranged:
        # nearest enemy that can actually shoot us, to decide whether to kite
        threats = [e for e in enemies if e.can_attack]
        nearest = min(threats, key=unit.distance_to) if threats else None
        if unit.weapon_cooldown == 0 and _in_range(unit, focus):
            unit.attack(focus)                       # ready + in range: fire
        elif nearest is not None:
            enemy_rng = (nearest.air_range if unit.is_flying
                         else nearest.ground_range)
            outrange = unit.ground_range > enemy_rng + 0.5
            close = unit.distance_to(nearest) < enemy_rng + 1.5
            if outrange and close and unit.weapon_cooldown > 0:
                unit.move(unit.position.towards(nearest.position, -2.5))  # kite
            else:
                unit.attack(focus)
        else:
            unit.attack(focus)
    else:
        unit.attack(focus)                           # melee: commit to focus


def command_army(bot, army, fallback_pos, kite: bool = True) -> None:
    """Focus-fire the whole army against the enemies near it (kiting when
    ``kite`` and attacking in the open); if none are near, advance on
    ``fallback_pos``."""
    center = army.center
    enemies = [e for e in bot.enemy_units.closer_than(14, center)
               if not e.is_memory]
    if not enemies:
        for u in army:
            u.attack(fallback_pos)
        return
    focus = army_focus(list(army), enemies)
    for u in army:
        command_unit(u, focus, enemies, fallback_pos, kite=kite)
