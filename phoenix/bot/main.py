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
    StutterUnitForward,
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
    ID,
    LOSS_CLOSE_OR_WORSE,
    TARGET,
    TIE_OR_BETTER,
    TIME_ORDER_COMMENCED,
    WORKER_TYPES,
    UnitRole,
    UnitTreeQueryType,
)
from cython_extensions import cy_closest_to, cy_in_attack_range, cy_pick_enemy_target
from sc2.data import Race
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
LIGHT_TRIGGER: float = 7.0
# enemy FLYING combat army supply past this (and outweighing their ground)
# locks the comp to pure stalker - immortal/colossus can't shoot up (Arpy Void
# Rays, who Tempests, Mulebot BCs). Support flyers (Medivac/Raven/WarpPrism)
# are excluded so Terran Bio+Medivac or 2 harassing Banshees (6 supply) don't
# lock out Immortals/Colossi against Marines+Marauders+Tanks (MicroMachine).
AIR_TRIGGER: float = 8.0
SUPPORT_AIR_TYPES: set[UnitID] = {
    UnitID.MEDIVAC,
    UnitID.RAVEN,
    UnitID.WARPPRISM,
    UnitID.WARPPRISMPHASING,
    UnitID.OBSERVER,
    UnitID.OBSERVERSIEGEMODE,
    UnitID.OVERSEER,
    UnitID.OVERSEERSIEGEMODE,
    UnitID.OVERLORDTRANSPORT,
}
CAPITAL_AIR_TYPES: set[UnitID] = {
    UnitID.BATTLECRUISER,
    UnitID.CARRIER,
    UnitID.TEMPEST,
    UnitID.BROODLORD,
    UnitID.MOTHERSHIP,
}

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

SIEGE_BLINK_TARGETS: set[UnitID] = {
    UnitID.TEMPEST,
    UnitID.SIEGETANKSIEGED,
    UnitID.LIBERATORAG,
    UnitID.BROODLORD,
    UnitID.WARPPRISM,
}

