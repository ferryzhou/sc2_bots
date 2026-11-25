"""PhoenixBot - Protoss bot built on ares-sc2.

v0 architecture:
- Opening from protoss_builds.yml via the ares build runner.
- After the opening completes, ares macro controllers take over
  (supply, workers, production, expansions, gas, upgrades).
- Army control via ares CombatManeuver behaviors with cython micro helpers.

The strategy layer is intentionally data-driven (army comp dict + builds yml)
so that future tooling can tune or swap strategies without touching code.
"""

import json
import os
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
    BuildStructure,
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
# only with replay-driven loss analysis. See phoenix/results/history.jsonl
# run 20260709_022501.
ARMY_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 1.0, "priority": 0},
}

# Gas-spending late composition. Diagnosed from the Hestia loss (27-min
# macro attrition): a pure-stalker army (125m/50g) is mineral-heavy, so
# with 2 assimilators/base we FLOODED gas (5176 unspent) while every
# mineral was spent and army production capped at 17 stalkers. Immortals
# (275m/100g, anti-armored - great vs Terran mech) and colossus
# (300m/200g, AoE) drain the excess gas AND give more army-value-per-
# mineral, easing the true constraint. Gated on time + gas bank (NOT
# supply, which floating prevents us from reaching) so it only kicks in
# once established and floating - never diluting early army like the
# always-on immortal experiment (cycle 8) that regressed.
LATE_COMP: dict[UnitID, dict] = {
    UnitID.IMMORTAL: {"proportion": 0.3, "priority": 0},
    UnitID.COLOSSUS: {"proportion": 0.2, "priority": 1},
    UnitID.STALKER: {"proportion": 0.5, "priority": 2},
}
# switch to the gas-spending comp once we're mid-game and floating gas
LATE_COMP_AFTER: float = 420.0  # 7:00
LATE_COMP_GAS_BANK: int = 300

# Reactive robo composition (Plan A). Pure stalkers have no answer to the
# ladder's most common counters - every recent macro loss traced to it:
# immortals (Chance), siege tanks (Stockfish), roaches (Persephone) all beat
# stalkers cost-for-cost, and zealot/ling floods (Klakinn, ZEALOCALYPSE)
# overrun them. The fix is composition (Principle 8) teched REACTIVELY to
# scouting (Principle 10), NOT always-on: an always-on 35% immortal comp
# REGRESSED (cycle 8, PvP 0-4) by diluting army at attack timings. So we only
# add robo units once we actually see the enemy army they counter.
#
# vs an armored enemy army (roach / immortal / stalker / marauder / tank /
# thor) -> immortals (bonus vs armored, and gas-heavy so they drain float).
IMMORTAL_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 0.65, "priority": 0},
    UnitID.IMMORTAL: {"proportion": 0.35, "priority": 1},
}
# vs a massed-light enemy army (zealot / zergling / marine / hydra flood)
# -> colossus (AoE splash shreds clumped light).
COLOSSUS_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 0.75, "priority": 0},
    UnitID.COLOSSUS: {"proportion": 0.25, "priority": 1},
}
# vs mixed armored+light armies (e.g. BioBot2.0 marine/marauder/tank or
# Lissy roach/ling/hydra): need BOTH immortals for armored AND colossus splash
# for clumped light instead of choosing only immortals (0 colossus vs 122
# marines in the 2026-08-22 BioBot2.0 loss).
MIXED_ROBO_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 0.55, "priority": 0},
    UnitID.IMMORTAL: {"proportion": 0.25, "priority": 1},
    UnitID.COLOSSUS: {"proportion": 0.20, "priority": 2},
}
# supply of scouted enemy armored / light army value that triggers the switch
# (a real presence, not one stray unit) - keeps the opening on pure stalkers
ARMORED_TRIGGER: float = 8.0
LIGHT_TRIGGER: float = 14.0
# enemy FLYING army supply past this (and outweighing their ground) locks the
# comp to pure stalker - immortal/colossus can't shoot up (42-VoidRay Arpy loss)
AIR_TRIGGER: float = 12.0

