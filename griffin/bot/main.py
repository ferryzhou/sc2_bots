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
    BuildStructure,
    BuildWorkers,
    ExpansionController,
    GasBuildingController,
    Mining,
    ProductionController,
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
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.data import Race
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

# Army composition consumed by SpawnController / ProductionController.
# Siege tanks are load-bearing vs the built-in cheater AIs: pure bio went
# 0-6 vs terran+protoss CheatVision across two timing sweeps, and HanBot
# (this repo's older Terran bot that beats cheater AIs) is bio+tank.
ARMY_COMP: dict[UnitID, dict] = {
    UnitID.MARINE: {"proportion": 0.5, "priority": 0},
    UnitID.MARAUDER: {"proportion": 0.2, "priority": 1},
    UnitID.SIEGETANK: {"proportion": 0.2, "priority": 0},
    UnitID.MEDIVAC: {"proportion": 0.1, "priority": 2},
}

# NOTE vs zerg: ladder-replay autopsies showed all four ladder losses to
# the remax cycle (griffin leads through 10-12min, then larvae rebuild the
# zerg army in minutes). A tank-heavy comp (30% tank / 15% medivac) was
# tried at both 55-supply and 40-supply attack timings and went 2-2 vs
# CheatVision zerg BOTH times (vs 2-0 typical for the default comp), with
# losses in long grind-downs. Reverted - the default comp stays; ladder
# TvZ remains an open problem needing a different idea (e.g. multi-prong
# or better re-engage discipline after a won fight).

# NOTE vs terran: a 10% VIKINGFIGHTER variant was tried and went 1-5
# (vs ~50% before) - air-only supply can't shoot the AI's ground push,
# so the ground army effectively fought at 90%. Reverted to the default
# comp; TvT instead attacks only at commit strength (like TvP below).