ATTACK_AT_SUPPLY: float = 26.0
REGROUP_BELOW_SUPPLY: float = 10.0
DEFEND_RADIUS: float = 30.0


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
        self._nat_rescout_tag: Optional[int] = None
        self._nat_rescout_done: bool = False
        self._enemy_has_expanded: bool = False
        self._established_macro: bool = False
        self._obs_nat_check_active: bool = False
        self._last_obs_nat_check: float = -100.0
        self._last_threat_time: float = 0.0
        # per-stalker blink cooldown tracking (blink is ~11s; avoids an
        # async get_available_abilities call per unit each frame)
        self._blinked_at: dict[int, float] = {}

    async def on_start(self) -> None:
        await super(PhoenixBot, self).on_start()
        self.current_base_target = self.enemy_start_locations[0]
        # Sweep all expansions first, then a coarse pathable-map grid across
        # playable_area (corners & edges) so hidden proxy buildings (e.g.
        # who's corner ProxyDarkShrine) and floating Terran structures are
        # always found and finished off.
        sweep_points: list[Point2] = list(self.expansion_locations_list)
        area = self.game_info.playable_area
        for x in range(int(area.x) + 8, int(area.x + area.width) - 4, 24):
            for y in range(int(area.y) + 8, int(area.y + area.height) - 4, 24):
                pt = Point2((float(x), float(y)))
                if self.in_pathing_grid(pt) and all(
                    pt.distance_to(p) > 14.0 for p in sweep_points
                ):
                    sweep_points.append(pt)
        self.expansions_generator = cycle(sweep_points)

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
        rax_techlabs = self.enemy_structures(UnitID.BARRACKSTECHLAB).amount
        marauders = self.enemy_units(UnitID.MARAUDER).amount
        return (
            rax >= 3
            or (rax >= ONE_BASE_MIN_GATES and rax_techlabs >= 2)
            or (rax >= ONE_BASE_MIN_GATES and marauders >= 2)
        )

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
            if len(ready_th) == 1:
                return self.start_location
            enemy_ground_in_main = self.enemy_units.filter(
                lambda u: u.type_id not in WORKER_TYPES
                and u.type_id not in COMMON_UNIT_IGNORE_TYPES
                and not u.is_flying
                and not u.is_memory
                and u.distance_to(self.start_location) < 18.0
            )
            main_pylons = self.structures(UnitID.PYLON).ready.closer_than(
                22.0, self.start_location
            )
            main_has_space = (
                self.structures.closer_than(22.0, self.start_location).amount
                < 14
                or self.mediator.request_building_placement(
                    base_location=self.start_location,
                    structure_type=UnitID.GATEWAY,
                    within_psionic_matrix=True,
                    reserve_placement=False,
                    production=True,
                )
                is not None
                or self.mediator.request_building_placement(
                    base_location=self.start_location,
                    structure_type=UnitID.PYLON,
                    within_psionic_matrix=False,
                    reserve_placement=False,
                    production=True,
                )
                is not None
            )
            if (
                self.get_total_supply(enemy_ground_in_main) < 10.0
                and bool(main_pylons)
                and main_has_space
            ):
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
        if self._enemy_has_expanded or self.mediator.get_enemy_expanded:
            return False
        # Already established on 2+ bases in mid-game macro (34+ probes past
        # 06:30, or 3+ bases with 40+ probes), OR already won a 1-base hold and
        # expanded onto 2+ bases: dropping back into 1-base emergency lockdown
        # stops probes, upgrades, and robo tech (MicroMachine 08:01, who 10:02).
        if (
            (len(self.townhalls) >= 3 and self.supply_workers >= 40)
            or (self._established_macro and self.time >= 240.0)
            or (
                len(self.townhalls.ready) >= 2
                and self.supply_workers >= 30
                and self.time >= 240.0
            )
            or (self._posthold_logged and len(self.townhalls) >= 2)
        ):
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
                if (
                    u.type_id in WORKER_TYPES
                    or u.is_flying
                    or u.is_hallucination
                ):
                    continue
                if u.type_id in (UnitID.LOCUSTMP, UnitID.LOCUSTMPFLYING):
                    light += 0.5
                    continue
                sup = self.calculate_supply_cost(u.type_id)
                if u.type_id in (
                    UnitID.SWARMHOSTMP,
                    UnitID.SWARMHOSTBURROWEDMP,
                ):
                    light += sup
                if u.is_armored:
                    armored += sup
                elif u.is_light:
                    light += sup
        return armored, light

    def _enemy_air_supply(self) -> float:
        """Scouted enemy FLYING combat army supply (excludes overlords and
        non-combat support flyers like Medivacs, Ravens, and Warp Prisms)."""
        air = 0.0
        for units in self.mediator.get_enemy_army_dict.values():
            for u in units:
                if (
                    u.is_flying
                    and u.type_id not in WORKER_TYPES
                    and u.type_id not in SUPPORT_AIR_TYPES
                    and not u.is_hallucination
                ):
                    air += self.calculate_supply_cost(u.type_id)
        return air

    def _won_the_hold(self) -> bool:
        """The all-in is weathered and we're clearly ahead - convert the won
        defense into ECONOMY. The 08-18 OneBaseStalkerBot ladder loss: Phoenix
        held, led 2450v1050 at 10:00, yet sat on ONE base for 19 minutes, mined
        out and collapsed 0v3500. Reproduced in sparring (17.5-min grind, Nexus
        x1 the whole game). Ahead = past the all-in's peak window, holding a
        real army, and at least 1.5x the scouted enemy army supply."""
        if self.time < 390.0:
            return False
        own = self.supply_used - self.supply_workers
        enemy = 0.0
        for units in self.mediator.get_enemy_army_dict.values():
            for u in units:
                if u.type_id not in WORKER_TYPES and not u.is_hallucination:
                    enemy += self.calculate_supply_cost(u.type_id)
        if self.time < 420.0:
            return (
                own >= 24.0
                and own >= 2.0 * max(enemy, 1.0)
                and not self._home_threat()
            )
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
        # the enemy's air outweighs (or rivals at >=9 supply, e.g. 3+ Banshees)
        # their ground army, stay on pure stalkers.
        air = self._enemy_air_supply()
        capital_air = sum(
            self.calculate_supply_cost(u.type_id)
            for units in self.mediator.get_enemy_army_dict.values()
            for u in units
            if u.type_id in CAPITAL_AIR_TYPES and not u.is_hallucination
        )
        own_aa_supply = 2.0 * (
            self.units(UnitID.STALKER).amount
            + self.already_pending(UnitID.STALKER)
        )
        if (
            (air >= AIR_TRIGGER and air > max(armored, light))
            or (air >= 9.0 and air >= 0.75 * max(armored, light))
            or (air >= 16.0 and air >= 0.5 * (armored + light))
            or (air >= 6.0 and own_aa_supply < 1.5 * air)
            or (capital_air >= 6.0 and own_aa_supply < 3.0 * capital_air)
        ):
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
        # no clear read yet: drain floating gas mid-game once established on
        # 2+ bases (36+ probes), else keep pumping Stalkers to punish post-hold
        if (
            self.time > LATE_COMP_AFTER
            and len(self.townhalls) >= 2
            and self.supply_workers >= 36
            and self.vespene > 400
        ):
            return LATE_COMP
        return ARMY_COMP

    def _counter_proxy_structures(self) -> None:
        """Cannon-rush / proxy-bunker response: pull nearby probes onto lethal
        or production proxy structures while they're building (cannons finished
        = too late). Ignore non-lethal Terran Supply Depots / Engineering Bays
        (Mulebot pulled 8 probes onto a SupplyDepot, crashing income to 307/m)."""
        lethal_proxies = {
            UnitID.PHOTONCANNON,
            UnitID.PYLON,
            UnitID.BUNKER,
            UnitID.SPINECRAWLER,
            UnitID.SPORECRAWLER,
            UnitID.HATCHERY,
            UnitID.GATEWAY,
            UnitID.BARRACKS,
        }
        proxies = [
            s
            for s in self.enemy_structures
            if s.type_id in lethal_proxies
            and any(s.distance_to(th) < 30.0 for th in self.townhalls)
        ]
        if not proxies or self.time > 420.0:
            return
        # prioritise unfinished cannons/bunkers, then pylons/production
        proxies.sort(
            key=lambda s: (
                s.build_progress >= 1.0,
                s.type_id not in (UnitID.PHOTONCANNON, UnitID.BUNKER),
            )
        )
        target = proxies[0]
        max_pull = (
            8
            if (
                target.type_id in (UnitID.PHOTONCANNON, UnitID.BUNKER)
                or target.distance_to(self.start_location) < 22.0
            )
            else 4
        )
        pullers = self.workers.sorted_by_distance_to(target)[:max_pull]
        for probe in pullers:
            if not probe.orders or probe.orders[0].ability.id not in (
                AbilityId.ATTACK,
                AbilityId.ATTACK_ATTACK,
            ):
                probe.attack(target)

    def _midgame_nat_rescout(self) -> None:
        """Send one quick probe to check the enemy natural around 3:10 if our
        1:45 probe missed a ~2:00 expansion (Rule 5: Scout constantly).
        Eliminates false EMERGENCY: one-base all-in alarms at 6:00-7:30 vs
        2-base macro opponents (seen in macroprotoss and macroterran)."""
        is_terran = self.enemy_race == Race.Terran
        start_t, end_t, abort_t = (
            (255.0, 310.0, 350.0) if is_terran else (190.0, 260.0, 300.0)
        )
        enemy_nat: Point2 = self.mediator.get_enemy_nat
        if self._nat_rescout_tag is not None:
            scout = self.workers.find_by_tag(self._nat_rescout_tag)
            if (
                scout is None
                or self.mediator.get_enemy_expanded
                or scout.distance_to(enemy_nat) < 8.0
                or self.time > abort_t
            ):
                if scout is not None:
                    self.mediator.assign_role(
                        tag=scout.tag, role=UnitRole.GATHERING
                    )
                self._nat_rescout_tag = None
                self._nat_rescout_done = True
                return
            scout.move(enemy_nat)
            return

        if (
            self._nat_rescout_done
            or self._enemy_has_expanded
            or self.mediator.get_enemy_expanded
            or not (start_t <= self.time <= end_t)
            or self.workers.amount < 20
            or bool(self._home_threat())
        ):
            return
        if scout := self.mediator.select_worker(target_position=enemy_nat):
            self.mediator.assign_role(tag=scout.tag, role=UnitRole.SCOUTING)
            self._nat_rescout_tag = scout.tag
            scout.move(enemy_nat)

    def _evacuate_harassed_probes(self) -> None:
        """Pull gathering probes away from lethal air/cloaked/burrowed raiders
        in our mineral lines and return them to GATHERING as soon as safe
        (Rule 9b). Temporarily assigns evacuated probes to CONTROL_GROUP_NINE
        so ares's Mining behavior in _after_step doesn't immediately overwrite
        probe.move() and send them right back into Banshee/Oracle/Mine fire."""
        if not self.townhalls or not self.workers:
            return
        raiders = self.enemy_units.filter(
            lambda u: not u.is_memory
            and not u.is_hallucination
            and u.type_id not in WORKER_TYPES
            and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and u.type_id not in SUPPORT_AIR_TYPES
            and (
                u.is_flying
                or u.is_cloaked
                or u.type_id
                in (
                    UnitID.DARKTEMPLAR,
                    UnitID.WIDOWMINEBURROWED,
                    UnitID.LURKERMPBURROWED,
                    UnitID.BANELING,
                )
            )
            and (
                u.can_attack_ground
                or u.type_id
                in (
                    UnitID.ORACLE,
                    UnitID.WIDOWMINE,
                    UnitID.WIDOWMINEBURROWED,
                    UnitID.BANSHEE,
                )
            )
            and any(u.distance_to(th) < 11.0 for th in self.townhalls)
        )
        safe_ths = [
            th
            for th in self.townhalls.ready
            if not raiders or raiders.closest_distance_to(th) > 16.0
        ]
        evacuated = self.mediator.get_units_from_role(
            role=UnitRole.CONTROL_GROUP_NINE, unit_type=self.worker_type
        )
        for probe in evacuated:
            if not raiders or raiders.closest_distance_to(probe) > 10.5:
                self.mediator.assign_role(
                    tag=probe.tag, role=UnitRole.GATHERING
                )
            else:
                nearest_r = raiders.closest_to(probe)
                dest = (
                    min(safe_ths, key=lambda th: th.distance_to(probe)).position
                    if safe_ths
                    else probe.position.towards(nearest_r.position, -8.0)
                )
                probe.move(dest)

        if not raiders:
            return
        gathering = self.mediator.get_units_from_role(
            role=UnitRole.GATHERING, unit_type=self.worker_type
        )
        if not gathering:
            return
        evacuated_tags: set[int] = set()
        for raider in raiders:
            high_burst = raider.is_cloaked or raider.type_id in (
                UnitID.BANSHEE,
                UnitID.ORACLE,
                UnitID.DARKTEMPLAR,
                UnitID.WIDOWMINEBURROWED,
                UnitID.LURKERMPBURROWED,
                UnitID.BANELING,
            )
            danger_radius = 7.5 if high_burst else 6.0
            for probe in gathering.closer_than(danger_radius, raider):
                if probe.tag in evacuated_tags:
                    continue
                if not high_burst and probe.shield_percentage >= 0.75:
                    continue
                evacuated_tags.add(probe.tag)
                self.mediator.remove_worker_from_mineral(worker_tag=probe.tag)
                self.mediator.assign_role(
                    tag=probe.tag, role=UnitRole.CONTROL_GROUP_NINE
                )
                dest = (
                    min(safe_ths, key=lambda th: th.distance_to(probe)).position
                    if safe_ths
                    else probe.position.towards(raider.position, -8.0)
                )
                probe.move(dest)

    async def on_step(self, iteration: int) -> None:
        await super(PhoenixBot, self).on_step(iteration)

        if self.mediator.get_enemy_expanded:
            self._enemy_has_expanded = True
        if len(self.townhalls.ready) >= 2 and self.supply_workers >= 26:
            self._established_macro = True
        self._maybe_switch_to_defense()
        self._update_detection()
        self._midgame_nat_rescout()
        self._all_in_read: bool = self._enemy_all_in
        # a chosen defensive opening commits us to the anti-all-in posture
        # while the opponent is actually on one base. Release immediately if
        # we scout an enemy expansion (Slenderina / Thssprtssbt took 2-4 bases
        # while Phoenix sat locked in OneBaseDefense until 7:30).
        self._defense_opening = (
            self.build_order_runner.chosen_opening == "OneBaseDefense"
            and self.time < 450.0
            and not self._enemy_has_expanded
        )
        if self._defense_opening:
            self._all_in_read = True
        self._update_emergency()
        self._counter_proxy_structures()
        self._evacuate_harassed_probes()
        self._macro()
        await self._fallback_build_robo()

        forces: Units = self.mediator.get_units_from_role(role=UnitRole.ATTACKING)
        forces_supply: float = self.get_total_supply(forces)
        self._micro_observers(forces)

        if threat := self._home_threat():
            # Split defense vs minor harass: never recall a 60-supply attacking
            # army from the enemy's doorstep because 1 Tempest, Warp Prism,
            # Banshee, or DT poked our outer base (who_protoss 07:48-10:54
            # pulled all 31 Stalkers back 6 times despite a 29.00 trade ratio).
            local_home = self.enemy_units.filter(
                lambda u: u.type_id not in COMMON_UNIT_IGNORE_TYPES
                and u.type_id not in WORKER_TYPES
                and not u.is_memory
                and not u.is_hallucination
                and (
                    any(
                        u.distance_to(th) < DEFEND_RADIUS + 6.0
                        for th in self.townhalls
                    )
                    or any(
                        u.distance_to(s) < 14.0 for s in self.structures.ready
                    )
                )
            )
            local_home_supply = self.get_total_supply(local_home)
            if (
                self._commenced_attack
                and not self._emergency
                and forces_supply >= 38.0
                and local_home_supply <= max(8.0, 0.22 * forces_supply)
            ):
                need_aa = any(u.is_flying for u in local_home)
                candidates = sorted(
                    forces,
                    key=lambda u: (
                        0 if (not need_aa or u.can_attack_air) else 1,
                        u.distance_to(threat),
                    ),
                )
                def_need = max(8.0, 2.0 * local_home_supply)
                def_tags: set[int] = set()
                def_supply = 0.0
                for u in candidates:
                    u_sup = self.calculate_supply_cost(u.type_id)
                    if (
                        def_supply < def_need
                        and forces_supply - (def_supply + u_sup) >= 24.0
                    ):
                        def_tags.add(u.tag)
                        def_supply += u_sup
                defenders = forces.filter(lambda u: u.tag in def_tags)
                attackers = forces.filter(lambda u: u.tag not in def_tags)
                if defenders:
                    self._micro(defenders, target=threat.position)
                forces = attackers
                forces_supply = self.get_total_supply(forces)
            else:
                # Full defense: never stand underneath unrevealed Cloaked
                # Banshees / DTs / Lurkers fighting visible escorts while our
                # Observer is still flying in from the Robo (MicroMachine
                # 09:42 lost 6 Stalkers + 1 Immortal while Observer was 35
                # tiles behind at (69, 161)). Pull back to merge with our
                # Observer first, then step in together with detection.
                target: Point2 = threat.position
                hold_pos: Optional[Point2] = None
                unrev_home = [
                    u
                    for u in local_home
                    if (u.is_cloaked or u.is_burrowed)
                    and not u.is_revealed
                    and u.type_id
                    not in (UnitID.WIDOWMINE, UnitID.WIDOWMINEBURROWED)
                ]
                observers = self.units(UnitID.OBSERVER)
                obs_incoming = bool(observers) or bool(
                    self.already_pending(UnitID.OBSERVER)
                )
                if (
                    unrev_home
                    and obs_incoming
                    and not any(
                        any(obs.distance_to(u) < 12.5 for obs in observers)
                        for u in unrev_home
                    )
                ):
                    if observers:
                        merge_pt = observers.closest_to(threat).position
                    else:
                        safe_ths = [
                            th
                            for th in self.townhalls.ready
                            if all(th.distance_to(u) > 14.0 for u in unrev_home)
                        ]
                        if safe_ths:
                            merge_pt = safe_ths[0].position
                        else:
                            merge_pt = self.mediator.find_closest_safe_spot(
                                from_pos=self.main_base_ramp.top_center,
                                grid=self.mediator.get_ground_grid,
                            )
                    target = merge_pt
                    hold_pos = merge_pt
                else:
                    # Defender's advantage (Rule 7 & 9a): when outnumbered or
                    # roughly even, hold at our ramp / Shield Battery anchor
                    # instead of sallying 25-30 tiles into open field, UNLESS
                    # enemy siege units are already shelling our structures.
                    local_enemy = self.enemy_units.filter(
                        lambda u: u.type_id not in COMMON_UNIT_IGNORE_TYPES
                        and u.type_id not in WORKER_TYPES
                        and not u.is_memory
                        and not u.is_hallucination
                        and any(
                            u.distance_to(th) < 35.0 for th in self.townhalls
                        )
                    )
                    local_enemy_supply = self.get_total_supply(local_enemy)
                    shelling_structures = any(
                        any(u.distance_to(s) < 14.5 for s in self.structures)
                        for u in local_enemy
                    )
                    ratio_gate = 1.5 if self._emergency else 1.35
                    if (
                        not shelling_structures
                        and forces_supply
                        < ratio_gate * max(local_enemy_supply, 4.0)
                    ):
                        ready_th = self.townhalls.ready
                        if (
                            self._emergency
                            and len(ready_th) <= 1
                            and threat.distance_to(self.start_location) > 18.0
                        ):
                            target = self.main_base_ramp.top_center
                            hold_pos = self.main_base_ramp.top_center
                        elif (
                            ready_th
                            and ready_th.closest_distance_to(threat) > 11.5
                        ):
                            closest_th = ready_th.closest_to(threat)
                            anchor = closest_th.position.towards(
                                threat.position, 5.0
                            )
                            target = anchor
                            hold_pos = anchor
                self._micro(forces, target=target, hold_pos=hold_pos)
                return

        # engagement gating: simulate the fight against visible + remembered
        # enemy combat units (ares UnitMemoryManager 30s cache) so 2 Marines
        # poking in front of fogged Siege Tanks / Banshees don't bait a 20-
        # supply army into a 31-supply ambush (MicroMachine 11:00).
        enemy_army: Units = self.enemy_units.filter(
            lambda u: u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and u.type_id not in WORKER_TYPES
            and not u.is_memory
            and not u.is_hallucination
        )
        sim_enemy_army: Units = self.mediator.get_all_enemy.filter(
            lambda u: u.type_id not in ALL_STRUCTURES
            and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and u.type_id not in WORKER_TYPES
            and not u.is_hallucination
        )
        fight = None
        if forces and sim_enemy_army:
            fight = self.mediator.can_win_fight(
                own_units=forces,
                enemy_units=sim_enemy_army,
                workers_do_no_damage=True,
            )

        # Anti-Armor Missile (-3 armor for 15s): never stand and trade into
        # Stimmed Bio / Auto-Turrets while orange-debuffed (VeTerran 09:00
        # lost 10 of 14 Stalkers). Pull back with fighting retreat until clear.
        shredded_cnt = sum(
            1
            for u in forces
            if u.has_buff(BuffId.RAVENSHREDDERMISSILEARMORREDUCTION)
        )
        army_shredded = bool(forces) and shredded_cnt >= max(
            4, int(0.35 * len(forces))
        )

        # Blind-push protection (MicroMachine 09:30-10:00 lost 3 Stalkers + 1
        # Immortal to 3 Cloaked Banshees for 0 damage while Observer lagged):
        # never push deeper while unrevealed cloaked/burrowed combat units are
        # actively hitting our spearhead with 0 Observers in detection range.
        blind_to_cloak = False
        if forces and enemy_army:
            unrevealed_dps = [
                u
                for u in enemy_army
                if (u.is_cloaked or u.is_burrowed)
                and not u.is_revealed
                and u.type_id
                not in (UnitID.WIDOWMINE, UnitID.WIDOWMINEBURROWED)
                and forces.closest_distance_to(u) < 10.0
            ]
            if unrevealed_dps:
                observers = self.units(UnitID.OBSERVER)
                blind_to_cloak = not any(
                    any(obs.distance_to(u) < 14.0 for obs in observers)
                    for u in unrevealed_dps
                )

        if self._commenced_attack:
            if (
                forces_supply < self._regroup_below_supply
                or (fight is not None and fight in LOSS_CLOSE_OR_WORSE)
                or (army_shredded and bool(enemy_army))
                or (blind_to_cloak and forces_supply < self._pressure_valve_supply)
            ):
                self._commenced_attack = False
        elif (
            not army_shredded
            and not blind_to_cloak
            and (
                forces_supply >= self._attack_at_supply
                or (
                    forces_supply >= 18.0
                    and not self._enemy_has_expanded
                    and self._won_the_hold()
                )
            )
            and (
                fight is None
                or fight in TIE_OR_BETTER
                # pressure valve: near max supply nothing is gained by waiting -
                # attack even into a predicted loss rather than starve at home
                or forces_supply >= self._pressure_valve_supply
            )
        ):
            # vs a one-base all-in, hold home-field advantage (wall +
            # batteries) until we've actually won the hold, then punish
            if not self._all_in_read or self._won_the_hold():
                self._commenced_attack = True

        if self._commenced_attack:
            self._micro(forces, target=self.attack_target)
        else:
            # Stage the army at our front-most ready expansion (when on 2+
            # bases outside emergency) so we guard expansions and attack
            # sooner instead of retreating all the way to the main ramp.
            ready_th = self.townhalls.ready
            if len(ready_th) >= 2 and not self._emergency:
                front_th = min(
                    ready_th,
                    key=lambda th: th.distance_to(self.game_info.map_center),
                )
                rally: Point2 = front_th.position.towards(
                    self.game_info.map_center, 6.0
                )
            else:
                rally = self.main_base_ramp.top_center.towards(
                    self.game_info.map_center, 4.0
                )
            grid: np.ndarray = self.mediator.get_ground_grid
            attackable_enemy: Units = enemy_army.filter(
                lambda u: not (u.is_cloaked or u.is_burrowed) or u.is_revealed
            )
            robo_forces = forces.of_type({UnitID.IMMORTAL, UnitID.COLOSSUS})
            rear_robo: Optional[Unit] = (
                max(robo_forces, key=lambda r: r.distance_to(rally))
                if robo_forces
                else None
            )
            if rear_robo is not None and rear_robo.distance_to(rally) <= 14.0:
                rear_robo = None
            for unit in forces:
                maneuver: CombatManeuver = CombatManeuver()
                has_action = False
                # Fighting retreat: shoot pursuing enemies (e.g. fast Cyclones
                # or Zerglings) whenever our weapon is off cooldown instead of
                # blind move-commanding 60 tiles home while dying for 0 damage.
                if attackable_enemy and (
                    in_range := cy_in_attack_range(unit, attackable_enemy)
                ):
                    maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_range)
                    )
                    has_action = True
                dest_rally = rally
                if (
                    rear_robo is not None
                    and unit.type_id in (UnitID.STALKER, UnitID.ZEALOT)
                    and unit.distance_to(rally) + 6.0
                    < rear_robo.distance_to(rally)
                    and unit.distance_to(rear_robo) < 18.0
                ):
                    dest_rally = rear_robo.position.towards(rally, 4.0)
                if unit.distance_to(dest_rally) > 8.0:
                    maneuver.add(
                        PathUnitToTarget(
                            unit=unit, grid=grid, target=dest_rally
                        )
                    )
                    maneuver.add(AMove(unit=unit, target=dest_rally))
                    has_action = True
                if has_action:
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
            # Prefer structures near our bases (active proxy threat) or enemy
            # townhalls (real economy) over orphaned corner proxy structures
            # (MicroMachine's (150,149) proxy Factory pulled half our army 70
            # tiles away from its 3 bases at (149,74)).
            near_home = self.enemy_structures.filter(
                lambda s: any(
                    s.distance_to(th) < 40.0 for th in self.townhalls
                )
            )
            if near_home:
                return cy_closest_to(self.start_location, near_home).position
            enemy_ths = self.enemy_structures.of_type(
                {
                    UnitID.COMMANDCENTER,
                    UnitID.ORBITALCOMMAND,
                    UnitID.PLANETARYFORTRESS,
                    UnitID.NEXUS,
                    UnitID.HATCHERY,
                    UnitID.LAIR,
                    UnitID.HIVE,
                }
            )
            if enemy_ths:
                return cy_closest_to(self.start_location, enemy_ths).position
            return cy_closest_to(
                self.enemy_start_locations[0], self.enemy_structures
            ).position
        elif self.time < 240.0:
            return self.enemy_start_locations[0]
        else:
            # nothing visible: sweep expansion locations
            if self.is_visible(self.current_base_target):
                self.current_base_target = next(self.expansions_generator)
            return self.current_base_target

    def _home_threat(self) -> Optional[Unit]:
        """Closest enemy combat unit near any of our townhalls or shelling
        our outer structures (range-14 Tempests / Siege Tanks)."""
        threats: list[Unit] = [
            u
            for u in self.enemy_units
            if u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and not u.is_memory
            and not u.is_hallucination
            and (
                any(u.distance_to(th) < DEFEND_RADIUS for th in self.townhalls)
                or (
                    u.type_id not in WORKER_TYPES
                    and any(
                        u.distance_to(s) < 14.0 for s in self.structures.ready
                    )
                )
            )
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

    def _intel_rush(self) -> bool:
        """Race-aware early rush detection without ares's permanently latched
        `time < 120 and barracks >= 2` clause, which false-triggered at 01:19
        against 2-Rax macro Terrans (VeTerran-revived) and locked PhoenixBot on
        1 base / 22 probes for 5+ minutes."""
        m = self.mediator
        if (
            m.get_enemy_ling_rushed
            or m.get_enemy_worker_rushed
            or m.get_is_proxy_zealot
            or m.get_enemy_ravager_rush
            or m.get_enemy_roach_rushed
            or m.get_enemy_four_gate
            or (
                m.get_enemy_went_marine_rush
                and not self.get_enemy_proxies(15.0, m.get_own_nat)
            )
            or (
                self.time < 240.0
                and len(m.get_enemy_army_dict[UnitID.ROACH]) >= 3
            )
            or (
                self.time < 105.0
                and len(m.get_enemy_army_dict[UnitID.ZERGLING]) >= 1
            )
        ):
            return True
        if self._enemy_has_expanded or m.get_enemy_expanded:
            return False
        if m.get_enemy_marauder_rush:
            return True
        rax = self.enemy_structures.filter(
            lambda s: s.type_id in (UnitID.BARRACKS, UnitID.BARRACKSFLYING)
        ).amount
        rax_tl = self.enemy_structures(UnitID.BARRACKSTECHLAB).amount
        return (self.time < 120.0 and rax >= 3) or (
            self.time < 150.0 and rax >= 2 and rax_tl >= 2
        )

    def _update_emergency(self) -> None:
        """Rush defense mode: abort the opening, stop spending on greed."""
        intel_rush: bool = self._intel_rush()
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
            and army_supply >= 20.0
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

    def _train_observers(self, urgent_only: bool = False) -> bool:
        """Train Observers from ready idle Robotics Facilities.

        With urgent_only=True, only ensures our first Observer (obs_total == 0)
        so replacing a 2nd Observer doesn't starve Colossi/Immortals from a
        single Robotics Facility. Returns True when urgently saving for
        Observer #1 so SpawnController doesn't steal its 75 gas.
        """
        robos = self.structures(UnitID.ROBOTICSFACILITY).ready
        if not robos:
            return False
        army_supply = self.supply_used - self.supply_workers
        if self._need_detection:
            want_obs = 3 if (len(robos) >= 2 and army_supply >= 28.0) else 2
        else:
            want_obs = 1 if (self.time >= 300.0 or self._emergency) else 0
        if urgent_only:
            want_obs = min(want_obs, 2 if self._need_detection else 1)
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

    def _train_robo_units(self, comp: dict[UnitID, dict]) -> bool:
        """Train Colossi / Immortals directly from idle Robotics Facilities
        ahead of SpawnController so continuous 125m Stalker warp-ins never
        pin minerals below 275-300 (fixes 0-Colossus losses vs 43-Marine Bio
        in BioBot2.0 / Terranosaur / Mulebot, and avoids ares SpawnController's
        can_afford-before-proportion blocking quirk).

        Returns True only when a ready idle Robo genuinely needs a Colossus or
        Immortal (below target proportion, gas available) so SpawnController
        pauses briefly (~3-5s) to fund it.
        """
        idle_robos = self.structures(UnitID.ROBOTICSFACILITY).ready.idle
        if not idle_robos:
            return False

        stalkers = self.units(UnitID.STALKER).amount + self.already_pending(
            UnitID.STALKER
        )
        immortals = self.units(UnitID.IMMORTAL).amount + self.already_pending(
            UnitID.IMMORTAL
        )
        want_colossus = UnitID.COLOSSUS in comp
        want_immortal = UnitID.IMMORTAL in comp
        if not (want_colossus or want_immortal):
            # When locked to ARMY_COMP by enemy air (e.g. Cloaked Banshees),
            # never pause Stalkers or build extra Robos, but don't leave our
            # detection Robo sitting idle if enemy ground also has Siege Tanks
            # / Cyclones / Marauders and we already have >=8 Stalkers.
            if (
                stalkers >= 8
                and immortals < 2
                and self._enemy_armored_light_supply()[0] >= 6.0
                and self.can_afford(UnitID.IMMORTAL)
                and self.supply_left >= 4
            ):
                idle_robos.first.train(UnitID.IMMORTAL)
            return False

        colossi = self.units(UnitID.COLOSSUS).amount + self.already_pending(
            UnitID.COLOSSUS
        )
        total = max(1, stalkers + immortals + colossi)

        target_unit: Optional[UnitID] = None
        if (
            want_colossus
            and self.structures(UnitID.ROBOTICSBAY).ready
            and colossi < 6
            and colossi / total < comp[UnitID.COLOSSUS]["proportion"]
        ):
            target_unit = UnitID.COLOSSUS
        elif (
            want_immortal
            and immortals < 8
            and immortals / total < comp[UnitID.IMMORTAL]["proportion"]
        ):
            target_unit = UnitID.IMMORTAL

        if target_unit is None:
            return False

        supply_need = self.calculate_supply_cost(target_unit)
        if self.can_afford(target_unit) and self.supply_left >= supply_need:
            idle_robos.first.train(target_unit)
            return False

        # Only pause Stalker warp-ins if we already have a real Stalker screen
        # and enough gas on hand so we don't starve Stalkers down to 2-3 units.
        army_supply = self.supply_used - self.supply_workers
        min_gas = 120 if target_unit == UnitID.COLOSSUS else 50
        return (
            army_supply >= 14.0
            and stalkers >= 6
            and self.vespene >= min_gas
            and self.supply_left >= supply_need
        )

    def _micro_observers(self, forces: Units) -> None:
        """Keep Observers covering cloaked/burrowed threats, periodically
        checking the enemy natural while still on a 1-base read, or escorting
        the main army just behind the front line so they aren't sniped."""
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
        enemy_nat: Point2 = self.mediator.get_enemy_nat
        if (
            self._enemy_has_expanded
            or home_hidden
            or (self._need_detection and len(observers) < 2)
            or self._home_threat()
        ):
            self._obs_nat_check_active = False
        elif (
            not self._obs_nat_check_active
            and (not self._need_detection or len(observers) >= 2)
            and self.time >= 270.0
            and self.time - self._last_obs_nat_check >= 75.0
        ):
            self._obs_nat_check_active = True
            self._last_obs_nat_check = self.time

        # Anchor escort Observer to the attacking spearhead (closest unit to
        # attack_target) rather than forces.center -- freshly warped
        # reinforcements at home otherwise pull forces.center to the middle of
        # the map, leaving our front line blind to DTs/Lurkers/Mines.
        if forces and self._commenced_attack:
            army_center: Point2 = cy_closest_to(
                self.attack_target, forces
            ).position
        elif forces:
            army_center = forces.center
        else:
            army_center = self.main_base_ramp.top_center
        # Assign the closest Observer to home_hidden so our home-guard
        # Observer handles base DTs instead of recalling the army escort
        # Observer across the map (leaving attacking Stalkers blind).
        home_obs_tag: Optional[int] = (
            observers.closest_to(home_hidden.center).tag if home_hidden else None
        )
        army_hidden = hidden.filter(
            lambda u: u.distance_to(army_center) < 25.0
        )
        aa_threats = self.enemy_units.filter(
            lambda u: not u.is_memory
            and not u.is_hallucination
            and (
                u.can_attack_air
                or u.type_id
                in (UnitID.WIDOWMINE, UnitID.WIDOWMINEBURROWED, UnitID.AUTOTURRET)
            )
        )
        aa_structures = self.enemy_structures.filter(
            lambda s: s.can_attack_air and s.is_ready
        )
        widow_mines = self.enemy_units.filter(
            lambda u: not u.is_memory
            and u.type_id in (UnitID.WIDOWMINE, UnitID.WIDOWMINEBURROWED)
        )
        air_grid: np.ndarray = self.mediator.get_air_grid
        for idx, obs in enumerate(observers):
            # Cloak-aware Observer survival: an Observer is cloaked, so
            # Marines/Cyclones cannot see or shoot it unless obs.is_revealed
            # (Scan/Raven/Turret/Overseer/Observer). Hovering 9.2 tiles from
            # hidden threats toward start_location keeps them inside Observer
            # 11.0 detection radius while staying behind our Stalkers and
            # outside Marine (5.0), Mine (5.0), Turret (6.0), Cyclone (7.0).
            mine_danger = any(obs.distance_to(m) < 6.2 for m in widow_mines)
            turret_danger = any(
                obs.distance_to(s) < max(s.air_range, 7.0) + 1.5
                for s in aa_structures
            )
            revealed_aa_danger = obs.is_revealed and any(
                obs.distance_to(u)
                < max(
                    u.air_range,
                    7.0 if u.type_id == UnitID.CYCLONE else 5.0,
                )
                + 1.2
                for u in aa_threats
            )
            if (
                mine_danger
                or turret_danger
                or revealed_aa_danger
                or obs.shield_percentage < 0.35
            ):
                safe = self.mediator.find_closest_safe_spot(
                    from_pos=obs.position, grid=air_grid
                )
                obs.move(safe)
                continue
            if home_hidden and (obs.tag == home_obs_tag or len(observers) == 1):
                t = home_hidden.closest_to(obs)
                near_turret = any(
                    t.distance_to(s) < 11.0 for s in aa_structures
                )
                hover = 8.5 if (obs.is_revealed or near_turret) else 2.5
                dest = t.position.towards(self.start_location, hover)
            elif army_hidden and (
                obs.tag != home_obs_tag or len(observers) == 1
            ):
                t = army_hidden.closest_to(army_center)
                near_turret = any(
                    t.distance_to(s) < 11.0 for s in aa_structures
                )
                hover = 8.5 if (obs.is_revealed or near_turret) else 2.5
                dest = t.position.towards(self.start_location, hover)
            elif (
                home_hidden
                and len(observers) >= 2
                and obs.tag != home_obs_tag
                and any(
                    u.distance_to(home_hidden.closest_to(observers.closest_to(home_hidden.center)))
                    > 11.0
                    for u in home_hidden
                )
            ):
                # Cover a second cloaked raider splitting between main & natural
                t = max(
                    home_hidden,
                    key=lambda u: u.distance_to(
                        observers.find_by_tag(home_obs_tag).position
                    )
                    if observers.find_by_tag(home_obs_tag) is not None
                    else 0.0,
                )
                near_turret = any(
                    t.distance_to(s) < 11.0 for s in aa_structures
                )
                hover = 8.5 if (obs.is_revealed or near_turret) else 2.5
                dest = t.position.towards(self.start_location, hover)
            elif (
                self._obs_nat_check_active
                and (not self._need_detection or len(observers) >= 2)
                and idx == len(observers) - 1
            ):
                dest = enemy_nat
                if obs.distance_to(enemy_nat) < 9.0:
                    self._obs_nat_check_active = False
            elif (
                (idx == 0 or (home_obs_tag is not None and obs.tag != home_obs_tag))
                and forces
            ):
                dest = army_center.towards(self.start_location, 3.5)
            elif self.townhalls:
                # second observer guards our most exposed expansion
                exposed = max(
                    self.townhalls,
                    key=lambda th: th.distance_to(self.start_location),
                )
                dest = exposed.position
            else:
                dest = army_center
            if obs.distance_to(dest) > 2.0:
                obs.move(dest)

    def _repair_unpowered_building_targets(self, prod_base: Point2) -> None:
        """Protect in-transit BuildingManager orders from two ares pitfalls:
        1. Unpowered fallback tiles (within_psionic_matrix=False on retry),
           which stranded Forge & Twilight builders for 120s in who_protoss.
        2. Shelled outer-expansion tiles: when a builder Probe dies en route to
           a natural/3rd site under Siege Tank / Banshee / army fire, ares
           re-selects the next closest Probe every 2s in a conga line of death
           (14 Probes lost 05:29-05:51 in MicroMachine). Relocate tech/prod
           orders to prod_base or cancel the unsafe outer dispatch."""
        ready_pylons = self.structures(UnitID.PYLON).ready
        tracker = self.mediator.get_building_tracker_dict
        if not tracker:
            return
        enemy_shooters = self.enemy_units.filter(
            lambda u: not u.is_memory
            and not u.is_hallucination
            and u.type_id not in WORKER_TYPES
            and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            and (
                u.can_attack_ground
                or u.type_id
                in (
                    UnitID.ORACLE,
                    UnitID.BANSHEE,
                    UnitID.SIEGETANKSIEGED,
                    UnitID.WIDOWMINEBURROWED,
                    UnitID.LURKERMPBURROWED,
                )
            )
        )
        relocatable = {
            UnitID.GATEWAY,
            UnitID.CYBERNETICSCORE,
            UnitID.ROBOTICSFACILITY,
            UnitID.ROBOTICSBAY,
            UnitID.FORGE,
            UnitID.TWILIGHTCOUNCIL,
        }
        cancellable_outer = {
            UnitID.SHIELDBATTERY,
            UnitID.PHOTONCANNON,
            UnitID.ASSIMILATOR,
        }
        for wtag, info in list(tracker.items()):
            sid = info.get(ID)
            target = info.get(TARGET)
            if sid is None or not isinstance(target, Point2):
                continue
            already_placed = any(
                s.distance_to(target) < 1.5 for s in self.structures
            )
            if (
                self.build_order_runner.build_completed
                and not already_placed
                and target.distance_to(self.start_location) >= 18.0
                and (sid in relocatable or sid in cancellable_outer)
            ):
                shellers = [
                    e
                    for e in enemy_shooters
                    if e.distance_to(target) <= max(e.ground_range, 6.5) + 2.5
                ]
                sheller_supply = sum(
                    self.calculate_supply_cost(e.type_id) for e in shellers
                )
                if sheller_supply >= 3.0:
                    if (
                        sid in relocatable
                        and ready_pylons
                        and prod_base.distance_to(target) > 16.0
                    ):
                        safe_slot = self.mediator.request_building_placement(
                            base_location=prod_base,
                            structure_type=sid,
                            within_psionic_matrix=True,
                            production=True,
                        ) or self.mediator.request_building_placement(
                            base_location=prod_base,
                            structure_type=sid,
                            within_psionic_matrix=True,
                            production=False,
                        )
                        if safe_slot is not None:
                            info[TARGET] = safe_slot
                            continue
                    elif sid in cancellable_outer:
                        self.manager_hub.building_manager.remove_unit(wtag)
                        continue
            if (
                not ready_pylons
                or sid in (UnitID.PYLON, UnitID.NEXUS, UnitID.ASSIMILATOR)
                or any(p.distance_to(target) <= 6.2 for p in ready_pylons)
            ):
                continue
            powered = self.mediator.request_building_placement(
                base_location=prod_base,
                structure_type=sid,
                within_psionic_matrix=True,
                production=True,
            ) or self.mediator.request_building_placement(
                base_location=prod_base,
                structure_type=sid,
                within_psionic_matrix=True,
                production=False,
            )
            if powered is not None:
                info[TARGET] = powered

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
        # starves the gas-heavy immortal/colossus comp. Disable vespene_boost
        # (broken in ares for Assimilators when workers_per_gas == 2) and
        # tighten flee thresholds so Probes pull out before Banshee 2-shots.
        workers_per_gas = 2 if self.vespene > 800 else 3
        self.register_behavior(
            Mining(
                workers_per_gas=workers_per_gas,
                vespene_boost=False,
                flee_at_health_perc=0.75,
                weight_safety_limit=8.0,
            )
        )

        prod_base: Point2 = self._production_base()
        self._repair_unpowered_building_targets(prod_base)
        macro_plan: MacroPlan = MacroPlan()
        if self.build_order_runner.build_completed:
            if self._emergency:
                # rush defense: gateway units + batteries, plus Immortals once
                # an emergency Robo completes vs armored 1-base armies
                # (Stalkers, Marauders, Roaches). Never build Zealots vs flyers
                # (kas 22-Mutalisk loss built 16 Zealots in emergency mode).
                if self._enemy_air_supply() >= 4.0:
                    comp = ARMY_COMP
                elif (
                    self.structures(UnitID.ROBOTICSFACILITY).ready
                    and self._enemy_armored_light_supply()[0] >= 6.0
                ):
                    comp = IMMORTAL_COMP
                else:
                    # Uncharged Zealots get kited by Terran Marines/Reapers/
                    # Hellions and vaporized by Widow Mines (VeTerran 0.19 trade).
                    comp = (
                        ARMY_COMP
                        if (
                            self._defense_opening
                            or self.enemy_race == Race.Terran
                        )
                        else self._emergency_comp
                    )
            elif self._all_in_read:
                # one-base all-in inbound: robo tech is too slow to matter,
                # pump gateway army now
                comp = ARMY_COMP
            else:
                # reactive robo composition vs the scouted enemy army
                comp = self._choose_army_comp()

            macro_plan.add(AutoSupply(base_location=prod_base))

            # Check whether a critical 3x3 tech/detection building is needed so
            # we can use non-production 3x3 slots or build a power Pylon at
            # >=100m instead of deadlocking at <350m (diagnosed from who's
            # ProxyDarkShrine loss where 4 gates + CyberCore filled all 5 main
            # production slots and blocked RoboticsFacility for 3+ minutes).
            has_gate = bool(
                self.structures(UnitID.GATEWAY).ready
                or self.structures(UnitID.WARPGATE).ready
            )
            need_cyber_rebuild = (
                has_gate
                and not self.structure_present_or_pending(UnitID.CYBERNETICSCORE)
            )
            gates_total = (
                self.structures(UnitID.GATEWAY).amount
                + self.structures(UnitID.WARPGATE).amount
                + self.already_pending(UnitID.GATEWAY)
            )
            emerg_army_supply = self.supply_used - self.supply_workers
            need_emergency_robo = (
                self._emergency
                and self.structures(UnitID.CYBERNETICSCORE).ready
                and not self.structures(UnitID.ROBOTICSFACILITY)
                and (
                    (
                        self.time >= 180.0
                        and gates_total >= 4
                        and emerg_army_supply >= 8.0
                    )
                    or (
                        gates_total >= 2
                        and emerg_army_supply >= 10.0
                        and self.vespene >= 175
                        and self._enemy_armored_light_supply()[0] >= 4.0
                    )
                )
            )
            need_detection_robo = (
                self._need_detection
                and self.structures(UnitID.CYBERNETICSCORE).ready
                and not self.structures(UnitID.ROBOTICSFACILITY)
            )
            need_urgent_3x3 = (
                need_cyber_rebuild
                or need_detection_robo
                or need_emergency_robo
            )
            has_prod_3x3 = (
                self.mediator.request_building_placement(
                    base_location=prod_base,
                    structure_type=UnitID.GATEWAY,
                    within_psionic_matrix=True,
                    reserve_placement=False,
                    production=True,
                )
                is not None
            )
            has_any_3x3 = has_prod_3x3 or (
                self.mediator.request_building_placement(
                    base_location=prod_base,
                    structure_type=UnitID.ROBOTICSFACILITY,
                    within_psionic_matrix=True,
                    reserve_placement=False,
                    production=False,
                )
                is not None
            )

            # Power-grid deadlock breaker (diagnosed from Thssprtssbt & who
            # losses): build a production Pylon whenever all powered 3x3 slots
            # are full and we either float >=350m or urgently need a 3x3 tech
            # structure (>=100m).
            if (
                not self.already_pending(UnitID.PYLON)
                and not self.not_started_but_in_building_tracker(UnitID.PYLON)
                and (
                    (self.minerals >= 350 and not has_prod_3x3)
                    or (need_urgent_3x3 and self.minerals >= 100 and not has_any_3x3)
                )
            ):
                macro_plan.add(
                    BuildStructure(
                        base_location=prod_base,
                        structure_id=UnitID.PYLON,
                        production=True,
                    )
                )

            # Train Observer #1 first when detection is needed, then Robo power
            # units (Colossi/Immortals) ahead of Observer #2 so a single Robo
            # doesn't spend 2 minutes replacing secondary Observers instead of
            # building Colossi (MicroMachine 0 Colossi with 936 gas).
            saving_for_observer = self._train_observers(urgent_only=True)
            saving_for_robo_unit = (
                False if saving_for_observer else self._train_robo_units(comp)
            )
            if not saving_for_observer and not saving_for_robo_unit:
                self._train_observers(urgent_only=False)

            # Rebuild CyberneticsCore immediately at a live base if lost or if
            # an early emergency aborted SafeExpand before CyberCore started
            # (Mulebot delayed CyberCore 01:19 -> 02:31).
            saving_for_cyber = False
            if need_cyber_rebuild:
                macro_plan.add(
                    BuildStructure(
                        base_location=prod_base,
                        structure_id=UnitID.CYBERNETICSCORE,
                        to_count=1,
                        production=has_prod_3x3,
                    )
                )
                saving_for_cyber = self.minerals < 175

            # Build a Robotics Facility immediately when cloak/burrow is
            # scouted and we don't have one yet (Hestia Banshees, Lissy Lurkers,
            # who ProxyDarkShrine). Keep saving_for_robo True while the builder
            # walks to the site too (SC2 deducts 150m/100g on placement, not on
            # dispatch), so SpawnController can't steal the builder's minerals.
            saving_for_robo = False
            if need_detection_robo:
                macro_plan.add(
                    BuildStructure(
                        base_location=prod_base,
                        structure_id=UnitID.ROBOTICSFACILITY,
                        to_count=1,
                        production=has_prod_3x3,
                    )
                )
                saving_for_robo = self.minerals < 275 or self.vespene < 150

            # post-hold conversion: once the all-in hold is clearly won, take
            # the natural. Merely adding an ExpansionController is NOT enough -
            # it has no mineral reservation, and SpawnController's continuous
            # spend pins the bank under ~105 (verified in the grind repro), so
            # the nexus never gets funded. While converting, the plan is ONLY
            # supply + expansion - army production pauses the ~40s it takes to
            # bank 400 (we are >=1.5x ahead by definition, so that is safe).
            posthold_expand = (
                (self._emergency or self._all_in_read)
                and (
                    self._won_the_hold()
                    or (
                        self.time >= 360.0
                        and emerg_army_supply >= 14.0
                        and not self._home_threat()
                    )
                )
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
                early_gate_priority = (
                    bool(self.structures(UnitID.GATEWAY).ready.idle)
                    and (self.supply_used - self.supply_workers) < 12.0
                    and self.minerals < 225
                )
                # 1-base ramp Shield Battery: ProtossStaticDefence places its
                # battery next to the Nexus (~12 range behind the ramp), so it
                # healed 0 shields during the Thssprtssbt ramp siege. Place one
                # right behind main_base_ramp.top_center first (also when our
                # natural Nexus is still under construction).
                ramp_top = self.main_base_ramp.top_center
                has_ramp_battery = any(
                    s.distance_to(ramp_top) < 9.0
                    or s.distance_to(self.start_location) < 16.0
                    for s in self.structures(UnitID.SHIELDBATTERY)
                )
                if (
                    len(self.townhalls.ready) <= 1
                    and self.structures(UnitID.CYBERNETICSCORE).ready
                    and not has_ramp_battery
                    and not self.already_pending(UnitID.SHIELDBATTERY)
                    and not self.not_started_but_in_building_tracker(
                        UnitID.SHIELDBATTERY
                    )
                ):
                    macro_plan.add(
                        BuildStructure(
                            base_location=self.start_location,
                            structure_id=UnitID.SHIELDBATTERY,
                            closest_to=ramp_top,
                            production=False,
                        )
                    )
                # Break prolonged 1-base standoffs or armored rushes with a Robo
                # (gives Immortals vs Stalker/Marauder/Roach + an Observer).
                if (
                    need_emergency_robo
                    and not need_detection_robo
                    and self.vespene >= 100
                ):
                    macro_plan.add(
                        BuildStructure(
                            base_location=prod_base,
                            structure_id=UnitID.ROBOTICSFACILITY,
                            to_count=1,
                            production=has_prod_3x3,
                        )
                    )
                    if not self._home_threat():
                        saving_for_robo = (
                            self.minerals < 275 or self.vespene < 150
                        )
                # units and production only - no expansions, no upgrades,
                # no worker overinvestment until the rush is dead
                if not (
                    saving_for_cyber
                    or saving_for_observer
                    or saving_for_robo
                    or saving_for_robo_unit
                ):
                    macro_plan.add(SpawnController(comp))
                # Pause Probe production while urgently saving for CyberCore or
                # our first detection Robo/Observer, OR while actively defending
                # our base with a tiny army (<12 supply) and >=16 working Probes.
                pause_emerg_probes = (
                    (saving_for_cyber and self.workers.amount >= 14)
                    or (
                        self._need_detection
                        and (saving_for_robo or saving_for_observer)
                        and self.workers.amount >= 8
                    )
                    or (
                        bool(self._home_threat())
                        and emerg_army_supply < 12.0
                        and self.workers.amount >= 16
                    )
                )
                if not pause_emerg_probes:
                    emerg_worker_cap = (
                        34
                        if (
                            len(self.townhalls.ready) >= 2
                            and not self._defense_opening
                        )
                        else 28
                    )
                    macro_plan.add(
                        BuildWorkers(
                            to_count=min(
                                emerg_worker_cap, 22 * len(self.townhalls)
                            )
                        )
                    )
                if not saving_for_robo and not saving_for_cyber:
                    # Cap emergency Assimilators at 2 while gas is banked or
                    # workers < 32 so we never pull 6 mineral probes onto gas #3-4
                    # while starving Stalkers during an early rush (MicroMachine).
                    if self.structures(UnitID.CYBERNETICSCORE).amount > 0:
                        emerg_gas = (
                            2
                            if (
                                self.vespene >= 100
                                or self.supply_workers < 32
                            )
                            else min(4, len(self.townhalls) * 2)
                        )
                        if (
                            not early_gate_priority
                            or self.gas_buildings.amount < 2
                        ):
                            macro_plan.add(
                                GasBuildingController(to_count=emerg_gas)
                            )
                    macro_plan.add(
                        ProductionController(
                            comp,
                            base_location=prod_base,
                            add_production_at_bank=(150, 0),
                        )
                    )
                # Bank-driven emergency Gateways: never float 1k+ minerals on 2
                # gates during an emergency hold (Thssprtssbt / VeTerran).
                if self.minerals >= 250 and not saving_for_robo:
                    gates = (
                        self.structures(UnitID.GATEWAY).amount
                        + self.structures(UnitID.WARPGATE).amount
                    )
                    pending_gates = self.already_pending(UnitID.GATEWAY)
                    target_gates = min(8, max(4, 3 * len(self.townhalls)))
                    if gates + pending_gates < target_gates and pending_gates < 2:
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.GATEWAY,
                                production=has_prod_3x3,
                            )
                        )
                # Battery at ready expansions once not starving idle Gateways
                # or dropping unfinished Batteries directly under enemy fire.
                if (
                    len(self.townhalls.ready) >= 2
                    and not early_gate_priority
                    and not self._home_threat()
                ):
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
                # (all minerals spent, army capped) - saturate up to 5 bases,
                # but pause probe cuts while defending an active attack on our
                # bases once we already have 36+ probes (MicroMachine built 16
                # probes while our army dropped to 2 Stalkers).
                if not (self._home_threat() and self.supply_workers >= 36):
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

                # Reactive Robo / RoboBay tech reservation AHEAD of
                # SpawnController: previously SpawnController pinned minerals
                # < 125 on Stalker warp-ins so RoboticsBay never got funded
                # (0 Colossi vs 43 Marines in BioBot2.0 / Terranosaur / Mulebot).
                saving_for_tech = False
                can_pause_for_tech = (
                    not self._home_threat() or army_supply >= 20.0
                )
                if (
                    not need_expand
                    and not self._all_in_read
                    and (not self._home_threat() or army_supply >= 16.0)
                    and army_supply >= 10.0
                    and self.structures(UnitID.CYBERNETICSCORE).ready
                ):
                    want_robo = (
                        UnitID.IMMORTAL in comp or UnitID.COLOSSUS in comp
                    )
                    if want_robo and not self.structures(
                        UnitID.ROBOTICSFACILITY
                    ):
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.ROBOTICSFACILITY,
                                to_count=1,
                                production=has_prod_3x3,
                            )
                        )
                        saving_for_tech = (
                            can_pause_for_tech
                            and self.vespene >= 50
                            and self.minerals < 275
                        )
                    elif (
                        UnitID.COLOSSUS in comp
                        and self.structures(UnitID.ROBOTICSFACILITY).ready
                        and not self.structures(UnitID.ROBOTICSBAY)
                    ):
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.ROBOTICSBAY,
                                to_count=1,
                                production=has_prod_3x3,
                            )
                        )
                        saving_for_tech = (
                            can_pause_for_tech
                            and self.vespene >= 75
                            and self.minerals < 275
                        )
                    elif (
                        UnitID.COLOSSUS in comp
                        and can_pause_for_tech
                        and self.structures(UnitID.ROBOTICSBAY).ready.idle
                        and UpgradeId.EXTENDEDTHERMALLANCE
                        not in self.state.upgrades
                        and not self.already_pending_upgrade(
                            UpgradeId.EXTENDEDTHERMALLANCE
                        )
                        and self.vespene >= 100
                    ):
                        saving_for_tech = not self.can_afford(
                            UpgradeId.EXTENDEDTHERMALLANCE
                        )

                saving_minerals = (
                    saving_for_observer
                    or saving_for_robo
                    or saving_for_robo_unit
                    or saving_for_tech
                    or (need_expand and self.minerals < 425)
                )

                # Saturation-driven Gateway floor (Rule 6): in MicroMachine v5,
                # ProductionController's (300, 300) bank gate never fired while
                # Probes + Forge + Twilight + Nexus #3 kept minerals < 300,
                # stranding PhoenixBot on 2 Gateways for 10:40 on 3 bases.
                cur_gates = (
                    self.structures(UnitID.GATEWAY).amount
                    + self.structures(UnitID.WARPGATE).amount
                )
                pend_gates = self.already_pending(UnitID.GATEWAY)
                min_gates = 0
                if (
                    len(self.townhalls.ready) >= 2
                    and self.structures(UnitID.CYBERNETICSCORE).ready
                    and not self._all_in_read
                ):
                    if (
                        self.supply_workers >= 52
                        and len(self.townhalls.ready) >= 3
                    ):
                        min_gates = 8
                    elif self.supply_workers >= 38:
                        min_gates = 6
                    elif self.supply_workers >= 29:
                        min_gates = 4
                    elif self.supply_workers >= 24:
                        min_gates = 3
                if (
                    cur_gates + pend_gates < min_gates
                    and pend_gates == 0
                    and not self.not_started_but_in_building_tracker(
                        UnitID.GATEWAY
                    )
                    and not need_expand
                    and not saving_minerals
                    and self.minerals >= 150
                ):
                    macro_plan.add(
                        BuildStructure(
                            base_location=prod_base,
                            structure_id=UnitID.GATEWAY,
                            production=has_prod_3x3,
                        )
                    )
                saving_for_gate = (
                    cur_gates + pend_gates < min_gates
                    and self.not_started_but_in_building_tracker(UnitID.GATEWAY)
                    and self.minerals < 175
                    and not self._home_threat()
                )

                # Upgrades ahead of SpawnController once stable: previously
                # WarpGates pinned minerals < 125 so +2/+2 and +3/+3 stalled
                # until minute 21 (DemsTossV2 4v11, BioBot2.0 4v9, Lissy 5v14).
                # Add a 2nd Forge on 3+ bases to cut +3/+3 time in half.
                if (
                    self.time > UPGRADES_AFTER
                    and army_supply >= 16
                    and (
                        len(self.townhalls.ready) < 2
                        or cur_gates + pend_gates >= 3
                    )
                    and not self._all_in_read
                    and not need_expand
                    and not saving_for_gate
                ):
                    macro_plan.add(
                        UpgradeController(
                            upgrade_list=list(DESIRED_UPGRADES),
                            base_location=prod_base,
                            prioritize=(
                                self.vespene >= 100
                                and army_supply >= 22.0
                                and not self._home_threat()
                                and not saving_minerals
                            ),
                        )
                    )
                    if (
                        len(self.townhalls) >= 3
                        and cur_gates + pend_gates >= 5
                        and self.time > 360.0
                        and army_supply >= 24.0
                        and not self._home_threat()
                        and not saving_minerals
                        and self.structures(UnitID.FORGE).amount == 1
                        and not self.already_pending(UnitID.FORGE)
                        and not self.not_started_but_in_building_tracker(
                            UnitID.FORGE
                        )
                        and self.minerals >= 200
                    ):
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.FORGE,
                                to_count=2,
                            )
                        )

                tracker = self.mediator.get_building_tracker_dict
                fresh_upgrade_bldg = any(
                    info.get(ID) in (UnitID.FORGE, UnitID.TWILIGHTCOUNCIL)
                    and self.time - info.get(TIME_ORDER_COMMENCED, 0.0) < 15.0
                    for info in tracker.values()
                )
                saving_for_upgrade_bldg = (
                    fresh_upgrade_bldg
                    and self.minerals < 175
                    and not self._home_threat()
                )
                if not (
                    saving_minerals
                    or saving_for_upgrade_bldg
                    or saving_for_gate
                ):
                    macro_plan.add(SpawnController(comp))
                # Pause competing mineral-draining buildings during short
                # Robo/tech/expand reservations so reservations complete in
                # 2-4s instead of freezing WarpGates for 60-96s (VeTerran).
                if not saving_minerals:
                    macro_plan.add(
                        ProductionController(comp, base_location=prod_base)
                    )
                # Bank-driven production drain (Rule 3 & Rule 6): ares'
                # ProductionController caps gateways/robos by current gas rate,
                # which left 3.4k minerals / 1.1k gas unspent at 10:00 on 5
                # bases once gas throttling kicked in. Add Gateways/Robos
                # whenever we're floating so our bank turns into max supply.
                if (
                    self.minerals >= 350
                    and not need_expand
                    and not saving_minerals
                ):
                    gates = (
                        self.structures(UnitID.GATEWAY).amount
                        + self.structures(UnitID.WARPGATE).amount
                    )
                    pending_gates = self.already_pending(UnitID.GATEWAY)
                    per_base = (
                        3 * len(self.townhalls)
                        if army_supply >= 36.0
                        else 2 * len(self.townhalls) + 1
                    )
                    target_gates = min(14, max(4, per_base))
                    if gates + pending_gates < target_gates and pending_gates < 2:
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.GATEWAY,
                                production=has_prod_3x3,
                            )
                        )
                if (
                    self.minerals >= 325
                    and self.vespene >= 350
                    and not need_expand
                    and not saving_minerals
                    and (UnitID.IMMORTAL in comp or UnitID.COLOSSUS in comp)
                    and self.structures(UnitID.CYBERNETICSCORE).ready
                ):
                    robos = self.structures(UnitID.ROBOTICSFACILITY).amount
                    pending_robos = self.already_pending(UnitID.ROBOTICSFACILITY)
                    target_robos = min(3, max(1, len(self.townhalls) - 1))
                    if army_supply < 28.0:
                        target_robos = 1
                    elif army_supply < 50.0:
                        target_robos = min(target_robos, 2)
                    if robos + pending_robos < target_robos and pending_robos == 0:
                        macro_plan.add(
                            BuildStructure(
                                base_location=prod_base,
                                structure_id=UnitID.ROBOTICSFACILITY,
                                production=has_prod_3x3,
                            )
                        )
                # shield battery at each base (auto-techs its prerequisites);
                # cannons skipped to avoid an early forge detour. Don't steal
                # 100m from idle early Gateways, active mineral reservations,
                # or drop unfinished Batteries directly under enemy fire.
                early_gate_priority = (
                    bool(self.structures(UnitID.GATEWAY).ready.idle)
                    and army_supply < 12.0
                    and self.minerals < 225
                )
                if (
                    not early_gate_priority
                    and not saving_minerals
                    and not self._home_threat()
                ):
                    macro_plan.add(
                        ProtossStaticDefence(
                            pylons_per_base=1,
                            photon_cannons_per_base=0,
                            shield_batteries_per_base=1,
                        )
                    )
                # Respect desired_bases so we don't drop an unprotected 4th
                # Nexus at 08:00 with only 24 army supply (MicroMachine); allow
                # expanding 1 ahead only when banking >=700m with a real army.
                if (
                    not self._all_in_read
                    and not need_expand
                    and not saving_minerals
                    and not self._home_threat()
                ):
                    extra_expand = (
                        1
                        if (self.minerals >= 700 and army_supply >= 36.0)
                        else 0
                    )
                    macro_plan.add(
                        ExpansionController(
                            to_count=min(5, desired_bases + extra_expand),
                            max_pending=1,
                        )
                    )
                # full gas geysers available once saturated; hold off taking
                # natural gas #3-4 before 30 probes when gas is already banked
                # so early mineral income funds Stalkers and Gateways.
                gas_cap = (
                    2
                    if (self.supply_workers < 30 and self.vespene >= 100)
                    else len(self.townhalls) * 2
                )
                if (not early_gate_priority or self.gas_buildings.amount < 2) and (
                    not saving_minerals or self.vespene < 150
                ):
                    macro_plan.add(GasBuildingController(to_count=gas_cap))
        else:
            macro_plan.add(SpawnController(ARMY_COMP))
        self.register_behavior(macro_plan)

        self._research_warpgate()
        self._research_thermal_lance()
        self._research_forge_and_twilight()
        self._chrono_production()

    async def _fallback_build_robo(self) -> None:
        """Native python-sc2 placement failsafe for urgent RoboticsFacility
        (detection or 1-base standoff) when all precalculated ares 3x3 slots
        at prod_base are occupied (who ProxyDarkShrine 4-gate main fill)."""
        if self.state.game_loop % 8 != 0:
            return
        gates_total = (
            self.structures(UnitID.GATEWAY).amount
            + self.structures(UnitID.WARPGATE).amount
            + self.already_pending(UnitID.GATEWAY)
        )
        urgent = self._need_detection or (
            self._emergency and self.time >= 210.0 and gates_total >= 4
        )
        if (
            not urgent
            or not self.structures(UnitID.CYBERNETICSCORE).ready
            or self.structure_present_or_pending(UnitID.ROBOTICSFACILITY)
            or self.not_started_but_in_building_tracker(UnitID.ROBOTICSFACILITY)
            or not self.can_afford(UnitID.ROBOTICSFACILITY)
        ):
            return
        pylons = self.structures(UnitID.PYLON).ready
        if not pylons:
            return
        prod_base = self._production_base()
        if (
            self.mediator.request_building_placement(
                base_location=prod_base,
                structure_type=UnitID.ROBOTICSFACILITY,
                within_psionic_matrix=True,
                reserve_placement=False,
                production=False,
            )
            is not None
        ):
            return
        anchor = pylons.closest_to(prod_base).position
        await self.build(UnitID.ROBOTICSFACILITY, near=anchor)

    def _research_warpgate(self) -> None:
        """Start Warp Gate research as soon as Cybernetics Core completes
        (~1:55 instead of waiting until 5:00 in UpgradeController, and even
        during OneBaseDefense/emergency where UpgradeController is off).
        50m/50g cuts Stalker cycle time from 30s to 23s (+30% throughput)."""
        if (
            UpgradeId.WARPGATERESEARCH in self.state.upgrades
            or self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH)
            or not self.can_afford(UpgradeId.WARPGATERESEARCH)
        ):
            return
        idle_cores = self.structures(UnitID.CYBERNETICSCORE).ready.idle
        if idle_cores:
            idle_cores.first.research(UpgradeId.WARPGATERESEARCH)

    def _research_thermal_lance(self) -> None:
        """Start Extended Thermal Lance (+2 Colossus range, 7 -> 9) as soon as
        Robotics Bay completes instead of queuing it behind +3/+3 Forge
        upgrades in DESIRED_UPGRADES."""
        if (
            UpgradeId.EXTENDEDTHERMALLANCE in self.state.upgrades
            or self.already_pending_upgrade(UpgradeId.EXTENDEDTHERMALLANCE)
            or not self.can_afford(UpgradeId.EXTENDEDTHERMALLANCE)
        ):
            return
        if (
            UnitID.COLOSSUS not in self._choose_army_comp()
            and not self.units(UnitID.COLOSSUS)
            and not self.already_pending(UnitID.COLOSSUS)
        ):
            return
        idle_bays = self.structures(UnitID.ROBOTICSBAY).ready.idle
        if idle_bays:
            idle_bays.first.research(UpgradeId.EXTENDEDTHERMALLANCE)

    def _research_forge_and_twilight(self) -> None:
        """Keep already-constructed Twilight Council and Forges researching
        continuously (Rule 10) even when UpgradeController is temporarily gated
        by expansion reservations or mid-fight supply dips (MicroMachine had
        Forge + Twilight ready at 07:46 with 800 gas but 0 Blink / 0 +1 at
        12:00)."""
        army_supply = self.supply_used - self.supply_workers
        if self._home_threat() and army_supply < 12.0:
            return
        if (
            self._need_detection
            and self.units(UnitID.OBSERVER).amount
            + self.already_pending(UnitID.OBSERVER)
            == 0
        ):
            return
        idle_twilights = self.structures(UnitID.TWILIGHTCOUNCIL).ready.idle
        if (
            idle_twilights
            and UpgradeId.BLINKTECH not in self.state.upgrades
            and not self.already_pending_upgrade(UpgradeId.BLINKTECH)
            and self.can_afford(UpgradeId.BLINKTECH)
        ):
            idle_twilights.first.research(UpgradeId.BLINKTECH)
        idle_forges = self.structures(UnitID.FORGE).ready.idle
        if not idle_forges:
            return
        has_twilight = bool(self.structures(UnitID.TWILIGHTCOUNCIL).ready)
        forge_chain: list[tuple[UpgradeId, Optional[UpgradeId], bool]] = [
            (UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1, None, False),
            (UpgradeId.PROTOSSGROUNDARMORSLEVEL1, None, False),
            (
                UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,
                UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1,
                True,
            ),
            (
                UpgradeId.PROTOSSGROUNDARMORSLEVEL2,
                UpgradeId.PROTOSSGROUNDARMORSLEVEL1,
                True,
            ),
            (
                UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3,
                UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,
                True,
            ),
            (
                UpgradeId.PROTOSSGROUNDARMORSLEVEL3,
                UpgradeId.PROTOSSGROUNDARMORSLEVEL2,
                True,
            ),
        ]
        for forge in idle_forges:
            for upg, prereq, need_twi in forge_chain:
                if upg in self.state.upgrades or self.already_pending_upgrade(
                    upg
                ):
                    continue
                if prereq is not None and prereq not in self.state.upgrades:
                    continue
                if need_twi and not has_twilight:
                    continue
                if self.can_afford(upg):
                    forge.research(upg)
                    break

    def _chrono_production(self) -> None:
        """Spend Nexus Chrono Boost energy across key bottlenecks instead of
        capping at 200 energy once Gateways become WarpGates."""
        structures_dict = self.mediator.get_own_structures_dict
        priority_types: list[UnitID] = [
            UnitID.CYBERNETICSCORE,
            UnitID.ROBOTICSFACILITY,
            UnitID.ROBOTICSBAY,
            UnitID.FORGE,
            UnitID.TWILIGHTCOUNCIL,
            UnitID.GATEWAY,
        ]
        if (
            self.supply_workers < 66
            and not self._emergency
            and not self._defense_opening
        ):
            priority_types.append(UnitID.NEXUS)

        chronoed_tags: set[int] = set()
        for th in self.townhalls:
            if th.energy < 50:
                continue
            for type_id in priority_types:
                busy = [
                    s
                    for s in structures_dict[type_id]
                    if s.build_progress >= 1.0
                    and not s.is_idle
                    and not s.has_buff(BuffId.CHRONOBOOSTENERGYCOST)
                    and s.tag not in chronoed_tags
                ]
                if busy:
                    th(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])
                    chronoed_tags.add(busy[0].tag)
                    break

    def _micro(
        self,
        forces: Units,
        target: Point2,
        hold_pos: Optional[Point2] = None,
    ) -> None:
        near_enemy: dict[int, Units] = self.mediator.get_units_in_range(
            start_points=forces,
            distances=15,
            query_tree=UnitTreeQueryType.AllEnemy,
            return_as_dict=True,
        )
        grid: np.ndarray = self.mediator.get_ground_grid
        clean_grid: np.ndarray = self.mediator.get_cached_ground_grid
        hold_height: float = (
            self.get_terrain_height(hold_pos) if hold_pos is not None else 0.0
        )
        robo_units: Units = forces.of_type({UnitID.COLOSSUS, UnitID.IMMORTAL})
        front_robo: Optional[Unit] = (
            cy_closest_to(target, robo_units)
            if (hold_pos is None and robo_units)
            else None
        )
        observers: Units = self.units(UnitID.OBSERVER)
        escort_obs: Optional[Unit] = (
            cy_closest_to(target, observers)
            if (
                hold_pos is None
                and self._need_detection
                and self._commenced_attack
                and observers
            )
            else None
        )

        for unit in forces:
            maneuver: CombatManeuver = CombatManeuver()

            all_close: Units = near_enemy[unit.tag].filter(
                lambda u: not u.is_memory
                and not u.is_hallucination
                and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            )
            only_enemy_units: Units = all_close.filter(
                lambda u: u.type_id not in ALL_STRUCTURES
            )
            # Never pick an undetected cloaked/burrowed unit as enemy_target
            # (cy_attack_ready is always False, which previously caused
            # StutterUnitBack to retreat 24 Stalkers across the map from 1 DT).
            attackable_units: Units = only_enemy_units.filter(
                lambda u: not (u.is_cloaked or u.is_burrowed) or u.is_revealed
            )
            unrevealed_threats: Units = only_enemy_units.filter(
                lambda u: (u.is_cloaked or u.is_burrowed) and not u.is_revealed
            )

            if all_close:
                # Prismatic Alignment Void Ray peel-back (Arpy / sharpy losses):
                # aligned Void Rays deal +6 bonus vs Armored (44 DPS) while
                # slowed to 2.62 speed vs Stalker 4.13. Kite out of the beam
                # until Alignment expires, then re-engage on its 43s cooldown.
                if unit.is_armored and attackable_units:
                    aligned_vrs = attackable_units.filter(
                        lambda u: u.type_id == UnitID.VOIDRAY
                        and u.has_buff(BuffId.VOIDRAYSWARMDAMAGEBOOST)
                        and u.distance_to(unit) < 8.5
                    )
                    if aligned_vrs:
                        safe: Point2 = self.mediator.find_closest_safe_spot(
                            from_pos=unit.position, grid=grid
                        )
                        if (
                            unit.type_id == UnitID.STALKER
                            and UpgradeId.BLINKTECH in self.state.upgrades
                            and self.time - self._blinked_at.get(unit.tag, -100.0)
                            > 11.0
                            and aligned_vrs.closest_distance_to(unit) < 6.5
                        ):
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
                        self.register_behavior(maneuver)
                        continue

                # shoot whatever is already in range (attackable units first)
                in_range_unit = False
                if in_attack_range := cy_in_attack_range(unit, attackable_units):
                    in_range_unit = True
                    maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_attack_range)
                    )
                elif in_attack_range := cy_in_attack_range(unit, all_close):
                    maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_attack_range)
                    )

                # Never pick an enemy unit our weapon cannot hit (MicroMachine
                # 11:03: Immortals picked flying Banshees as enemy_target and
                # StutterUnitForward-walked past Marauders straight into Sieged
                # Tanks without firing), and never get stuck pressing into a
                # cliff wall chasing a flyer over unpathable dead space.
                reachable_units: Units = attackable_units.filter(
                    lambda u: (
                        unit.can_attack_air
                        if u.is_flying
                        else unit.can_attack_ground
                    )
                    and (
                        (not u.is_flying)
                        or u.distance_to(unit) <= unit.air_range + 1.5
                        or self.in_pathing_grid(u.position)
                    )
                )
                structures_close: Units = all_close.filter(
                    lambda u: u.type_id in ALL_STRUCTURES
                    and (
                        unit.can_attack_air
                        if u.is_flying
                        else unit.can_attack_ground
                    )
                )
                if reachable_units:
                    enemy_target: Unit = cy_pick_enemy_target(reachable_units)
                elif structures_close:
                    enemy_target = cy_pick_enemy_target(structures_close)
                else:
                    # Only unattackable flyers, unrevealed cloaked threats, or
                    # out-of-range void flyers remain: pull ground-only units
                    # back to safety if air-to-ground raiders are hitting them.
                    exposed_to_air = (
                        not unit.can_attack_air
                        and any(
                            u.is_flying
                            and (
                                u.can_attack_ground
                                or u.type_id
                                in (UnitID.BANSHEE, UnitID.ORACLE)
                            )
                            and u.distance_to(unit) < 8.5
                            for u in only_enemy_units
                        )
                    )
                    if (
                        exposed_to_air
                        or (
                            unrevealed_threats
                            and unrevealed_threats.closest_distance_to(unit)
                            < 5.5
                        )
                        or (
                            unit.shield_percentage < 0.15
                            and unit.health_percentage < 0.75
                        )
                    ):
                        maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                    else:
                        maneuver.add(
                            PathUnitToTarget(
                                unit=unit, grid=clean_grid, target=target
                            )
                        )
                        maneuver.add(AMove(unit=unit, target=target))
                    self.register_behavior(maneuver)
                    continue
                # Ramp-hold leash (Thssprtssbt loss): never march down our own
                # main ramp 1-by-1 into a larger army camping the low ground.
                # Units shoot freely from high ground and stay near hold_pos
                # until the enemy actually climbs onto our terrain height.
                if hold_pos is not None:
                    unit_height = self.get_terrain_height(unit.position)
                    enemy_height = self.get_terrain_height(enemy_target.position)
                    if (
                        unit.distance_to(hold_pos) > 5.5
                        or unit_height < hold_height - 4.0
                    ):
                        maneuver.add(
                            PathUnitToTarget(
                                unit=unit, grid=grid, target=hold_pos
                            )
                        )
                        self.register_behavior(maneuver)
                        continue
                    if (
                        enemy_height < hold_height - 4.0
                        or enemy_target.distance_to(hold_pos) > 8.5
                    ):
                        if unit.shield_percentage < 0.2:
                            maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                        elif unit.distance_to(hold_pos) > 3.0:
                            maneuver.add(
                                PathUnitToTarget(
                                    unit=unit, grid=grid, target=hold_pos
                                )
                            )
                        elif in_range_unit:
                            maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                        self.register_behavior(maneuver)
                        continue

                is_shredded = unit.has_buff(
                    BuffId.RAVENSHREDDERMISSILEARMORREDUCTION
                )
                is_locked_on = unit.has_buff(BuffId.LOCKON)
                if unit.type_id == UnitID.ZEALOT:
                    # Zealots are melee: always close in and fight rather than
                    # kiting backwards away from enemies
                    maneuver.add(AMove(unit=unit, target=enemy_target.position))
                elif (
                    unit.type_id == UnitID.STALKER
                    and (
                        is_locked_on
                        or unit.shield_percentage
                        < (0.55 if is_shredded else 0.3)
                    )
                    and UpgradeId.BLINKTECH in self.state.upgrades
                    and self.time - self._blinked_at.get(unit.tag, -100.0) > 11.0
                ):
                    # Blink-back damaged, Anti-Armor debuffed, or Cyclone
                    # Lock-On targeted Stalker to break the 15-tile tether.
                    safe = self.mediator.find_closest_safe_spot(
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
                elif (
                    unit.type_id == UnitID.STALKER
                    and hold_pos is None
                    and not is_shredded
                    and not is_locked_on
                    and unit.shield_percentage >= 0.65
                    and enemy_target.type_id in SIEGE_BLINK_TARGETS
                    and UpgradeId.BLINKTECH in self.state.upgrades
                    and self.time - self._blinked_at.get(unit.tag, -100.0) > 11.0
                    and 6.5 <= unit.distance_to(enemy_target) <= 13.5
                    and self.in_pathing_grid(
                        blink_pos := unit.position.towards(
                            enemy_target.position,
                            min(8.0, unit.distance_to(enemy_target) - 2.5),
                        )
                    )
                    and (
                        not any(
                            (e.is_cloaked or e.is_burrowed)
                            and e.type_id
                            not in (UnitID.WIDOWMINE, UnitID.WIDOWMINEBURROWED)
                            and e.distance_to(blink_pos) < 10.5
                            for e in only_enemy_units
                        )
                        or any(
                            obs.distance_to(blink_pos) < 10.0
                            for obs in observers
                        )
                    )
                    and (
                        (
                            sieged_tanks_in_range := sum(
                                1
                                for e in only_enemy_units
                                if e.type_id == UnitID.SIEGETANKSIEGED
                                and e.distance_to(blink_pos) < 13.5
                            )
                        )
                        < 2
                        or sum(
                            1 for f in forces if f.distance_to(unit) < 9.0
                        )
                        >= 4 * sieged_tanks_in_range
                    )
                    and (
                        (
                            escort_cnt := sum(
                                1
                                for e in only_enemy_units
                                if e.tag != enemy_target.tag
                                and e.type_id not in WORKER_TYPES
                                and e.distance_to(blink_pos) < 6.5
                            )
                        )
                        < 4
                        or sum(
                            1 for f in forces if f.distance_to(unit) < 9.0
                        )
                        > escort_cnt + 2
                    )
                ):
                    # Offensive Blink-forward onto long-range siege units
                    # (Tempests / Sieged Tanks / Brood Lords / Warp Prisms)
                    # when unguarded or supported by a larger local force.
                    maneuver.add(
                        UseAbility(
                            AbilityId.EFFECT_BLINK_STALKER,
                            unit,
                            blink_pos,
                        )
                    )
                    self._blinked_at[unit.tag] = self.time
                elif (
                    (
                        unit.shield_percentage < 0.1
                        and unit.health_percentage < 0.75
                    )
                    or (is_shredded and unit.shield_percentage < 0.25)
                    or (is_locked_on and unit.shield_percentage < 0.7)
                ):
                    # Walk back when hull is taking damage, -3 armor debuffed,
                    # or tethered by Cyclone Lock-On (breaks 15-range tether).
                    maneuver.add(KeepUnitSafe(unit=unit, grid=grid))
                else:
                    # Ranged stutter: ONLY step back on cooldown when already in
                    # weapon range AND enemy doesn't outrange us. Previously
                    # calling StutterUnitBack when out of range ran Stalkers
                    # backwards from melee units, and kiting away from range-14
                    # Tempests let them kite out of range 6 forever.
                    own_range = (
                        unit.air_range
                        if enemy_target.is_flying
                        else unit.ground_range
                    )
                    enemy_range = (
                        enemy_target.air_range
                        if unit.is_flying
                        else enemy_target.ground_range
                    )
                    if (
                        in_range_unit
                        and enemy_target.type_id not in ALL_STRUCTURES
                        and enemy_range <= own_range + 0.5
                    ):
                        maneuver.add(
                            StutterUnitBack(
                                unit=unit, target=enemy_target, grid=grid
                            )
                        )
                    elif not in_range_unit and (
                        abs(
                            self.get_terrain_height(unit.position)
                            - self.get_terrain_height(enemy_target.position)
                        )
                        > 4.0
                        or not self.in_pathing_grid(enemy_target.position)
                    ):
                        # Enemy is across a cliff/ramp: path up the ramp on
                        # clean_grid instead of straight-line cliff wedging.
                        ramp_dest = (
                            enemy_target.position
                            if self.in_pathing_grid(enemy_target.position)
                            else target
                        )
                        maneuver.add(
                            PathUnitToTarget(
                                unit=unit, grid=clean_grid, target=ramp_dest
                            )
                        )
                    else:
                        maneuver.add(
                            StutterUnitForward(unit=unit, target=enemy_target)
                        )
            else:
                # Deathball cohesion: keep fast Stalkers/Zealots screened in
                # front of our slower Colossi/Immortals (and escort Observer vs
                # confirmed cloak/burrow threats) while marching so the screen
                # doesn't arrive 10s early blind or piecemeal.
                move_target = target
                if (
                    front_robo is not None
                    and unit.type_id in (UnitID.STALKER, UnitID.ZEALOT)
                    and unit.distance_to(target) + 8.0
                    < front_robo.distance_to(target)
                    and unit.distance_to(front_robo) > 10.0
                ):
                    move_target = front_robo.position.towards(target, 4.0)
                elif (
                    escort_obs is not None
                    and unit.type_id in (UnitID.STALKER, UnitID.ZEALOT)
                    and unit.distance_to(target) + 10.0
                    < escort_obs.distance_to(target)
                    and 12.0 < unit.distance_to(escort_obs) < 35.0
                ):
                    move_target = escort_obs.position.towards(target, 6.0)
                maneuver.add(
                    PathUnitToTarget(unit=unit, grid=grid, target=move_target)
                )
                maneuver.add(AMove(unit=unit, target=move_target))

            self.register_behavior(maneuver)