# Cloak / burrow units and tech structures that require Observer detection
# (2026-08-22 Hestia loss to 4 cloaked Banshees, Lissy 3-28 loss to burrowed
# Lurkers -- Phoenix previously never trained an Observer).
CLOAK_BURROW_UNITS: set[UnitID] = {
    UnitID.BANSHEE,
    UnitID.DARKTEMPLAR,
    UnitID.LURKERMP,
    UnitID.LURKERMPBURROWED,
    UnitID.WIDOWMINE,
    UnitID.WIDOWMINEBURROWED,
    UnitID.GHOST,
    UnitID.ROACHBURROWED,
    UnitID.INFESTOR,
    UnitID.INFESTORBURROWED,
    UnitID.SWARMHOSTMP,
    UnitID.SWARMHOSTBURROWEDMP,
}
CLOAK_BURROW_STRUCTURES: set[UnitID] = {
    UnitID.DARKSHRINE,
    UnitID.LURKERDENMP,
    UnitID.GHOSTACADEMY,
    UnitID.STARPORTTECHLAB,
}

# used while defending early aggression - zealots are the only gateway unit
# available before cybercore tech and hold rushes far better than nothing
EMERGENCY_COMP: dict[UnitID, dict] = {
    UnitID.STALKER: {"proportion": 0.5, "priority": 0},
    UnitID.ZEALOT: {"proportion": 0.5, "priority": 1},
}

# build-order watchdog: the ares build runner can stall forever if an
# opening step is denied (early pressure blocking the expansion step is the
# usual cause). While stalled, build_completed stays False and the macro
# fallback runs almost nothing - two ladder losses (StarK234, Princess-Mika)
# froze at ~45 supply / 2 gateways and floated 9-12k minerals, never handing
# off to the macro controllers. Force the handoff once the opening has
# clearly overrun (past this time, or past this supply - both well beyond a
# healthy opening's ~27-supply endpoint) so full macro always resumes.
BUILD_ORDER_DEADLINE: float = 200.0
BUILD_ORDER_SUPPLY_CAP: float = 36.0

# early-rush window: aggression detected before this triggers emergency mode
EARLY_THREAT_UNTIL: float = 300.0

