"""GriffinBot - Terran bot built on ares-sc2.

v0 architecture (mirrors PhoenixBot):
- Opening from terran_builds.yml via the ares build runner.
- After the opening completes, ares macro controllers take over
  (supply, workers, production, expansions, gas, upgrades).
- Army control via ares CombatManeuver behaviors with cython micro helpers.
- Terran-specific plumbing: orbital morphs + MULE calldowns, stim micro,
  supply depot raise/lower.

The strategy layer is intentionally data-driven (army comp dict + builds yml)
so that future tooling can tune or swap strategies without touching code.
"""

from itertools import cycle
from typing import Optional

import numpy as np
from loguru import logger

import bot.compat  # noqa: F401 - 4.10 linux client compatibility patches
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from ares.behaviors.combat.individual import (
    AMove,
    KeepUnitSafe,
    PathUnitToTarget,
    ShootTargetInRange,
    StutterUnitBack,
    UseAbility,
)
from ares.behaviors.macro import (
    AutoSupply,
    BuildWorkers,
    ExpansionController,
    GasBuildingController,
    Mining,
    ProductionController,
    SpawnController,
    UpgradeController,
)
from ares.behaviors.macro.macro_plan import MacroPlan
from ares.consts import ALL_STRUCTURES, WORKER_TYPES, UnitRole, UnitTreeQueryType
from cython_extensions import cy_closest_to, cy_in_attack_range, cy_pick_enemy_target
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

# Army composition consumed by SpawnController / ProductionController.
ARMY_COMP: dict[UnitID, dict] = {
    UnitID.MARINE: {"proportion": 0.6, "priority": 0},
    UnitID.MARAUDER: {"proportion": 0.3, "priority": 1},
    UnitID.MEDIVAC: {"proportion": 0.1, "priority": 2},
}

# used while defending early aggression - marines only, no tech detours
EMERGENCY_COMP: dict[UnitID, dict] = {
    UnitID.MARINE: {"proportion": 1.0, "priority": 0},
}

# early-rush window: aggression detected before this triggers emergency mode
EARLY_THREAT_UNTIL: float = 300.0
# don't spend on ebay upgrades before this (mirrors the phoenix rush
# lessons); early enough that stim is done for the 40-supply push
UPGRADES_AFTER: float = 240.0

DESIRED_UPGRADES: list[UpgradeId] = [
    UpgradeId.STIMPACK,
    UpgradeId.SHIELDWALL,  # combat shield
    UpgradeId.TERRANINFANTRYWEAPONSLEVEL1,
    UpgradeId.PUNISHERGRENADES,  # concussive shells
    UpgradeId.TERRANINFANTRYARMORSLEVEL1,
    UpgradeId.TERRANINFANTRYWEAPONSLEVEL2,
    UpgradeId.TERRANINFANTRYARMORSLEVEL2,
]

COMMON_UNIT_IGNORE_TYPES: set[UnitID] = {
    UnitID.EGG,
    UnitID.LARVA,
    UnitID.CREEPTUMORBURROWED,
    UnitID.CREEPTUMORQUEEN,
    UnitID.CREEPTUMOR,
    UnitID.MULE,
}

# support units that should follow the army rather than stutter into it
SUPPORT_TYPES: set[UnitID] = {UnitID.MEDIVAC}

STIMABLE_TYPES: set[UnitID] = {UnitID.MARINE, UnitID.MARAUDER}
STIM_BUFFS: set[BuffId] = {BuffId.STIMPACK, BuffId.STIMPACKMARAUDER}

# Attack timing, calibrated by gauntlet sweeps vs CheatVision:
# - 28 supply, no gates: won vs zerg by constant pressure but 0-6 vs
#   terran+protoss (pushed without stim/medivacs, traded out, then
#   streamed reinforcements in piecemeal until eliminated)
# - 50 supply + 2 medivacs + 10:00 fallback + cohesion micro: 0-6 vs all
#   races - too passive, the cheater economy snowballs while bio waits
# Current: standard stim-timing push - 40 supply once stim + a medivac
# are in, with a 8:00 fallback so the army never sits home forever.
ATTACK_AT_SUPPLY: float = 40.0
REGROUP_BELOW_SUPPLY: float = 15.0
MEDIVACS_FOR_ATTACK: int = 1
ATTACK_ANYWAY_AFTER: float = 480.0
DEFEND_RADIUS: float = 25.0


