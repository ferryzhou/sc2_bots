"""PhoenixBot - Protoss bot built on ares-sc2.

v0 architecture:
- Opening from protoss_builds.yml via the ares build runner.
- After the opening completes, ares macro controllers take over
  (supply, workers, production, expansions, gas, upgrades).
- Army control via ares CombatManeuver behaviors with cython micro helpers.

The strategy layer is intentionally data-driven (army comp dict + builds yml)
so that future tooling can tune or swap strategies without touching code.
"""

from itertools import cycle
from typing import Optional

import numpy as np
from loguru import logger

import bot.compat  # noqa: F401 - 4.10 linux client compatibility patches
from bot.tuning import Tuner
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
from sc2.ids.ability_id import AbilityId
from ares.behaviors.macro import (
    AutoSupply,
    BuildWorkers,
    ExpansionController,
    GasBuildingController,
    Mining,
    ProductionController,
    ProtossStaticDefence,
    SpawnController,
    UpgradeController,
)
from ares.behaviors.macro.macro_plan import MacroPlan
from ares.consts import (
    ALL_STRUCTURES,
    LOSS_CLOSE_OR_WORSE,
    TIE_OR_BETTER,
    WORKER_TYPES,
    UnitRole,
    UnitTreeQueryType,
)
from cython_extensions import cy_closest_to, cy_in_attack_range, cy_pick_enemy_target
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

# Army composition consumed by SpawnController / ProductionController.
# NOTE: an immortal-heavy variant (35% immortal priority 0) was tried and
# REGRESSED vs CheatInsane (7-5 vs 11-1, PvP 0-4): robo investment diluted
# army supply at the timings the enemy attacks. Revisit composition changes
# only with replay-driven loss analysis. See results/history_phoenix.jsonl
# run 20260709_022501.
ARMY_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 1.0, "priority": 0},
}

# late-game extension, gated on being maxed AND banking (so it can never
# dilute early army like the failed immortal experiment): colossus AoE is
# the close-out vs mass queen/ling turtles and maxed deathballs - the
# 47-min QueenBot ladder loss was won on trades (51k killed) but never
# closed
LATE_COMP: dict[UnitID, dict] = {
    UnitID.COLOSSUS: {"proportion": 0.2, "priority": 0},
    UnitID.STALKER: {"proportion": 0.8, "priority": 1},
}
LATE_COMP_SUPPLY: float = 180.0
LATE_COMP_BANK: int = 1200

# used while defending early aggression - zealots are the only gateway unit
# available before cybercore tech and hold rushes far better than nothing
EMERGENCY_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 0.5, "priority": 0},
    UnitID.ZEALOT: {"proportion": 0.5, "priority": 1},
}

# early-rush window: aggression detected before this triggers emergency mode
EARLY_THREAT_UNTIL: float = 300.0
# don't spend on forge/twilight upgrades before this (a 2:32 forge+twilight
# was the direct cause of rush losses - see the Chance loss analysis)
UPGRADES_AFTER: float = 300.0

DESIRED_UPGRADES: list[UpgradeId] = [
    UpgradeId.WARPGATERESEARCH,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1,
    UpgradeId.BLINKTECH,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL1,
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL2,
]

COMMON_UNIT_IGNORE_TYPES: set[UnitID] = {
    UnitID.EGG,
    UnitID.LARVA,
    UnitID.CREEPTUMORBURROWED,
    UnitID.CREEPTUMORQUEEN,
    UnitID.CREEPTUMOR,
    UnitID.MULE,
}

ATTACK_AT_SUPPLY: float = 26.0
REGROUP_BELOW_SUPPLY: float = 10.0
DEFEND_RADIUS: float = 25.0