# scout-driven opening switch: if we scout a COMMITTED one-base all-in (no
# natural + >=2 production + >=2 gas) before we'd take our own natural, switch
# the opening to OneBaseDefense. ares' get_enemy_four_gate needs 3 gates by
# 3:20, but a one-base stalker all-in only lands its 3rd gate ~3:16 -- after
# our SafeExpand nexus (supply 27, ~3:29). The 2-gate + 2-gas + no-natural
# tell is visible ~2:15-2:30, early enough to preempt our expansion.
DEFENSE_SWITCH_UNTIL: float = 210.0
ONE_BASE_MIN_GATES: int = 2
ONE_BASE_MIN_GAS: int = 2
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
    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3,
    UpgradeId.PROTOSSGROUNDARMORSLEVEL3,
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
        self._defense_opening: bool = False
        self._switched_to_defense: bool = False
        self._posthold_logged: bool = False
        self._need_detection: bool = False
        self._detection_logged: bool = False
        self._last_threat_time: float = 0.0
        # per-stalker blink cooldown tracking (blink is ~11s; avoids an
        # async get_available_abilities call per unit each frame)
        self._blinked_at: dict[int, float] = {}

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
        # controlled-experiment hook: pin any subset of params to fixed
        # values (JSON) so an A/B can isolate one knob. Does not affect the
        # ladder (env var unset there); tell() still records the real result.
        override = os.environ.get("PHOENIX_PARAM_OVERRIDE")
        if override:
            p.update(json.loads(override))
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

    def _enemy_committed_one_base(self) -> bool:
        """Scouted tell of a committed one-base all-in, EARLY enough to react
        (before our own natural). Enemy has no second base yet but is pouring
        into one-base production + double gas:
          - Protoss: >=2 gateways AND >=2 assimilators (OneBaseStalkerBot)
          - Terran:  >=2 barracks AND >=2 refineries (oberon 1-base marauder)
        Structures persist as snapshots once scouted, so a scout that dies
        after one look still counts."""
        if self.mediator.get_enemy_expanded:
            return False
        gates = self.enemy_structures.filter(
            lambda s: s.type_id in (UnitID.GATEWAY, UnitID.WARPGATE)
        ).amount
        p_gas = self.enemy_structures(UnitID.ASSIMILATOR).amount
        if gates >= ONE_BASE_MIN_GATES and p_gas >= ONE_BASE_MIN_GAS:
            return True
        rax = self.enemy_structures.filter(
            lambda s: s.type_id in (UnitID.BARRACKS, UnitID.BARRACKSFLYING)
        ).amount
        t_gas = self.enemy_structures(UnitID.REFINERY).amount
        return rax >= ONE_BASE_MIN_GATES and t_gas >= ONE_BASE_MIN_GAS

    def _enemy_proxy_aggression(self) -> bool:
        """Proxy all-in tell that _enemy_committed_one_base MISSES: proxy
        4-gate (ZEALOCALYPSE) or proxy barracks (oberon) builds production
        FORWARD near our base. Use ares' proxy read plus our own proximity
        check on any enemy proxy structure near OUR start location."""
        if self.mediator.get_is_proxy_zealot:
            return True
        return any(
            s.type_id
            in (
                UnitID.GATEWAY,
                UnitID.WARPGATE,
                UnitID.PYLON,
                UnitID.BARRACKS,
                UnitID.BUNKER,
                UnitID.FACTORY,
            )
            and s.distance_to(self.start_location) < 65.0
            for s in self.enemy_structures
        )

    def _maybe_switch_to_defense(self) -> None:
        """Before we commit to our economic expansion, if the scout reads a
        committed one-base all-in (home tech OR a forward proxy), switch the
        opening to OneBaseDefense (no expo, 4-gate + gas + cyber behind the
        wall). This closes the gap the GateExpand removal only narrowed:
        SafeExpand still expands at ~3:29 and loses the midgame production race.
        Fires once, only while the opening is still running and before ~3:30 so
        it preempts the natural."""
        if (
            self._switched_to_defense
            or self.build_order_runner.build_completed
            or self.build_order_runner.chosen_opening == "OneBaseDefense"
            or self.time > DEFENSE_SWITCH_UNTIL
        ):
            return
        proxy = self._enemy_proxy_aggression()
        if self._enemy_committed_one_base() or proxy:
            self.build_order_runner.switch_opening("OneBaseDefense")
            self._switched_to_defense = True
            reason = "proxy all-in" if proxy else "committed one-base all-in"
            logger.warning(
                f"{self.time_formatted} SCOUT SWITCH -> OneBaseDefense ({reason})"
            )

    def _update_detection(self) -> None:
        """Latch detection need once any cloaked/burrowed unit or cloak/burrow
        tech building is scouted (Hestia Banshees, Lissy Lurkers, DTs, Widow
        Mines). Stays latched so Observers are replaced if sniped."""
        if self._need_detection:
            return
        found = any(
            u.is_cloaked or u.is_burrowed or u.type_id in CLOAK_BURROW_UNITS
            for u in self.enemy_units
        )
        if not found:
            found = any(
                u.type_id in CLOAK_BURROW_UNITS
                for units in self.mediator.get_enemy_army_dict.values()
                for u in units
            )
        if not found:
            found = any(
                s.type_id in CLOAK_BURROW_STRUCTURES
                for s in self.enemy_structures
            )
        if found:
            self._need_detection = True
            if not self._detection_logged:
                self._detection_logged = True
                logger.warning(
                    f"{self.time_formatted} DETECTION NEEDED: cloak/burrow threat scouted"
                )

    def _production_base(self) -> Point2:
        """Return a live, safe base location for macro building placement.

        Hardcoding self.start_location caused 4.5-5 minute production freezes
        in the Arpy and DemsTossV2 losses once the main base lost its pylons
        or Nexus: replacement CyberneticsCore / Pylons / Gateways couldn't
        place at the dead main. Prefer start_location while a ready Nexus
        stands there uncontested, else fall back to the safest ready Nexus.
        """
        ready_th = self.townhalls.ready
        if not ready_th:
            return self.start_location
        main_th = ready_th.closer_than(10.0, self.start_location)
        if main_th:
            enemy_in_main = self.enemy_units.filter(
                lambda u: u.type_id not in WORKER_TYPES
                and u.type_id not in COMMON_UNIT_IGNORE_TYPES
                and not u.is_memory
                and u.distance_to(self.start_location) < 18.0
            )
            if not enemy_in_main or len(ready_th) == 1:
                return self.start_location
        # Fall back to the ready Nexus furthest from visible enemy combat units
        enemy_combat = self.enemy_units.filter(
            lambda u: u.type_id not in WORKER_TYPES
            and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and not u.is_memory
        )
        if not enemy_combat:
            return ready_th.closest_to(self.start_location).position
        return max(
            ready_th,
            key=lambda th: enemy_combat.closest_distance_to(th.position),
        ).position

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

    def _enemy_armored_light_supply(self) -> tuple[float, float]:
        """Scouted enemy GROUND army supply split into armored vs light. Uses
        ares' cached enemy army dict (includes remembered units), so a unit
        seen once still counts even after it leaves vision. Flyers are excluded:
        this read drives the robo comp (immortal/colossus), and BOTH are
        ground-only - counting mutalisks as 'light' picked colossus (which can't
        even hit air) vs the kas muta/ultra army while the Ultralisks that
        actually needed immortals went unanswered. Stalkers cover air."""
        armored = light = 0.0
        for units in self.mediator.get_enemy_army_dict.values():
            for u in units:
                if u.type_id in WORKER_TYPES or u.is_flying:
                    continue
                sup = self.calculate_supply_cost(u.type_id)
                if u.is_armored:
                    armored += sup
                elif u.is_light:
                    light += sup
        return armored, light

    def _enemy_air_supply(self) -> float:
        """Scouted enemy FLYING army supply (overlords cost 0 so they don't
        count). Drives the anti-air guard below."""
        air = 0.0
        for units in self.mediator.get_enemy_army_dict.values():
            for u in units:
                if u.is_flying and u.type_id not in WORKER_TYPES:
                    air += self.calculate_supply_cost(u.type_id)
        return air

    def _won_the_hold(self) -> bool:
        """The all-in is weathered and we're clearly ahead - convert the won
        defense into ECONOMY. The 08-18 OneBaseStalkerBot ladder loss: Phoenix
        held, led 2450v1050 at 10:00, yet sat on ONE base for 19 minutes, mined
        out and collapsed 0v3500. Reproduced in sparring (17.5-min grind, Nexus
        x1 the whole game). Ahead = past the all-in's peak window, holding a
        real army, and at least 1.5x the scouted enemy army supply."""
        if self.time < 420.0:
            return False
        own = self.supply_used - self.supply_workers
        enemy = 0.0
        for units in self.mediator.get_enemy_army_dict.values():
            for u in units:
                if u.type_id not in WORKER_TYPES:
                    enemy += self.calculate_supply_cost(u.type_id)
        return own >= 20.0 and own >= 1.5 * max(enemy, 1.0)

    def _choose_army_comp(self) -> dict[UnitID, dict]:
        """Reactive composition: answer the scouted enemy army. Robo units are
        added only once we actually see the army they counter, never during
        the opening/all-in window - that reactivity is what separates this
        from the always-on immortal comp that regressed."""
        armored, light = self._enemy_armored_light_supply()
        # anti-air guard: vs a real AIR army, robo splash is a dead spend --
        # immortals and colossus cannot shoot up. The 26-min Arpy loss massed
        # 42 Void Rays while our 32-zealot ground read teched colossus; every
        # robo mineral was wasted. Stalkers are our only scalable AA, so once
        # the enemy's air outweighs their ground army, stay on pure stalkers.
        air = self._enemy_air_supply()
        if air >= AIR_TRIGGER and air > max(armored, light):
            return ARMY_COMP
        # mixed armored + light army (e.g. Terran bio/tank or Zerg roach/ling/
        # hydra): build BOTH immortals and colossus splash instead of 0 splash
        if armored >= ARMORED_TRIGGER and light >= LIGHT_TRIGGER:
            return MIXED_ROBO_COMP
        # armored takes precedence (immortals also beat the light-vs-colossus
        # case acceptably, and armored is the deadlier miss for stalkers)
        if armored >= ARMORED_TRIGGER and armored >= light:
            return IMMORTAL_COMP
        if light >= LIGHT_TRIGGER and light > armored:
            return COLOSSUS_COMP
        # no clear read yet: drain floating gas mid-game (old LATE_COMP), else
        # the mineral-cheap stalker default
        if self.time > LATE_COMP_AFTER and self.vespene > LATE_COMP_GAS_BANK:
            return LATE_COMP
        return ARMY_COMP

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

        self._maybe_switch_to_defense()
        self._update_detection()
        self._all_in_read: bool = self._enemy_all_in
        # a chosen defensive opening commits us to the anti-all-in posture
        # while the opponent is actually on one base. Release immediately if
        # we scout an enemy expansion (Slenderina / Thssprtssbt took 2-4 bases
        # while Phoenix sat locked in OneBaseDefense until 7:30).
        self._defense_opening = (
            self.build_order_runner.chosen_opening == "OneBaseDefense"
            and self.time < 450.0
            and not self.mediator.get_enemy_expanded
        )
        if self._defense_opening:
            self._all_in_read = True
        self._update_emergency()
        self._counter_proxy_structures()
        self._macro()

        forces: Units = self.mediator.get_units_from_role(role=UnitRole.ATTACKING)
        forces_supply: float = self.get_total_supply(forces)
        self._micro_observers(forces)

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
        if unit.type_id == UnitID.OBSERVER:
            return
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
        # Two triggers: an EARLY rush (proximity / intel, <5min) OR a
        # mid-game ONE-BASE ALL-IN (_all_in_read, 3:30-11min). The latter
        # was the gap: one-base timings (ZEALOCALYPSE, OneBaseStalkerBot)
        # hit at 6-10min - past the early window - and out-produced us 2-4x
        # while we kept our economic opening. Both now abort the build and
        # drop into lockdown (pump army + batteries, no expand/greed).
        early_rush = (intel_rush or self._early_aggression_seen()) and (
            self.time < EARLY_THREAT_UNTIL
        )
        # a WON hold ends the lockdown - and blocks re-entry while we stay
        # clearly ahead. The all-in read alone kept emergency alive until
        # ~12:00 vs early-pressure opponents, and the lockdown's costs (28-
        # worker cap, zealot-heavy comp, no robo/upgrades) are what lost the
        # DemsTossV2-style grinds: we sat on 28 workers making zealots while
        # they macroed to 80 probes and teched immortals.
        if self._won_the_hold():
            if self._emergency:
                self._emergency = False
                logger.warning(
                    f"{self.time_formatted} POST-HOLD: lockdown released "
                    f"(clearly ahead) - resuming full macro"
                )
            return
        if early_rush or self._all_in_read:
            self._last_threat_time = self.time
            if not self._emergency:
                self._emergency = True
                reason = "early rush" if early_rush else "one-base all-in"
                logger.warning(f"{self.time_formatted} EMERGENCY: {reason}")
                # abort an ECONOMIC opening to react - but NOT the OneBaseDefense
                # opening, which IS the response and must be allowed to run (its
                # wall + 4 gates + gas + cyber ARE our defense). Aborting it at
                # t=0 left us at 22 supply / 0 army - it completed instantly.
                if (not self.build_order_runner.build_completed
                        and not self._defense_opening):
                    self.build_order_runner.set_build_completed()
        elif (
            self._emergency
            and self.time - self._last_threat_time > self._emergency_exit_seconds
        ):
            self._emergency = False

    def _desired_bases(self, army_supply: float) -> int:
        """Healthy target Nexus count based on game clock, worker saturation,
        and army safety (Rule 4: Expand). Used to reserve 400 minerals ahead
        of SpawnController so WarpGates don't starve expansions forever
        (Terranosaur 1-base 12.5m, Lissy/sharpy 2-base 15-16m losses)."""
        target = 1
        if self.time >= 160.0 or self.supply_workers >= 18:
            target = 2
        if (
            self.time >= 330.0
            and self.supply_workers >= 34
            and army_supply >= 16.0
        ):
            target = 3
        if (
            self.time >= 510.0
            and self.supply_workers >= 54
            and army_supply >= 28.0
        ):
            target = 4
        if (
            self.time >= 690.0
            and self.supply_workers >= 70
            and army_supply >= 40.0
        ):
            target = 5
        return target

    def _train_observers(self) -> bool:
        """Train Observers from ready idle Robotics Facilities.

        Returns True when we urgently need our first Observer (cloak/burrow
        threat scouted, 0 alive/pending, ready idle Robo) and are saving the
        75 gas so SpawnController doesn't steal it for a Stalker.
        """
        robos = self.structures(UnitID.ROBOTICSFACILITY).ready
        if not robos:
            return False
        want_obs = 2 if self._need_detection else (1 if self.time >= 300.0 else 0)
        if want_obs == 0:
            return False
        obs_total = self.units(UnitID.OBSERVER).amount + self.already_pending(
            UnitID.OBSERVER
        )
        if obs_total >= want_obs:
            return False
        idle_robos = robos.idle
        if not idle_robos:
            return False
        if self.can_afford(UnitID.OBSERVER) and self.supply_left >= 1:
            idle_robos.first.train(UnitID.OBSERVER)
            return False
        return self._need_detection and obs_total == 0

    def _micro_observers(self, forces: Units) -> None:
        """Keep Observers covering cloaked/burrowed threats or escorting the
        main army just behind the front line so they aren't sniped."""
        observers = self.units(UnitID.OBSERVER)
        if not observers:
            return
        hidden = self.enemy_units.filter(
            lambda u: not u.is_memory
            and (
                u.is_cloaked
                or u.is_burrowed
                or u.type_id in CLOAK_BURROW_UNITS
            )
        )
        home_hidden = hidden.filter(
            lambda u: any(u.distance_to(th) < 30.0 for th in self.townhalls)
        )
        army_center: Point2 = (
            forces.center if forces else self.main_base_ramp.top_center
        )
        for idx, obs in enumerate(observers):
            if home_hidden and (idx == 0 or len(observers) == 1):
                t = home_hidden.closest_to(obs)
                dest = t.position.towards(obs.position, 3.0)
            elif hidden and idx == 0:
                t = hidden.closest_to(army_center)
                dest = t.position.towards(army_center, 3.0)
            elif idx == 0 and forces:
                dest = army_center.towards(self.start_location, 3.0)
            elif self.townhalls:
                # second observer guards our most exposed expansion
                exposed = max(
                    self.townhalls,
                    key=lambda th: th.distance_to(self.start_location),
                )
                dest = exposed.position
            else:
                dest = army_center
            if obs.distance_to(dest) > 2.5:
                obs.move(dest)

    def _macro(self) -> None:
        # build-order watchdog: if the ares build runner has stalled (an
        # opening step denied, build_completed stuck False past a healthy
        # opening), force the handoff so the full macro stack - AutoSupply,
        # BuildWorkers, ProductionController, ExpansionController - resumes
        # instead of the near-empty fallback branch. Fires once; guards the
        # macro-freeze losses where we floated 9-12k minerals stuck at ~45
        # supply. Emergency already force-completes on rushes; this covers
        # the non-rush stalls (macro opponents that contest our expansion).
        if not self.build_order_runner.build_completed and (
            self.time > BUILD_ORDER_DEADLINE
            or self.supply_used >= BUILD_ORDER_SUPPLY_CAP
        ):
            logger.warning(
                f"{self.time_formatted} build-order watchdog: forcing "
                f"handoff to macro (t={self.time:.0f} supply={self.supply_used})"
            )
            self.build_order_runner.set_build_completed()

        # dynamic gas throttle: our army is mineral-heavy, so when gas is
        # flooding (the Hestia loss floated 5k+) ease workers off gas onto
        # minerals - cuts the waste AND speeds us toward max supply, which
        # mineral income (not gas) gates. Gentle (2, not 1) so it never
        # starves the gas-heavy immortal/colossus comp.
        workers_per_gas = 2 if self.vespene > 800 else 3
        self.register_behavior(Mining(workers_per_gas=workers_per_gas))

        prod_base: Point2 = self._production_base()
        macro_plan: MacroPlan = MacroPlan()
        if self.build_order_runner.build_completed:
            if self._emergency:
                # rush defense: gateway units + batteries, no robo detour.
                # In the dedicated one-base defense we know it's a ranged/armored
                # all-in - pump PURE stalkers (zealots just get kited); otherwise
                # the stalker/zealot mix (zealots tank light floods).
                comp = ARMY_COMP if self._defense_opening else self._emergency_comp
            elif self._all_in_read:
                # one-base all-in inbound: robo tech is too slow to matter,
                # pump gateway army now
                comp = ARMY_COMP
            else:
                # reactive robo composition vs the scouted enemy army
                comp = self._choose_army_comp()

            macro_plan.add(AutoSupply(base_location=prod_base))

            # Train Observers ahead of SpawnController so Stalkers don't drain
            # the 75 gas needed for detection against cloaked/burrowed units.
            saving_for_observer = self._train_observers()

            # Rebuild CyberneticsCore immediately at a live base if lost
            # (Arpy / DemsTossV2 froze for 4.5-5 min floating 3k+ when the
            # single ramp CyberCore died).
            has_gate = bool(
                self.structures(UnitID.GATEWAY).ready
                or self.structures(UnitID.WARPGATE).ready
            )
            if has_gate and not self.structure_present_or_pending(
                UnitID.CYBERNETICSCORE
            ):
                macro_plan.add(
                    BuildStructure(
                        base_location=prod_base,
                        structure_id=UnitID.CYBERNETICSCORE,
                        to_count=1,
                    )
                )

            # Build a Robotics Facility immediately when cloak/burrow is
            # scouted and we don't have one yet (Hestia Banshees, Lissy Lurkers).
            saving_for_robo = False
            if (
                self._need_detection
                and self.structures(UnitID.CYBERNETICSCORE).ready
                and not self.structure_present_or_pending(
                    UnitID.ROBOTICSFACILITY
                )
            ):
                macro_plan.add(
                    BuildStructure(
                        base_location=prod_base,
                        structure_id=UnitID.ROBOTICSFACILITY,
                        to_count=1,
                    )
                )
                saving_for_robo = not self.can_afford(UnitID.ROBOTICSFACILITY)

            # post-hold conversion: once the all-in hold is clearly won, take
            # the natural. Merely adding an ExpansionController is NOT enough -
            # it has no mineral reservation, and SpawnController's continuous
            # spend pins the bank under ~105 (verified in the grind repro), so
            # the nexus never gets funded. While converting, the plan is ONLY
            # supply + expansion - army production pauses the ~40s it takes to
            # bank 400 (we are >=1.5x ahead by definition, so that is safe).
            posthold_expand = (
                (self._emergency or self._all_in_read)
                and self._won_the_hold()
                and len(self.townhalls) < 2
                and not self.already_pending(UnitID.NEXUS)
            )
            if posthold_expand and not self._posthold_logged:
                self._posthold_logged = True
                logger.warning(
                    f"{self.time_formatted} POST-HOLD: won the defense, "
                    f"converting - taking the natural"
                )
            if posthold_expand:
                macro_plan.add(ExpansionController(to_count=2, max_pending=1))
            elif self._emergency:
                # units and production only - no expansions, no upgrades,
                # no worker overinvestment until the rush is dead
                if not (saving_for_observer or saving_for_robo):
                    macro_plan.add(SpawnController(comp))
                macro_plan.add(
                    BuildWorkers(to_count=min(28, 22 * len(self.townhalls)))
                )
                macro_plan.add(
                    ProductionController(
                        comp,
                        base_location=prod_base,
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
                army_supply = self.supply_used - self.supply_workers
                # mineral income was the true constraint in the Hestia loss
                # (all minerals spent, army capped) - saturate up to 5 bases
                macro_plan.add(
                    BuildWorkers(to_count=min(80, 22 * len(self.townhalls)))
                )
                # Scheduled expansion reservation: when current bases are
                # saturated and home is safe, place ExpansionController AHEAD
                # of SpawnController so WarpGates don't pin minerals < 125
                # forever (Terranosaur 1-base 12.5m; Lissy/sharpy 2-base 15m).
                desired_bases = self._desired_bases(army_supply)
                need_expand = (
                    not self._all_in_read
                    and not self._home_threat()
                    and len(self.townhalls) < desired_bases
                    and not self.already_pending(UnitID.NEXUS)
                )
                if need_expand:
                    macro_plan.add(
                        ExpansionController(
                            to_count=desired_bases, max_pending=1
                        )
                    )
                if not (
                    saving_for_observer
                    or saving_for_robo
                    or (need_expand and self.minerals < 525)
                ):
                    macro_plan.add(SpawnController(comp))
                # upgrades only once we're stable: past the rush window AND
                # holding a real army (a 5:00 forge while defending was a
                # second death spiral in the Chance loss analysis); never
                # while a one-base all-in is inbound
                if (
                    self.time > UPGRADES_AFTER
                    and army_supply >= 16
                    and not self._all_in_read
                ):
                    upgrades = list(DESIRED_UPGRADES)
                    if self.mediator.get_own_army_dict[UnitID.COLOSSUS]:
                        upgrades.append(UpgradeId.EXTENDEDTHERMALLANCE)
                    macro_plan.add(
                        UpgradeController(
                            upgrade_list=upgrades,
                            base_location=prod_base,
                        )
                    )
                macro_plan.add(
                    ProductionController(comp, base_location=prod_base)
                )
                # Bank-driven production drain (Rule 3 & Rule 6): ares'
                # ProductionController caps gateways/robos by current gas rate,
                # which left 3.4k minerals / 1.1k gas unspent at 10:00 on 5
                # bases once gas throttling kicked in. Add Gateways/Robos
                # whenever we're floating so our bank turns into max supply.
                if self.minerals >= 600:
                    gates = (
                        self.structures(UnitID.GATEWAY).amount
                        + self.structures(UnitID.WARPGATE).amount
                    )
                    pending_gates = self.already_pending(UnitID.GATEWAY)
                    target_gates = min(14, max(4, 3 * len(self.townhalls)))
                    if gates + pending_gates < target_gates and pending_gates < 2:
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.GATEWAY,
                            )
                        )
                if (
                    self.minerals >= 500
                    and self.vespene >= 450
                    and (UnitID.IMMORTAL in comp or UnitID.COLOSSUS in comp)
                    and self.structures(UnitID.CYBERNETICSCORE).ready
                ):
                    robos = self.structures(UnitID.ROBOTICSFACILITY).amount
                    pending_robos = self.already_pending(UnitID.ROBOTICSFACILITY)
                    target_robos = min(3, max(1, len(self.townhalls) - 1))
                    if robos + pending_robos < target_robos and pending_robos == 0:
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.ROBOTICSFACILITY,
                            )
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
                if not self._all_in_read and not need_expand:
                    macro_plan.add(
                        ExpansionController(to_count=5, max_pending=1)
                    )
                # full gas geysers available; the dynamic gas throttle in
                # Mining (above) prevents over-mining when we're floating
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
                    # damaged stalker: blink toward safety if it's ready
                    # (jumps 8 range instantly out of the fight), else run.
                    # BLINKTECH is already in DESIRED_UPGRADES but was never
                    # actually fired before this.
                    if (
                        unit.type_id == UnitID.STALKER
                        and UpgradeId.BLINKTECH in self.state.upgrades
                        and self.time - self._blinked_at.get(unit.tag, -100.0)
                        > 11.0
                    ):
                        safe: Point2 = self.mediator.find_closest_safe_spot(
                            from_pos=unit.position, grid=grid
                        )
                        maneuver.add(
                            UseAbility(
                                AbilityId.EFFECT_BLINK_STALKER,
                                unit,
                                unit.position.towards(safe, 8.0),
                            )
                        )
                        self._blinked_at[unit.tag] = self.time
                    else:
                        maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                else:
                    maneuver.add(
                        StutterUnitBack(unit=unit, target=enemy_target, grid=grid)
                    )
            else:
                maneuver.add(PathUnitToTarget(unit=unit, grid=grid, target=target))
                maneuver.add(AMove(unit=unit, target=target))

            self.register_behavior(maneuver)