class GriffinBot(AresBot):
    expansions_generator: cycle
    current_base_target: Point2

    def __init__(self, game_step_override: Optional[int] = None):
        super().__init__(game_step_override)
        self._commenced_attack: bool = False
        self._emergency: bool = False
        self._last_threat_time: float = 0.0

    async def on_start(self) -> None:
        await super(GriffinBot, self).on_start()
        self.current_base_target = self.enemy_start_locations[0]
        self.expansions_generator = cycle(list(self.expansion_locations_list))

    async def on_step(self, iteration: int) -> None:
        await super(GriffinBot, self).on_step(iteration)

        self._update_emergency()
        self._macro()
        self._manage_orbitals()
        self._manage_depots()

        forces: Units = self.mediator.get_units_from_role(role=UnitRole.ATTACKING)
        forces_supply: float = self.get_total_supply(forces)

        if threat := self._home_threat():
            # defend: during an early rush hold the ramp choke (don't chase
            # down the ramp into the flood) unless enemies are already inside
            target: Point2 = threat.position
            if self._emergency and threat.distance_to(self.start_location) > 18.0:
                target = self.main_base_ramp.top_center
            self._micro(forces, target=target)
            return

        if self._commenced_attack and forces_supply < REGROUP_BELOW_SUPPLY:
            self._commenced_attack = False
        elif (
            not self._commenced_attack
            and forces_supply >= ATTACK_AT_SUPPLY
            and (
                (
                    self.units(UnitID.MEDIVAC).amount >= MEDIVACS_FOR_ATTACK
                    and UpgradeId.STIMPACK in self.state.upgrades
                )
                or self.time > ATTACK_ANYWAY_AFTER
            )
        ):
            self._commenced_attack = True

        if self._commenced_attack:
            self._micro(forces, target=self.attack_target)
        else:
            # stage the army between our bases and the map center
            rally: Point2 = self.main_base_ramp.top_center.towards(
                self.game_info.map_center, 4.0
            )
            grid: np.ndarray = self.mediator.get_ground_grid
            for unit in forces:
                if unit.distance_to(rally) > 8.0:
                    maneuver: CombatManeuver = CombatManeuver()
                    maneuver.add(PathUnitToTarget(unit=unit, grid=grid, target=rally))
                    maneuver.add(AMove(unit=unit, target=rally))
                    self.register_behavior(maneuver)

    async def on_unit_created(self, unit: Unit) -> None:
        await super(GriffinBot, self).on_unit_created(unit)
        if unit.type_id not in WORKER_TYPES:
            self.mediator.assign_role(tag=unit.tag, role=UnitRole.ATTACKING)

    @property
    def attack_target(self) -> Point2:
        if self.enemy_structures:
            return cy_closest_to(self.start_location, self.enemy_structures).position
        elif self.time < 240.0:
            return self.enemy_start_locations[0]
        else:
            # nothing visible: sweep expansion locations
            if self.is_visible(self.current_base_target):
                self.current_base_target = next(self.expansions_generator)
            return self.current_base_target

    def _home_threat(self) -> Optional[Unit]:
        """Closest enemy combat unit near any of our townhalls, if any."""
        threats: list[Unit] = [
            u
            for u in self.enemy_units
            if u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and not u.is_memory
            and any(u.distance_to(th) < DEFEND_RADIUS for th in self.townhalls)
        ]
        if not threats:
            return None
        return cy_closest_to(self.start_location, Units(threats, self))

    def _early_aggression_seen(self) -> bool:
        """Enemy combat units or proxy structures near our main."""
        combat = [
            u
            for u in self.enemy_units
            if u.type_id not in WORKER_TYPES
            and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and not u.is_memory
            and u.distance_to(self.start_location) < 50.0
        ]
        proxy = [
            s
            for s in self.enemy_structures
            if s.distance_to(self.start_location) < 50.0
        ]
        return len(combat) >= 3 or len(proxy) >= 1

    def _update_emergency(self) -> None:
        """Rush defense mode: abort the opening, stop spending on greed."""
        if self._early_aggression_seen():
            self._last_threat_time = self.time
            if not self._emergency and self.time < EARLY_THREAT_UNTIL:
                self._emergency = True
                logger.warning(f"{self.time_formatted} EMERGENCY: early rush detected")
                if not self.build_order_runner.build_completed:
                    # hand control to the reactive macro plan immediately
                    self.build_order_runner.set_build_completed()
        elif self._emergency and self.time - self._last_threat_time > 45.0:
            self._emergency = False

    def _macro(self) -> None:
        self.register_behavior(Mining())

        macro_plan: MacroPlan = MacroPlan()
        if self.build_order_runner.build_completed:
            comp = EMERGENCY_COMP if self._emergency else ARMY_COMP
            macro_plan.add(AutoSupply(base_location=self.start_location))
            if self._emergency:
                # units and production only - no expansions, no upgrades,
                # no worker overinvestment until the rush is dead
                macro_plan.add(SpawnController(comp))
                macro_plan.add(
                    BuildWorkers(to_count=min(28, 22 * len(self.townhalls)))
                )
                macro_plan.add(
                    ProductionController(
                        comp,
                        base_location=self.start_location,
                        add_production_at_bank=(150, 0),
                    )
                )
            else:
                macro_plan.add(
                    BuildWorkers(to_count=min(66, 22 * len(self.townhalls)))
                )
                macro_plan.add(SpawnController(comp))
                # upgrades only once we're stable: past the rush window AND
                # holding a real army (same gating as phoenix)
                army_supply = self.supply_used - self.supply_workers
                if self.time > UPGRADES_AFTER and army_supply >= 12:
                    macro_plan.add(
                        UpgradeController(
                            upgrade_list=DESIRED_UPGRADES,
                            base_location=self.start_location,
                        )
                    )
                macro_plan.add(
                    ProductionController(comp, base_location=self.start_location)
                )
                macro_plan.add(ExpansionController(to_count=4, max_pending=1))
                macro_plan.add(
                    GasBuildingController(to_count=len(self.townhalls) * 2)
                )
        else:
            macro_plan.add(SpawnController(ARMY_COMP))
        self.register_behavior(macro_plan)

    def _manage_orbitals(self) -> None:
        """Morph finished CCs to orbitals and call down MULEs."""
        # morph: any plain command center once a barracks is done
        if self.structures(UnitID.BARRACKS).ready:
            for cc in self.townhalls(UnitID.COMMANDCENTER).ready.idle:
                if self.can_afford(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND):
                    cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)

        # MULEs: dump energy on the mineral line (keep 50 banked for scans
        # later; v0 doesn't scan, so just spend everything)
        for oc in self.townhalls(UnitID.ORBITALCOMMAND).filter(
            lambda th: th.energy >= 50
        ):
            if mfs := self.mineral_field.closer_than(10, oc):
                oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mfs.random)

    def _manage_depots(self) -> None:
        """Keep depots lowered unless enemy ground forces are close."""
        enemy_ground: Units = self.enemy_units.filter(
            lambda u: not u.is_flying
            and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and not u.is_memory
        )
        for depot in self.structures(UnitID.SUPPLYDEPOT).ready:
            if not enemy_ground.closer_than(10, depot):
                depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
        for depot in self.structures(UnitID.SUPPLYDEPOTLOWERED).ready:
            if enemy_ground.closer_than(8, depot):
                depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)

    def _micro(self, forces: Units, target: Point2) -> None:
        near_enemy: dict[int, Units] = self.mediator.get_units_in_range(
            start_points=forces,
            distances=15,
            query_tree=UnitTreeQueryType.AllEnemy,
            return_as_dict=True,
        )
        grid: np.ndarray = self.mediator.get_ground_grid
        bio: Units = forces.filter(lambda u: u.type_id not in SUPPORT_TYPES)
        bio_center: Point2 = bio.center if bio else target

        for unit in forces:
            maneuver: CombatManeuver = CombatManeuver()

            if unit.type_id in SUPPORT_TYPES:
                # medivacs: hug the bio ball (heal is autocast), run when low
                if unit.health_percentage < 0.5:
                    maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                maneuver.add(AMove(unit=unit, target=bio_center))
                self.register_behavior(maneuver)
                continue

            all_close: Units = near_enemy[unit.tag].filter(
                lambda u: not u.is_memory and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            )
            only_enemy_units: Units = all_close.filter(
                lambda u: u.type_id not in ALL_STRUCTURES
            )

            if all_close:
                self._maybe_stim(unit, only_enemy_units, maneuver)
                # shoot whatever is already in range (units before structures)
                if in_attack_range := cy_in_attack_range(unit, only_enemy_units):
                    maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_attack_range)
                    )
                elif in_attack_range := cy_in_attack_range(unit, all_close):
                    maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_attack_range)
                    )

                enemy_target: Unit = cy_pick_enemy_target(all_close)
                if unit.health_percentage < 0.3:
                    maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                else:
                    maneuver.add(
                        StutterUnitBack(unit=unit, target=enemy_target, grid=grid)
                    )
            else:
                maneuver.add(PathUnitToTarget(unit=unit, grid=grid, target=target))
                maneuver.add(AMove(unit=unit, target=target))

            self.register_behavior(maneuver)

    def _maybe_stim(
        self, unit: Unit, enemies_close: Units, maneuver: CombatManeuver
    ) -> None:
        """Stim healthy bio when real enemy units are in the fight."""
        if (
            unit.type_id in STIMABLE_TYPES
            and UpgradeId.STIMPACK in self.state.upgrades
            and unit.health_percentage > 0.6
            and not any(unit.has_buff(b) for b in STIM_BUFFS)
            and enemies_close
            and cy_in_attack_range(unit, enemies_close)
        ):
            maneuver.add(UseAbility(ability=AbilityId.EFFECT_STIM, unit=unit))