class PhoenixBot(AresBot):
    expansions_generator: cycle
    current_base_target: Point2

    def __init__(self, game_step_override: Optional[int] = None):
        super().__init__(game_step_override)
        self._commenced_attack: bool = False
        self._emergency: bool = False
        self._last_threat_time: float = 0.0

    async def on_start(self) -> None:
        await super(PhoenixBot, self).on_start()
        self.current_base_target = self.enemy_start_locations[0]
        self.expansions_generator = cycle(list(self.expansion_locations_list))

        # continuous parameter learning: draw this game's strategy knobs
        # from the persisted search distribution (data dir survives between
        # ladder games, so learning continues on the arena)
        from pathlib import Path

        self._tuner = Tuner(Path("data"))
        p = self._tuner.ask()
        self._attack_at_supply: float = p["attack_at_supply"]
        self._pressure_valve_supply: float = p["pressure_valve_supply"]
        self._regroup_below_supply: float = p["regroup_below_supply"]
        self._emergency_exit_seconds: float = p["emergency_exit_seconds"]
        z = p["emergency_zealot_proportion"]
        self._emergency_comp: dict[UnitID, dict] = {
            UnitID.STALKER: {"proportion": round(1.0 - z, 3), "priority": 0},
            UnitID.ZEALOT: {"proportion": round(z, 3), "priority": 1},
        }
        logger.info(f"tuning sample: { {k: round(v, 2) for k, v in p.items()} }")

    async def on_end(self, game_result) -> None:
        score = self.state.score
        killed = float(
            (score.killed_value_units or 0)
            + (score.killed_value_structures or 0)
        )
        proto = score._proto
        lost = float(
            getattr(proto, "lost_minerals_army", 0)
            + getattr(proto, "lost_vespene_army", 0)
        )
        self._tuner.tell(
            won=str(game_result) == "Result.Victory",
            tied=str(game_result) == "Result.Tie",
            killed_value=killed,
            lost_value=lost,
        )
        await super(PhoenixBot, self).on_end(game_result)

    @property
    def _enemy_all_in(self) -> bool:
        """One-base all-in read: past the rush window but the enemy still
        hasn't expanded and shows a real army. The 4 midgame ladder losses
        (Klakinn/Montka/OneBaseStalkerBot/PiG_Bot) all died to this at
        8-11min: their army value was 2-6x ours while we teched/expanded."""
        if not (210.0 < self.time < 660.0):
            return False
        if self.mediator.get_enemy_expanded:
            return False
        enemy_army_supply = self.get_total_supply(
            self.enemy_units.filter(
                lambda u: u.type_id not in WORKER_TYPES
                and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            )
        )
        return (
            enemy_army_supply >= 10.0
            or self.mediator.get_enemy_went_four_gate
            or self.mediator.get_enemy_went_marine_rush
        )

    def _counter_proxy_structures(self) -> None:
        """Cannon-rush response: pull nearby probes onto proxy structures
        while they're building (cannons finished = too late). The 2 cannon
        losses ended with our supply collapsing 26->1 with zero response."""
        proxies = [
            s
            for s in self.enemy_structures
            if any(s.distance_to(th) < 30.0 for th in self.townhalls)
        ]
        if not proxies or self.time > 420.0:
            return
        # prioritise unfinished cannons, then pylons
        proxies.sort(key=lambda s: (s.build_progress >= 1.0,
                                    s.type_id != UnitID.PHOTONCANNON))
        target = proxies[0]
        pullers = self.workers.sorted_by_distance_to(target)[:8]
        for probe in pullers:
            if not probe.orders or probe.orders[0].ability.id not in (
                AbilityId.ATTACK, AbilityId.ATTACK_ATTACK
            ):
                probe.attack(target)

    async def on_step(self, iteration: int) -> None:
        await super(PhoenixBot, self).on_step(iteration)

        self._update_emergency()
        self._all_in_read: bool = self._enemy_all_in
        self._counter_proxy_structures()
        self._macro()

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

        # engagement gating: simulate the fight against the visible enemy
        # army before committing / while committed (ares combat sim)
        enemy_army: Units = self.enemy_units.filter(
            lambda u: u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and u.type_id not in WORKER_TYPES
            and not u.is_memory
        )
        fight = None
        if forces and enemy_army:
            fight = self.mediator.can_win_fight(
                own_units=forces,
                enemy_units=enemy_army,
                workers_do_no_damage=True,
            )

        if self._commenced_attack:
            if forces_supply < self._regroup_below_supply or (
                fight is not None and fight in LOSS_CLOSE_OR_WORSE
            ):
                self._commenced_attack = False
        elif forces_supply >= self._attack_at_supply and (
            fight is None
            or fight in TIE_OR_BETTER
            # pressure valve: near max supply nothing is gained by waiting -
            # attack even into a predicted loss rather than starve at home
            or forces_supply >= self._pressure_valve_supply
        ):
            # vs a one-base all-in, hold home-field advantage (wall +
            # batteries) instead of meeting the push in the open
            if not self._all_in_read:
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
        await super(PhoenixBot, self).on_unit_created(unit)
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
        # ares intel detections (race-aware, timing-tuned) plus our own
        # proximity heuristic as a catch-all
        intel_rush: bool = bool(
            self.mediator.get_did_enemy_rush or self.mediator.get_is_proxy_zealot
        )
        if intel_rush or self._early_aggression_seen():
            self._last_threat_time = self.time
            if not self._emergency and self.time < EARLY_THREAT_UNTIL:
                self._emergency = True
                logger.warning(f"{self.time_formatted} EMERGENCY: early rush detected")
                if not self.build_order_runner.build_completed:
                    # hand control to the reactive macro plan immediately
                    self.build_order_runner.set_build_completed()
        elif (
            self._emergency
            and self.time - self._last_threat_time > self._emergency_exit_seconds
        ):
            self._emergency = False

    def _macro(self) -> None:
        self.register_behavior(Mining())

        macro_plan: MacroPlan = MacroPlan()
        if self.build_order_runner.build_completed:
            if self._emergency:
                comp = self._emergency_comp
            elif (self.supply_used >= LATE_COMP_SUPPLY
                  and self.minerals >= LATE_COMP_BANK):
                comp = LATE_COMP
            else:
                comp = ARMY_COMP
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
                # a battery behind the wall is the strongest rush holder
                macro_plan.add(
                    ProtossStaticDefence(
                        pylons_per_base=1,
                        photon_cannons_per_base=0,
                        shield_batteries_per_base=1,
                    )
                )
            else:
                macro_plan.add(
                    BuildWorkers(to_count=min(66, 22 * len(self.townhalls)))
                )
                macro_plan.add(SpawnController(comp))
                # upgrades only once we're stable: past the rush window AND
                # holding a real army (a 5:00 forge while defending was a
                # second death spiral in the Chance loss analysis); never
                # while a one-base all-in is inbound
                army_supply = self.supply_used - self.supply_workers
                if (self.time > UPGRADES_AFTER and army_supply >= 16
                        and not self._all_in_read):
                    upgrades = list(DESIRED_UPGRADES)
                    if self.mediator.get_own_army_dict[UnitID.COLOSSUS]:
                        upgrades.append(UpgradeId.EXTENDEDTHERMALLANCE)
                    macro_plan.add(
                        UpgradeController(
                            upgrade_list=upgrades,
                            base_location=self.start_location,
                        )
                    )
                macro_plan.add(
                    ProductionController(comp, base_location=self.start_location)
                )
                # shield battery at each base (auto-techs its prerequisites);
                # cannons skipped to avoid an early forge detour
                macro_plan.add(
                    ProtossStaticDefence(
                        pylons_per_base=1,
                        photon_cannons_per_base=0,
                        shield_batteries_per_base=1,
                    )
                )
                # no new bases while a one-base all-in is inbound - units win
                # that fight, a half-built nexus doesn't
                if not self._all_in_read:
                    macro_plan.add(
                        ExpansionController(to_count=4, max_pending=1)
                    )
                macro_plan.add(
                    GasBuildingController(to_count=len(self.townhalls) * 2)
                )
        else:
            macro_plan.add(SpawnController(ARMY_COMP))
        self.register_behavior(macro_plan)

        self._chrono_production()

    def _chrono_production(self) -> None:
        structures_dict = self.mediator.get_own_structures_dict
        for th in self.townhalls:
            if th.energy >= 50:
                if busy := [
                    s
                    for type_id in (UnitID.ROBOTICSFACILITY, UnitID.GATEWAY)
                    for s in structures_dict[type_id]
                    if s.build_progress >= 1.0
                    and not s.is_idle
                    and not s.has_buff(BuffId.CHRONOBOOSTENERGYCOST)
                ]:
                    th(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])

    def _micro(self, forces: Units, target: Point2) -> None:
        near_enemy: dict[int, Units] = self.mediator.get_units_in_range(
            start_points=forces,
            distances=15,
            query_tree=UnitTreeQueryType.AllEnemy,
            return_as_dict=True,
        )
        grid: np.ndarray = self.mediator.get_ground_grid

        for unit in forces:
            maneuver: CombatManeuver = CombatManeuver()

            all_close: Units = near_enemy[unit.tag].filter(
                lambda u: not u.is_memory and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            )
            only_enemy_units: Units = all_close.filter(
                lambda u: u.type_id not in ALL_STRUCTURES
            )

            if all_close:
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
                if self._emergency and unit.type_id == UnitID.ZEALOT:
                    # holding a wall gap: kiting backwards opens the door,
                    # so zealots stand and fight
                    maneuver.add(AMove(unit=unit, target=enemy_target.position))
                elif unit.shield_percentage < 0.3:
                    maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                else:
                    maneuver.add(
                        StutterUnitBack(unit=unit, target=enemy_target, grid=grid)
                    )
            else:
                maneuver.add(PathUnitToTarget(unit=unit, grid=grid, target=target))
                maneuver.add(AMove(unit=unit, target=target))

            self.register_behavior(maneuver)