# vs protoss: instrumented losses showed an immortal/zealot/sentry/templar
# deathball wiping the whole army in one fight (immortals delete armored
# marauders+tanks, storm melts clumped bio). Ghosts are the counter: EMP
# strips shields and drains sentry/templar energy before the engagement.
ARMY_COMP_VS_PROTOSS: dict[UnitID, dict] = {
    UnitID.MARINE: {"proportion": 0.35, "priority": 1},
    UnitID.MARAUDER: {"proportion": 0.2, "priority": 1},
    UnitID.GHOST: {"proportion": 0.15, "priority": 0},
    UnitID.SIEGETANK: {"proportion": 0.2, "priority": 0},
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
    # long ladder games (two 60-min ties) reach these; a maxed 3-3 army
    # is how the eventual forced engagement gets won
    UpgradeId.TERRANINFANTRYWEAPONSLEVEL3,
    UpgradeId.TERRANINFANTRYARMORSLEVEL3,
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

TANK_TYPES: set[UnitID] = {UnitID.SIEGETANK, UnitID.SIEGETANKSIEGED}
# siege when ground targets are inside this; unsiege when none remain
# within a comfortably larger radius (hysteresis avoids mode-flapping)
SIEGE_AT_RANGE: float = 11.0
UNSIEGE_BEYOND_RANGE: float = 16.0

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
# with an overwhelming army, commit unconditionally: real-opponent games
# stalled to the 40-min wall timeout with a massed army cycling
# attack/regroup outside a defended base instead of finishing
COMMIT_AT_SUPPLY: float = 70.0
# hysteresis on attack/regroup flips: the combat sim swings wildly as
# enemy units enter/leave vision (TvT logs showed regroup->attack->regroup
# in one second), and each yo-yo bleeds units into the enemy's siege line
ATTACK_DECISION_COOLDOWN: float = 30.0
# stalemate breaker: two ladder games ended as 60-min ties with griffin
# camping at commit strength while the sim gate kept declining the fight.
# Past this time with a commit-strength army, attack permanently - a 3-3
# maxed push resolving the game beats a guaranteed half-point tie.
STALEMATE_AFTER: float = 1320.0
# NOTE: a heal-retreat discipline was tried here (fall back when the
# post-fight bio averaged <55% HP, re-attack at 70%) to counter the
# ladder remax anatomy - it went 2-4 vs CheatVision (baseline 5-1).
# Same lesson as every passivity lever on this bot: giving a cheater
# economy free time loses more than tired pushes do. Ladder-targeted
# behavior changes need ladder-realistic validation, not the gauntlet.
# contain-breaking: the terran AI sieges tanks + liberators just OUTSIDE
# the defend radius and fortifies while we turtle (TvT logs: home_threats=0
# for minutes, then LOSS_OVERWHELMING once the line crosses it). Siege
# units setting up this close to a base are engaged immediately.
CONTAIN_RADIUS: float = 40.0
CONTAIN_TYPES: set[UnitID] = {
    UnitID.SIEGETANK,
    UnitID.SIEGETANKSIEGED,
    UnitID.LIBERATOR,
    UnitID.LIBERATORAG,
    UnitID.WIDOWMINE,
    UnitID.WIDOWMINEBURROWED,
    UnitID.LURKERMP,
    UnitID.LURKERMPBURROWED,
    UnitID.COLOSSUS,
    UnitID.DISRUPTOR,
}
# vs protoss and terran, only attack at commit strength: instrumented
# losses in both matchups showed 40-50 supply pushes feeding a stronger
# army/siege line one at a time (45->9, rebuild, 46->8, eliminated) while
# macro easily sustained more - and the games griffin wins are the ones
# where it fights at 130+ supply
ATTACK_AT_SUPPLY_VS_PROTOSS: float = COMMIT_AT_SUPPLY
ATTACK_AT_SUPPLY_VS_TERRAN: float = COMMIT_AT_SUPPLY
# (a 55-supply zerg delay was also tried: 2-2, losses in 27/35-min games -
# early pressure is what beats zerg before the bank/remax scales)
DEFEND_RADIUS: float = 25.0

# Standing home guard: real-opponent losses (Stockfish, MicroMachine) came
# with 600-1300s of idle worker time - reaper/hellion harassment met zero
# resistance whenever the army was away, and any threat recalled the whole
# army instead. A small squad stays home; the main army is only recalled
# when the threat outweighs the guard.
HOME_GUARD_SUPPLY: float = 10.0
RECALL_MARGIN: float = 4.0


class GriffinBot(AresBot):
    expansions_generator: cycle
    current_base_target: Point2

    def __init__(self, game_step_override: Optional[int] = None):
        super().__init__(game_step_override)
        self._commenced_attack: bool = False
        self._emergency: bool = False
        self._last_threat_time: float = 0.0
        self._last_status_log: float = 0.0
        self._last_attack_decision: float = -999.0
        self._enemy_air_seen: bool = False

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
        self._counter_proxy_structures()
        self._build_turrets_vs_air()

        forces: Units = self.mediator.get_units_from_role(role=UnitRole.ATTACKING)
        forces_supply: float = self.get_total_supply(forces)
        guard: Units = self.mediator.get_units_from_role(role=UnitRole.BASE_DEFENDER)

        threats: Units = self._home_threats()
        if threats:
            threat: Unit = cy_closest_to(self.start_location, threats)
            # defend: during an early rush hold the ramp choke (don't chase
            # down the ramp into the flood) unless enemies are already inside
            target: Point2 = threat.position
            if self._emergency and threat.distance_to(self.start_location) > 18.0:
                target = self.main_base_ramp.top_center
            self._micro(guard, target=target)
            # during an emergency, an outnumbered defense also pulls SCVs -
            # the ZEALOCALYPSE 4-gate rolled the wall 30->1 supply in two
            # minutes while every SCV kept mining
            if self._emergency:
                combat_supply = forces_supply + self.get_total_supply(guard)
                if self.get_total_supply(threats) > combat_supply:
                    for scv in self.workers.sorted_by_distance_to(threat)[:12]:
                        if not scv.orders or scv.orders[0].ability.id not in (
                            AbilityId.ATTACK,
                            AbilityId.ATTACK_ATTACK,
                        ):
                            scv.attack(threat)
            # recall the main army when the guard is outmatched, and always
            # against a forming contain - siege lines only get stronger
            if (
                self._emergency
                or any(u.type_id in CONTAIN_TYPES for u in threats)
                or self.get_total_supply(threats)
                > self.get_total_supply(guard) + RECALL_MARGIN
            ):
                self._micro(forces, target=target)
                return
        else:
            # station the guard between the natural and the main, covering
            # both mineral lines against harassment
            station: Point2 = self.mediator.get_own_nat.towards(
                self.start_location, 4.0
            )
            grid: np.ndarray = self.mediator.get_ground_grid
            for unit in guard:
                if unit.distance_to(station) > 8.0:
                    maneuver: CombatManeuver = CombatManeuver()
                    maneuver.add(
                        PathUnitToTarget(unit=unit, grid=grid, target=station)
                    )
                    maneuver.add(AMove(unit=unit, target=station))
                    self.register_behavior(maneuver)

        # engagement gating: simulate the fight against the visible enemy
        # army before committing / while committed (ares combat sim) - the
        # instrumented TvP losses came from feeding 40-50 supply pushes
        # into a stronger deathball one at a time
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

        # periodic state line + attack/regroup transitions, for loss analysis
        if self.time - self._last_status_log >= 30.0:
            self._last_status_log = self.time
            enemy_comp: dict[str, int] = {}
            for u in enemy_army:
                enemy_comp[u.type_id.name] = enemy_comp.get(u.type_id.name, 0) + 1
            comp_str = ",".join(
                f"{n}:{c}"
                for n, c in sorted(enemy_comp.items(), key=lambda x: -x[1])[:6]
            )
            logger.info(
                f"{self.time_formatted} STATUS army={forces_supply:.0f} "
                f"guard={self.get_total_supply(guard):.0f} "
                f"bases={self.townhalls.amount} workers={self.workers.amount} "
                f"attacking={self._commenced_attack} fight={fight} "
                f"home_threats={self.get_total_supply(threats):.0f} "
                f"enemy=[{comp_str}]"
            )

        decision_ready: bool = (
            self.time - self._last_attack_decision >= ATTACK_DECISION_COOLDOWN
        )
        stalemate: bool = (
            self.time > STALEMATE_AFTER and forces_supply >= COMMIT_AT_SUPPLY
        )
        if self._commenced_attack:
            # supply crash aborts immediately; sim-based regroup respects
            # the cooldown so vision flicker can't thrash the state, and is
            # disabled entirely in stalemate mode - resolve the game
            if forces_supply < REGROUP_BELOW_SUPPLY or (
                not stalemate
                and decision_ready
                and fight is not None
                and fight in LOSS_CLOSE_OR_WORSE
            ):
                self._commenced_attack = False
                self._last_attack_decision = self.time
                logger.info(
                    f"{self.time_formatted} REGROUP at "
                    f"army={forces_supply:.0f} fight={fight}"
                )
        elif stalemate or decision_ready and (
            forces_supply >= COMMIT_AT_SUPPLY
            or (
                forces_supply >= self._attack_at_supply
                and (fight is None or fight in TIE_OR_BETTER)
                and (
                    (
                        self.units(UnitID.MEDIVAC).amount >= MEDIVACS_FOR_ATTACK
                        and UpgradeId.STIMPACK in self.state.upgrades
                    )
                    or self.time > ATTACK_ANYWAY_AFTER
                )
            )
        ):
            self._commenced_attack = True
            self._last_attack_decision = self.time
            logger.info(
                f"{self.time_formatted} ATTACK at "
                f"army={forces_supply:.0f} fight={fight}"
            )

        if self._commenced_attack:
            self._micro(forces, target=self.attack_target)
        else:
            # stage the army at the natural facing the map - the old main-ramp
            # rally left the natural CC exposed while turtling to commit
            # strength; tanks siege pre-emptively to anchor the defense
            rally: Point2 = self.mediator.get_own_nat.towards(
                self.game_info.map_center, 5.0
            )
            grid: np.ndarray = self.mediator.get_ground_grid
            for unit in forces:
                if unit.type_id == UnitID.SIEGETANK and unit.distance_to(rally) <= 8.0:
                    maneuver = CombatManeuver()
                    maneuver.add(
                        UseAbility(ability=AbilityId.SIEGEMODE_SIEGEMODE, unit=unit)
                    )
                    self.register_behavior(maneuver)
                elif unit.type_id == UnitID.SIEGETANKSIEGED:
                    continue  # hold the defensive siege while staging
                elif unit.distance_to(rally) > 8.0:
                    maneuver = CombatManeuver()
                    maneuver.add(PathUnitToTarget(unit=unit, grid=grid, target=rally))
                    maneuver.add(AMove(unit=unit, target=rally))
                    self.register_behavior(maneuver)

    async def on_unit_created(self, unit: Unit) -> None:
        await super(GriffinBot, self).on_unit_created(unit)
        if unit.type_id in WORKER_TYPES:
            return
        # keep the home guard topped up; medivacs always travel with the army
        guard: Units = self.mediator.get_units_from_role(role=UnitRole.BASE_DEFENDER)
        if (
            unit.type_id not in SUPPORT_TYPES
            and self.get_total_supply(guard) < HOME_GUARD_SUPPLY
        ):
            self.mediator.assign_role(tag=unit.tag, role=UnitRole.BASE_DEFENDER)
        else:
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

    @property
    def _army_comp(self) -> dict[UnitID, dict]:
        if self.enemy_race == Race.Protoss:
            return ARMY_COMP_VS_PROTOSS
        return ARMY_COMP

    @property
    def _attack_at_supply(self) -> float:
        if self.enemy_race == Race.Protoss:
            return ATTACK_AT_SUPPLY_VS_PROTOSS
        if self.enemy_race == Race.Terran:
            return ATTACK_AT_SUPPLY_VS_TERRAN
        return ATTACK_AT_SUPPLY

    def _counter_proxy_structures(self) -> None:
        """Cannon-rush / proxy response: pull SCVs onto proxy structures
        while they're building. Ladder loss to PerilousProtossBot: 4
        cannons at our main, dead by 6:00 with zero response."""
        proxies = [
            s
            for s in self.enemy_structures
            if any(s.distance_to(th) < 30.0 for th in self.townhalls)
        ]
        if not proxies or self.time > 420.0:
            return
        # prioritise unfinished cannons, then pylons
        proxies.sort(
            key=lambda s: (
                s.build_progress >= 1.0,
                s.type_id != UnitID.PHOTONCANNON,
            )
        )
        target = proxies[0]
        for scv in self.workers.sorted_by_distance_to(target)[:8]:
            if not scv.orders or scv.orders[0].ability.id not in (
                AbilityId.ATTACK,
                AbilityId.ATTACK_ATTACK,
            ):
                scv.attack(target)

    @staticmethod
    def _with_vikings(comp: dict[UnitID, dict]) -> dict[UnitID, dict]:
        """Blend a 20% viking share into a composition (proportions rescaled)."""
        blended = {
            k: {
                "proportion": round(v["proportion"] * 0.8, 3),
                "priority": v["priority"],
            }
            for k, v in comp.items()
        }
        blended[UnitID.VIKINGFIGHTER] = {"proportion": 0.2, "priority": 0}
        return blended

    def _build_turrets_vs_air(self) -> None:
        """Missile turrets at each mineral line once enemy air combat units
        are seen. Ladder loss to sharpy_protoss_test1: double-stargate void
        rays collapsed us 74->22 supply with marines as the only AA."""
        air_threats = [
            u
            for u in self.enemy_units
            if u.is_flying
            and (
                u.can_attack_ground
                or u.type_id in {UnitID.ORACLE, UnitID.LIBERATOR, UnitID.BANSHEE}
            )
        ]
        if not air_threats:
            return
        if not self._enemy_air_seen:
            self._enemy_air_seen = True
            logger.warning(
                f"{self.time_formatted} enemy air seen "
                f"({air_threats[0].type_id.name}) - adding vikings + turrets"
            )
        if not self.structures(UnitID.ENGINEERINGBAY):
            if (
                not self.already_pending(UnitID.ENGINEERINGBAY)
                and self.can_afford(UnitID.ENGINEERINGBAY)
            ):
                self.register_behavior(
                    BuildStructure(
                        base_location=self.start_location,
                        structure_id=UnitID.ENGINEERINGBAY,
                    )
                )
            return
        if self.already_pending(UnitID.MISSILETURRET) >= 2:
            return
        for th in self.townhalls.ready:
            if not self.structures(UnitID.MISSILETURRET).closer_than(
                12.0, th
            ) and self.can_afford(UnitID.MISSILETURRET):
                self.register_behavior(
                    BuildStructure(
                        base_location=th.position,
                        structure_id=UnitID.MISSILETURRET,
                    )
                )
                return

    def _home_threats(self) -> Units:
        """Enemy combat units near our townhalls, plus siege units forming
        a contain further out."""
        return Units(
            [
                u
                for u in self.enemy_units
                if u.type_id not in COMMON_UNIT_IGNORE_TYPES
                and not u.is_memory
                and any(
                    u.distance_to(th)
                    < (
                        CONTAIN_RADIUS
                        if u.type_id in CONTAIN_TYPES
                        else DEFEND_RADIUS
                    )
                    for th in self.townhalls
                )
            ],
            self,
        )

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
            comp = EMERGENCY_COMP if self._emergency else self._army_comp
            # reactive vikings: only once enemy air combat units are seen
            # (a permanent viking share was tried and went 1-5 - air-blind
            # supply can't shoot a ground push; see the vs-terran NOTE).
            # Air-heavy opponents (sharpy void rays, Asteria tempests) are
            # unanswerable without a mobile AA share.
            if self._enemy_air_seen and not self._emergency:
                comp = self._with_vikings(comp)
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
                # long games: keep taking bases so a mined-out economy
                # doesn't decide the 60-min grinds
                expansion_target = 4 if self.time < 900.0 else 6
                macro_plan.add(
                    ExpansionController(to_count=expansion_target, max_pending=1)
                )
                macro_plan.add(
                    GasBuildingController(to_count=len(self.townhalls) * 2)
                )
        else:
            macro_plan.add(SpawnController(self._army_comp))
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

            if unit.type_id in TANK_TYPES:
                self._tank_micro(unit, all_close, grid, target, maneuver)
                self.register_behavior(maneuver)
                continue

            if all_close:
                # EMP the shielded/energy deathball before shooting
                if (
                    unit.type_id == UnitID.GHOST
                    and unit.energy >= 75
                    and only_enemy_units
                ):
                    emp_target: Unit = cy_pick_enemy_target(only_enemy_units)
                    maneuver.add(
                        UseAbility(
                            ability=AbilityId.EMP_EMP,
                            unit=unit,
                            target=emp_target.position,
                        )
                    )
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

    def _tank_micro(
        self,
        unit: Unit,
        enemies_close: Units,
        grid: np.ndarray,
        target: Point2,
        maneuver: CombatManeuver,
    ) -> None:
        """Siege against nearby ground targets, unsiege and follow otherwise."""
        ground: Units = enemies_close.filter(lambda u: not u.is_flying)
        closest_dist: float = (
            unit.distance_to(cy_closest_to(unit.position, ground))
            if ground
            else 9999.0
        )
        if unit.type_id == UnitID.SIEGETANK:
            if closest_dist < SIEGE_AT_RANGE:
                maneuver.add(
                    UseAbility(ability=AbilityId.SIEGEMODE_SIEGEMODE, unit=unit)
                )
            else:
                maneuver.add(PathUnitToTarget(unit=unit, grid=grid, target=target))
                maneuver.add(AMove(unit=unit, target=target))
        else:  # sieged: hold and shoot; pack up only when nothing is in reach
            if closest_dist > UNSIEGE_BEYOND_RANGE:
                maneuver.add(
                    UseAbility(ability=AbilityId.UNSIEGE_UNSIEGE, unit=unit)
                )

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
