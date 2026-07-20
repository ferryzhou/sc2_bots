"""AiurBot -- a concise Protoss bot driven by the ``strategy_engine`` library.

One file, one loop each step::

    perceive (scout -> enemy_memory) -> advise (StrategicAdvisor) -> act (macro + army)

Every strategic decision -- opponent archetype, engagement odds, defense plan,
investment priority, power timing, efficiency, harassment, rules -- comes from
the library (which mirrors ``PRINCIPLES.md`` / ``STRATEGY.md`` / ``COMBAT.md``).
This file only translates an ``Advice`` into Protoss build/train/move orders, so
the principles (never stop probes, don't get supply blocked, spend your money,
expand, scout, fight only favorable engagements, keep upgrades working) are
*executed* here but *decided* in the library.
"""

import os
import random
import sys

# make the repo-root strategy_engine importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sc2.bot_ai import BotAI
from sc2.data import Race, Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as Up

from strategy_engine import (
    StrategicAdvisor,
    GameState,
    Engagement,
    classify_opening,
    ProductionState,
    plan_production,
    desired_gateways,
    desired_robos,
    desired_stargates,
)

# gateway unit token -> its warp-in ability (for warpgate production)
WARP_ABILITY = {
    U.ZEALOT: AbilityId.WARPGATETRAIN_ZEALOT,
    U.STALKER: AbilityId.WARPGATETRAIN_STALKER,
    U.ADEPT: AbilityId.TRAINWARP_ADEPT,
    U.SENTRY: AbilityId.WARPGATETRAIN_SENTRY,
    U.HIGHTEMPLAR: AbilityId.WARPGATETRAIN_HIGHTEMPLAR,
}
# tech-building key (strategy_engine.production) -> the structure that provides it
TECH_STRUCT = {
    "CYBERNETICSCORE": U.CYBERNETICSCORE, "ROBOTICSFACILITY": U.ROBOTICSFACILITY,
    "STARGATE": U.STARGATE, "ROBOTICSBAY": U.ROBOTICSBAY,
    "TEMPLARARCHIVE": U.TEMPLARARCHIVE, "FLEETBEACON": U.FLEETBEACON,
}

# --------------------------------------------------------------------------- #
# Scouting tables: enemy structure -> normalized name (for classify_opening)   #
# and the type sets / supply estimates the perception layer folds into memory. #
# --------------------------------------------------------------------------- #
OPENING_STRUCT = {
    U.NEXUS: "Nexus", U.GATEWAY: "Gateway", U.WARPGATE: "Gateway",
    U.CYBERNETICSCORE: "CyberneticsCore", U.FORGE: "Forge",
    U.PHOTONCANNON: "PhotonCannon", U.ASSIMILATOR: "Assimilator",
    U.ROBOTICSFACILITY: "RoboticsFacility", U.STARGATE: "Stargate",
    U.TWILIGHTCOUNCIL: "TwilightCouncil",
    U.COMMANDCENTER: "CommandCenter", U.ORBITALCOMMAND: "CommandCenter",
    U.PLANETARYFORTRESS: "CommandCenter", U.SUPPLYDEPOT: "SupplyDepot",
    U.BARRACKS: "Barracks", U.REFINERY: "Refinery", U.FACTORY: "Factory",
    U.STARPORT: "Starport", U.ENGINEERINGBAY: "EngineeringBay", U.BUNKER: "Bunker",
    U.HATCHERY: "Hatchery", U.LAIR: "Hatchery", U.HIVE: "Hatchery",
    U.SPAWNINGPOOL: "SpawningPool", U.EXTRACTOR: "Extractor",
    U.ROACHWARREN: "RoachWarren", U.BANELINGNEST: "BanelingNest",
    U.EVOLUTIONCHAMBER: "EvolutionChamber", U.SPINECRAWLER: "SpineCrawler",
    U.HYDRALISKDEN: "HydraliskDen",
}
OPENING_GAS = {"Assimilator", "Refinery", "Extractor"}
OPENING_TH = {"Nexus", "CommandCenter", "Hatchery"}
TOWNHALLS = {U.NEXUS, U.HATCHERY, U.LAIR, U.HIVE, U.COMMANDCENTER,
             U.ORBITALCOMMAND, U.PLANETARYFORTRESS}
PRODUCTION = {U.GATEWAY, U.WARPGATE, U.ROBOTICSFACILITY, U.STARGATE,
              U.BARRACKS, U.FACTORY, U.STARPORT,
              U.ROACHWARREN, U.HYDRALISKDEN, U.SPAWNINGPOOL}
GAS = {U.ASSIMILATOR, U.REFINERY, U.EXTRACTOR}
STATIC_DEF = {U.PHOTONCANNON, U.SPINECRAWLER, U.BUNKER, U.MISSILETURRET, U.SPORECRAWLER}
WORKERS = {U.PROBE, U.SCV, U.DRONE}
CLOAK_HINTS = {U.DARKTEMPLAR, U.BANSHEE, U.DARKSHRINE, U.GHOST,
               U.ROACHWARREN, U.LURKERDENMP}
AIR_HINTS = {U.STARGATE, U.STARPORT, U.SPIRE, U.VOIDRAY, U.PHOENIX, U.ORACLE,
             U.MUTALISK, U.BANSHEE, U.LIBERATOR, U.CARRIER, U.TEMPEST,
             U.BROODLORD, U.GREATERSPIRE, U.CORRUPTOR, U.BATTLECRUISER}
# light ground units -- a mass of these is a splash (AoE) target
LIGHT_GROUND = {U.ZERGLING, U.BANELING, U.HYDRALISK, U.MARINE, U.ZEALOT,
                U.ADEPT, U.REAPER}
ARMY_SUPPLY = {
    U.ZERGLING: 0.5, U.BANELING: 0.5, U.ROACH: 2, U.HYDRALISK: 2, U.QUEEN: 2,
    U.MUTALISK: 2, U.ULTRALISK: 6, U.LURKERMP: 3, U.RAVAGER: 3,
    U.ZEALOT: 2, U.STALKER: 2, U.ADEPT: 2, U.SENTRY: 2, U.IMMORTAL: 4,
    U.COLOSSUS: 6, U.ARCHON: 4, U.HIGHTEMPLAR: 2, U.DARKTEMPLAR: 2,
    U.VOIDRAY: 4, U.PHOENIX: 2, U.CARRIER: 6, U.TEMPEST: 5,
    U.MARINE: 1, U.MARAUDER: 2, U.HELLION: 2, U.SIEGETANK: 3, U.THOR: 6,
    U.CYCLONE: 3, U.MEDIVAC: 2, U.VIKINGFIGHTER: 2, U.BANSHEE: 3,
}
ARMY = {U.ZEALOT, U.STALKER, U.IMMORTAL, U.ARCHON, U.ADEPT, U.SENTRY,
        U.HIGHTEMPLAR, U.DARKTEMPLAR, U.COLOSSUS, U.VOIDRAY, U.TEMPEST}
# enemy air units to prioritize for anti-air focus-fire
AIR_ENEMY_UNITS = {U.MUTALISK, U.BANSHEE, U.VOIDRAY, U.PHOENIX, U.ORACLE,
                   U.CARRIER, U.TEMPEST, U.LIBERATOR, U.VIKINGFIGHTER,
                   U.MEDIVAC, U.BATTLECRUISER, U.BROODLORD}


class AiurBot(BotAI):
    """Protoss bot: perceive -> advise (library) -> act."""

    def __init__(self):
        super().__init__()
        self.enemy_memory = {}          # scouting -> belief, fed to the engine
        self.advisor = StrategicAdvisor()
        self.scout_tag = None
        self.scout_sent = False
        self.last_log = 0.0
        self.enemy_opening = None
        self._wall = None               # cached ramp wall layout
        self.force_build_id = None      # set by run.py --build; a spawningtool id
        self.build_script = None
        self._expo_loc = None           # cached next-expansion Point2
        self._expo_probe = None          # tag of the pre-sent builder probe

    # placement hooks for the shared buildscript driver (see buildscript.py)
    def bs_pylon_pos(self):
        return self._wall_pylon()

    def bs_wall_pos(self, i):
        return self._wall_building(i)

    async def on_start(self):
        self.client.game_step = 4       # responsive without being wasteful
        if self.force_build_id is not None:
            from buildscript import BuildScript
            self.build_script = BuildScript(self.force_build_id)
            if self.build_script.active:
                print(f"reproducing build: {self.build_script.build.title}")

    async def on_step(self, iteration):
        if not self.townhalls:
            for w in self.workers:       # last-ditch: everyone attacks
                w.attack(self.enemy_start_locations[0])
            return
        await self.distribute_workers()
        self._perceive()
        advice = self._advise()
        await self._macro(advice)
        self._army(advice)
        self._log(advice)

    async def on_end(self, result: Result):
        print(f"AiurBot game ended: {result}")

    # -------------------------------------------------------------- perceive ---
    def _perceive(self):
        """Fold visible enemy units/structures into enemy_memory for the engine.

        Structure counts are max-ever-seen (they persist through fog); the army
        read is current-visible so a spent flood reads as spent.
        """
        mem = self.enemy_memory
        enemies = self.enemy_units | self.enemy_structures
        home = self.start_location

        def seen(types):
            return self.enemy_structures.of_type(types).amount

        mem["enemy_base_count"] = max(mem.get("enemy_base_count") or 0, seen(TOWNHALLS)) or None
        mem["enemy_production_structures"] = max(mem.get("enemy_production_structures") or 0, seen(PRODUCTION))
        mem["enemy_gas_count"] = max(mem.get("enemy_gas_count") or 0, seen(GAS))
        mem["enemy_static_defense"] = max(mem.get("enemy_static_defense") or 0, seen(STATIC_DEF))
        vis_workers = self.enemy_units.of_type(WORKERS).amount
        mem["enemy_worker_count"] = max(mem.get("enemy_worker_count") or 0, vis_workers) or None
        if self.enemy_units:
            mem["enemy_army_supply"] = sum(
                ARMY_SUPPLY.get(u.type_id, 0) for u in self.enemy_units
                if u.type_id not in WORKERS)

        if enemies:
            mem["last_scouted_time"] = self.time
        if any(e.type_id in CLOAK_HINTS for e in enemies):
            mem["enemy_has_cloak"] = True
        if any(e.type_id in AIR_HINTS for e in enemies):
            mem["enemy_has_air"] = True
        # a mass of light ground units is a splash target (sticky: Zerg re-floods)
        if self.enemy_units.of_type(LIGHT_GROUND).amount >= 10:
            mem["enemy_massing_light"] = True
        if self.enemy_structures and self.enemy_structures.closest_distance_to(home) < 45:
            mem["enemy_proxy"] = True
        near = self.enemy_units.filter(
            lambda u: u.type_id not in WORKERS and u.distance_to(home) < 55)
        mem["enemy_army_moving_out"] = near.amount >= 3
        self._track_opening(mem)

    def _track_opening(self, mem):
        """Record first-seen time + placement zone of each enemy structure, so
        ``classify_opening`` can name the opponent's opening family."""
        seen = mem.setdefault("enemy_opening_seen", {})
        enemy_main = self.enemy_start_locations[0]
        home = self.start_location
        for s in self.enemy_structures:
            name = OPENING_STRUCT.get(s.type_id)
            if name is None or name in seen:
                continue
            d_enemy = s.distance_to(enemy_main)
            d_home = s.distance_to(home)
            zone = ("forward" if (d_home < d_enemy and d_home < 60)
                    else "main" if d_enemy <= 14
                    else "ramp_wall" if d_enemy <= 30
                    else "natural")
            seen[name] = {"t": self.time, "zone": zone}
        gas_ts = [d["t"] for n, d in seen.items() if n in OPENING_GAS]
        mem["enemy_first_gas"] = min(gas_ts) if gas_ts else None
        exp_ts = [d["t"] for n, d in seen.items()
                  if n in OPENING_TH and d["zone"] in ("natural", "ramp_wall")]
        mem["enemy_expand_t"] = min(exp_ts) if exp_ts else None

    # --------------------------------------------------------------- advise ----
    def _advise(self):
        """Build a GameState (+ Protoss-specific reads), hand it to the library."""
        mem = dict(self.enemy_memory)
        er = getattr(self, "enemy_race", None)
        mem["enemy_race"] = er.name if er is not None and hasattr(er, "name") else None
        mem["have_detection"] = (
            self.units(U.OBSERVER).amount + self.structures(U.PHOTONCANNON).ready.amount > 0)
        # composition read: mass-light Zerg wants splash; flag unfavorable if we
        # are stalker-heavy with no splash vs Zerg.
        if self.enemy_race == Race.Zerg:
            splash = (self.units(U.COLOSSUS).amount + self.units(U.HIGHTEMPLAR).amount
                      + self.units(U.ARCHON).amount)
            zealots = self.units(U.ZEALOT).amount
            stalkers = self.units(U.STALKER).amount
            mem["composition_favorable"] = (splash > 0 or zealots >= stalkers)

        state = GameState.from_bot(self, mem)
        # production / upgrade context the adapter can't see
        state.production_structures = (
            self.structures(U.GATEWAY).amount + self.structures(U.WARPGATE).amount
            + self.structures(U.ROBOTICSFACILITY).amount + self.structures(U.STARGATE).amount)
        state.idle_production = sum(
            1 for g in (self.structures(U.GATEWAY).ready
                        | self.structures(U.ROBOTICSFACILITY).ready) if g.is_idle)
        state.upgrade_structures = self.structures(U.FORGE).ready.amount
        state.upgrades_done = len(self.state.upgrades) if self.state.upgrades else 0
        state.has_harass_units = self.units.of_type({U.ORACLE, U.PHOENIX, U.DARKTEMPLAR}).amount > 0

        advice = self.advisor.advise(state)
        # name the enemy's opening from what we've scouted (reuses the openings
        # library); surfaced for awareness/logging.
        race = mem.get("enemy_race")
        seen = mem.get("enemy_opening_seen") or {}
        if race in ("Protoss", "Terran", "Zerg") and seen:
            signals = [(n, d["t"], d["zone"]) for n, d in seen.items()]
            self.enemy_opening = classify_opening(
                race, signals, mem.get("enemy_first_gas"), mem.get("enemy_expand_t"))
        else:
            self.enemy_opening = None
        return advice

    # ---------------------------------------------------------------- macro ----
    async def _macro(self, advice):
        # Supply, probes, and chrono always run adaptively (avoid supply blocks,
        # never stop workers). The rest is either driven by a scripted build (the
        # --build opening, reproducing a pro benchmark) or the reactive managers.
        self._chrono()
        scripted = (self.build_script is not None and self.build_script.active
                    and not advice.defense.emergency)
        if scripted:
            # the script OWNS supply/tech/army/expansion/gas AND workers while active
            # (probes and pylons yield to the Nexus via the shared allocator, so the
            # opening never supply-blocks or starves an expansion); still defend.
            await self.build_script.step(self, advice, manage_workers=True,
                                         worker_cap=advice.macro.worker_cap)
            await self._defense(advice)
            return
        await self._supply(advice)
        self._probes(advice)
        await self._gas()
        await self._expand(advice)
        if not self.structures(U.PYLON).ready:
            return
        await self._tech(advice)
        await self._defense(advice)
        await self._upgrades()
        await self._train(advice)

    def _probes(self, advice):
        # Principle 1: never stop producing workers (while safe) -- but the macro
        # plan owns the cap and can pause probes to force units when floating.
        cap = advice.macro.worker_cap
        if self.supply_workers >= cap:
            return
        # while thin and rushed, bank for gateway units
        if (advice.defense.prioritize_army and self.supply_army < 8
                and self.time < 240 and self.minerals < 200):
            return
        # force-train: cut probes for a tick so army production gets the supply/money
        if advice.macro.force_train and self.supply_left <= 3:
            return
        for nexus in self.townhalls.ready.idle:
            if self.can_afford(U.PROBE) and self.supply_left > 0:
                nexus.train(U.PROBE)

    async def _supply(self, advice):
        # Principle 2: don't get supply blocked -- build well ahead of the block.
        # The macro plan raises parallel-pylon limits when we're floating.
        production = max(1, self.structures(U.GATEWAY).amount + self.structures(U.WARPGATE).amount)
        threshold = 3 + 2 * production
        pending = self.already_pending(U.PYLON)
        parallel = advice.macro.allow_parallel_build
        floating = self.minerals > 500 and self.supply_cap >= 32
        if (self.supply_cap < 200 and self.townhalls and self.can_afford(U.PYLON)
                and ((self.supply_left <= threshold and pending < 1 + parallel)
                     or (floating and pending < 2 + parallel))):
            wp = self._wall_pylon()
            if wp is not None and not self.structures(U.PYLON):
                await self.build(U.PYLON, near=wp)
            else:
                nexus = self.townhalls.ready.random if self.townhalls.ready else self.townhalls.first
                await self.build(U.PYLON, near=nexus.position.towards(self.game_info.map_center, 6))

    async def _gas(self):
        # Take gas only when we can staff it. Grabbing it earlier (as the greedy
        # opening did at ~0:27) both drains minerals the natural needs AND leaves
        # the geyser empty until the mineral line saturates -- pure waste. So hold
        # the first gas until ~14 workers / the natural, then 2 per base.
        if not self.structures(U.GATEWAY):
            return
        if self.townhalls.amount < 2 and self.supply_workers < 14:
            return
        want = min(2 * self.townhalls.ready.amount, 6)
        have = self.gas_buildings.amount + self.already_pending(U.ASSIMILATOR)
        if have >= want or not self.can_afford(U.ASSIMILATOR):
            return
        for nexus in self.townhalls.ready:
            for g in self.vespene_geyser.closer_than(10, nexus):
                if not self.gas_buildings.closer_than(1, g):
                    w = self.select_build_worker(g.position)
                    if w:
                        w.build_gas(g)
                    return

    async def _expand(self, advice):
        # Principle 4: execute the library's base target. It grows the target through
        # the mid-late game and caps our production so minerals are left for the Nexus,
        # so here we just take the base when we're below target.
        if advice.defense.emergency:
            return  # under an active all-in -- army first
        if self.townhalls.amount + self.already_pending(U.NEXUS) < advice.macro.base_target:
            await self._prep_expansion()   # pre-send the builder probe when close
            if self.can_afford(U.NEXUS):
                await self._do_expansion()

    async def _prep_expansion(self):
        """Pre-send a probe to the next base when we're close to affording it, so
        the Nexus is placed the instant the bank crosses 400 -- travel overlaps
        banking instead of following it (saves ~30-40s per expansion). Pro basic."""
        if self.already_pending(U.NEXUS):
            self._expo_loc = self._expo_probe = None
            return
        if self._expo_loc is None:
            self._expo_loc = await self.get_next_expansion()
        loc = self._expo_loc
        if loc is None:
            return
        if self.minerals >= 260 and self._expo_probe is None and self.workers.gathering:
            w = self.workers.gathering.closest_to(loc)
            if w is not None:
                self._expo_probe = w.tag
                w.move(loc)

    async def _do_expansion(self):
        """Place the Nexus now, reusing the pre-sent probe if it's on-site."""
        loc = self._expo_loc or await self.get_next_expansion()
        if loc is None:
            return False
        probe = self.workers.find_by_tag(self._expo_probe) if self._expo_probe else None
        if probe is None and self.workers.gathering:
            probe = self.workers.gathering.closest_to(loc)
        if probe is None:
            return False
        probe.build(U.NEXUS, loc)
        self._expo_loc = self._expo_probe = None
        return True

    # expansion hooks for the shared buildscript driver
    async def bs_prep_expansion(self):
        await self._prep_expansion()

    async def bs_expand(self):
        return await self._do_expansion()

    async def _tech(self, advice):
        gates = self.structures(U.GATEWAY)
        # count warpgates too: once Warp Gate research lands, gateways morph out of
        # structures(GATEWAY), so 'do we have a gateway' must include warpgates or we
        # wrongly rebuild the 'first gateway' on the wall forever.
        gate_count = gates.amount + self.structures(U.WARPGATE).amount
        pylon = self.structures(U.PYLON).ready.random

        # Forge-FIRST when the library wants static defense -- but only for a
        # scouted rush (emergency) or once the natural is down. PROACTIVE insurance
        # must not preempt the greedy expand: pros take the natural first (~2:00)
        # and add the cannon/wall reactively. (This was spending 450 min on a
        # forge + 2 cannons before the Nexus, slipping it to ~4:45.)
        if (advice.defense.static_defense >= 1 and not self.structures(U.FORGE)
                and self.already_pending(U.FORGE) == 0 and self.can_afford(U.FORGE)
                and (advice.defense.emergency or self.townhalls.amount >= 2)):
            await self.build(U.FORGE, near=pylon)
            return
        # first gateway -- on the ramp wall if we can
        if gate_count + self.already_pending(U.GATEWAY) == 0:
            if self.can_afford(U.GATEWAY):
                wp = self._wall_building(0)
                near = wp if wp is not None else pylon.position.towards(self.game_info.map_center, 5)
                await self.build(U.GATEWAY, near=near)
            return
        # under a real EMERGENCY, hold the rest of the tech until cannons are up
        if advice.defense.emergency:
            cannons = self.structures(U.PHOTONCANNON).amount + self.already_pending(U.PHOTONCANNON)
            if self.structures(U.FORGE).ready and cannons < advice.defense.static_defense:
                if (gate_count + self.already_pending(U.GATEWAY) < 2
                        and self.can_afford(U.GATEWAY) and self.minerals > 320):
                    await self.build(U.GATEWAY, near=pylon.position.towards(self.game_info.map_center, 5))
                return
        # cybernetics core after the first gateway -- completes the ramp wall
        if gates.ready and not self.structures(U.CYBERNETICSCORE) and self.already_pending(U.CYBERNETICSCORE) == 0:
            if self.can_afford(U.CYBERNETICSCORE):
                wp = self._wall_building(1)
                near = wp if wp is not None else pylon
                await self.build(U.CYBERNETICSCORE, near=near)
            return
        if not self.structures(U.CYBERNETICSCORE).ready:
            return
        # Greedy opening (pro macro standard): once Gateway + Cyber are up, HOLD all
        # further tech until the natural is down, so minerals bank for a fast Nexus
        # (~2:30 instead of ~5:00). A real rush flips defense.emergency, which both
        # skips this hold and stops the expand -- so greed only happens when safe.
        if (advice.macro.base_target >= 2 and self.townhalls.amount < 2
                and not advice.defense.emergency):
            return
        # robotics for immortals + observer (detection, anti-armor)
        if not self.structures(U.ROBOTICSFACILITY) and self.already_pending(U.ROBOTICSFACILITY) == 0:
            if self.can_afford(U.ROBOTICSFACILITY):
                await self.build(U.ROBOTICSFACILITY, near=pylon)
        # forge for upgrades (if not already up for defense)
        if not self.structures(U.FORGE) and self.already_pending(U.FORGE) == 0:
            if self.can_afford(U.FORGE) and self.townhalls.amount >= 2:
                await self.build(U.FORGE, near=pylon)
        # twilight council -> charge (huge vs Zerg) / blink
        if (self.structures(U.CYBERNETICSCORE).ready and self.townhalls.amount >= 2
                and not self.structures(U.TWILIGHTCOUNCIL) and self.already_pending(U.TWILIGHTCOUNCIL) == 0
                and self.can_afford(U.TWILIGHTCOUNCIL)):
            await self.build(U.TWILIGHTCOUNCIL, near=pylon)
        # robotics bay -> colossus: splash counters a ling/hydra flood AND is a
        # heavy gas sink (Colossus = 200 gas). Build it vs Zerg, or for any race
        # once gas is floating (principle 3: spend gas, don't float).
        if ((self.enemy_race == Race.Zerg or self.vespene >= 400)
                and self.structures(U.ROBOTICSFACILITY).ready
                and not self.structures(U.ROBOTICSBAY) and self.already_pending(U.ROBOTICSBAY) == 0
                and self.townhalls.amount >= 2 and self.can_afford(U.ROBOTICSBAY)):
            await self.build(U.ROBOTICSBAY, near=pylon)
        # scale robo + stargate with GAS income (strategy_engine.production): these
        # are the gas sinks (Immortal/Colossus/Void Ray), so their count tracks the
        # gas the economy makes -- the fix for floating gas while out-mining but
        # under-arming. desired_robos/stargates already fold in splash/anti-air need.
        robos = self.structures(U.ROBOTICSFACILITY).amount + self.already_pending(U.ROBOTICSFACILITY)
        if (self.structures(U.ROBOTICSFACILITY).ready and robos < desired_robos(
                self._facility_state(), advice.composition)
                and self.already_pending(U.ROBOTICSFACILITY) == 0
                and self.can_afford(U.ROBOTICSFACILITY)):
            await self.build(U.ROBOTICSFACILITY, near=pylon)
        comp = advice.composition
        if ((comp.escalate_tech or comp.need_anti_air or self.vespene >= 300)
                and self.structures(U.CYBERNETICSCORE).ready):
            stargates = self.structures(U.STARGATE).amount + self.already_pending(U.STARGATE)
            if (stargates < desired_stargates(self._facility_state(), comp)
                    and self.already_pending(U.STARGATE) == 0
                    and self.can_afford(U.STARGATE)):
                await self.build(U.STARGATE, near=pylon)
        # scale gateways with INCOME (strategy_engine.production): add a Gateway
        # whenever the mineral income outruns current throughput, capped by bases.
        # Counting warpgates too (they ARE gateways) fixes the old bug where morphed
        # gates dropped out of the count and we over/under-built. This is what keeps
        # 'somewhere to spend' ahead of the economy so army production never idles.
        have_gates = (self.structures(U.GATEWAY).amount + self.structures(U.WARPGATE).amount
                      + self.already_pending(U.GATEWAY))
        max_pending = advice.macro.allow_parallel_build
        if (have_gates < self._desired_gateways()
                and self.already_pending(U.GATEWAY) < max_pending
                and self.can_afford(U.GATEWAY) and self.minerals > 150):
            await self.build(U.GATEWAY, near=pylon.position.towards(self.game_info.map_center, 5))

    async def _defense(self, advice):
        # The library decides how much to defend; we translate it into Protoss
        # structures. No hard-coded archetype logic here.
        plan = advice.defense
        want = plan.static_defense
        if want <= 0 and not plan.need_detection:
            return
        # Proactive (non-emergency) static defense waits until the natural is down
        # so it doesn't delay a greedy expand; a scouted rush is built immediately.
        if not plan.emergency and not plan.need_detection and self.townhalls.amount < 2:
            return
        base = self.townhalls.closest_to(self.enemy_start_locations[0]) if self.townhalls else None
        if base is None:
            return
        cannons = self.structures(U.PHOTONCANNON).amount + self.already_pending(U.PHOTONCANNON)
        batteries = self.structures(U.SHIELDBATTERY).amount + self.already_pending(U.SHIELDBATTERY)
        # Cannons are the primary hold (Forge -> up fast, no micro). Split them
        # between the mineral line (runby cover) and the ramp choke (frontal push).
        if self.structures(U.FORGE).ready and cannons < want and self.can_afford(U.PHOTONCANNON):
            pos = self._mineral_line(base) if cannons % 2 == 0 else self._choke(base)
            await self.build(U.PHOTONCANNON, near=pos)
            return
        # A couple of shield batteries sustain the wall/cannons once cyber is up.
        if (plan.emergency and self.structures(U.CYBERNETICSCORE).ready
                and batteries < 2 and self.can_afford(U.SHIELDBATTERY)):
            await self.build(U.SHIELDBATTERY, near=self._choke(base))
            return
        # detection: a cannon also detects -- cover the mineral line
        if (plan.need_detection and self.structures(U.FORGE).ready
                and cannons < want + 1 and self.can_afford(U.PHOTONCANNON)):
            await self.build(U.PHOTONCANNON, near=self._mineral_line(base))

    async def _upgrades(self):
        # Principle 10: upgrades compound -- keep upgrade structures working.
        twi = self.structures(U.TWILIGHTCOUNCIL).ready.idle
        if twi:
            up = Up.CHARGE if self.enemy_race == Race.Zerg else Up.BLINKTECH
            if self.already_pending_upgrade(up) == 0 and self.can_afford(up):
                twi.first.research(up)
        forge = self.structures(U.FORGE).ready.idle
        if not forge:
            return
        # vs Zerg (mass lings) armor first -- +1 armor turns a 5-dmg ling into 4;
        # otherwise weapons first.
        W1, A1 = Up.PROTOSSGROUNDWEAPONSLEVEL1, Up.PROTOSSGROUNDARMORSLEVEL1
        W2, A2 = Up.PROTOSSGROUNDWEAPONSLEVEL2, Up.PROTOSSGROUNDARMORSLEVEL2
        W3, A3 = Up.PROTOSSGROUNDWEAPONSLEVEL3, Up.PROTOSSGROUNDARMORSLEVEL3
        order = ((A1, W1, A2, W2, A3, W3) if self.enemy_race == Race.Zerg
                 else (W1, A1, W2, A2, W3, A3))
        for up in order:
            if self.already_pending_upgrade(up) == 0 and self.can_afford(up):
                forge.first.research(up)
                return

    async def _train(self, advice):
        # Production is DECIDED by strategy_engine.production (how many facilities to
        # add + what to build now to saturate every ready producer, resource- and
        # supply-balanced) and only EXECUTED here. This is the fix for the pro-gap:
        # we out-mine the pro but fielded a fraction of the army because production
        # sat idle -- above all, warpgates never warped (no warp-in logic existed).
        state = self._prod_state(advice)
        plan = plan_production(state, advice.composition)

        # ROBO + STARGATE: train from each idle producer, in the planned order.
        robos = list(self.structures(U.ROBOTICSFACILITY).ready.idle)
        for token, prod in zip(plan.robo_units, robos):
            uid = getattr(U, token)
            if self.can_afford(uid):
                prod.train(uid)
        stargates = list(self.structures(U.STARGATE).ready.idle)
        for token, prod in zip(plan.stargate_units, stargates):
            uid = getattr(U, token)
            if self.can_afford(uid):
                prod.train(uid)

        # GATEWAY: warp in from every off-cooldown warpgate (the army engine), and
        # train from any un-morphed idle gateway (pre-Warp-Gate).
        if not plan.gateway_units:
            return
        warpgates = self.structures(U.WARPGATE).ready
        ready_wg = []
        if warpgates:
            for wg, abils in zip(warpgates, await self.get_available_abilities(warpgates)):
                if any(a in abils for a in WARP_ABILITY.values()):
                    ready_wg.append(wg)
        gates = list(self.structures(U.GATEWAY).ready.idle)
        pylon = self._warp_pylon()
        for token in plan.gateway_units:
            uid = getattr(U, token)
            if not self.can_afford(uid):
                continue
            if ready_wg and pylon is not None:
                if await self._warp_in(ready_wg[-1], uid, pylon):
                    ready_wg.pop()
                    continue
            if gates:
                gates.pop().train(uid)

    def _prod_state(self, advice):
        """Snapshot the bot as a framework-agnostic ProductionState for the planner.

        ``minerals`` is what's *spendable on army*: when we still owe a mandated
        expansion we hide the 400 Nexus cost from the planner, so it banks toward
        the base instead of leaking it into units (the generic 'reserve via the
        resource input' trick -- no special-case hold needed)."""
        owe_base = (self.townhalls.amount + self.already_pending(U.NEXUS)
                    < advice.macro.base_target and not advice.defense.emergency)
        spendable_min = self.minerals - (400 if owe_base else 0)
        have_tech = frozenset(k for k, uid in TECH_STRUCT.items()
                              if self.structures(uid).ready)
        need_obs = (self.structures(U.ROBOTICSFACILITY).ready
                    and self.units(U.OBSERVER).amount + self.already_pending(U.OBSERVER) == 0)
        return ProductionState(
            minerals=max(0.0, spendable_min), vespene=float(self.vespene),
            mineral_income=self._income()[0], vespene_income=self._income()[1],
            supply_left=float(self.supply_left),
            bases=max(1, self.townhalls.ready.amount),
            gateways=self.structures(U.GATEWAY).amount + self.structures(U.WARPGATE).amount,
            robos=self.structures(U.ROBOTICSFACILITY).amount,
            stargates=self.structures(U.STARGATE).amount,
            ready_gateways=(self.structures(U.GATEWAY).ready.idle.amount
                            + self.structures(U.WARPGATE).ready.amount),
            ready_robos=self.structures(U.ROBOTICSFACILITY).ready.idle.amount,
            ready_stargates=self.structures(U.STARGATE).ready.idle.amount,
            have_tech=have_tech, need_observer=bool(need_obs),
        )

    def _income(self):
        """(mineral, vespene) collection rate per minute, from the game score."""
        sc = self.state.score
        return (float(getattr(sc, "collection_rate_minerals", 0)),
                float(getattr(sc, "collection_rate_vespene", 0)))

    def _facility_state(self):
        """Minimal ProductionState for the library's facility-count targets: it only
        reads income, bases, and which tech is up."""
        mi, vi = self._income()
        return ProductionState(
            0, 0, mi, vi, 0, bases=max(1, self.townhalls.ready.amount),
            gateways=0, robos=0, stargates=0, ready_gateways=0, ready_robos=0,
            ready_stargates=0,
            have_tech=frozenset(k for k, uid in TECH_STRUCT.items()
                                if self.structures(uid).ready))

    def _desired_gateways(self):
        """Income-scaled gateway target (strategy_engine.production), capped by bases."""
        return desired_gateways(self._facility_state())

    def _warp_pylon(self):
        """A powered pylon to warp near -- the one closest to our rally/front."""
        pylons = self.structures(U.PYLON).ready
        return pylons.closest_to(self._rally()) if pylons else None

    async def _warp_in(self, warpgate, uid, pylon):
        """Warp ``uid`` in at a buildable spot near ``pylon``. Returns True if issued."""
        ability = WARP_ABILITY.get(uid)
        if ability is None:
            return False
        pos = pylon.position.towards(self._rally(), 2).random_on_distance([1, 4])
        placement = await self.find_placement(ability, pos, placement_step=1)
        if placement is None:
            return False
        return bool(warpgate.warp_in(uid, placement))

    def _chrono(self):
        # Chrono technique: in the OPENING, pump probes -- accelerating the worker
        # ramp is the single biggest economic lever and is how pros hit ~150 supply
        # by 12:00. Once the economy is developed (~40 workers), shift chrono to
        # upgrades, then production. Also chrono the Cyber Core while it researches
        # (Warp Gate) -- the fastest way to online army tempo.
        early_eco = self.supply_workers < 40 and self.time < 360
        for nexus in self.townhalls.ready:
            if nexus.energy < 50:
                continue
            cyber = self.structures(U.CYBERNETICSCORE).ready
            if cyber and not cyber.first.is_idle:      # researching (warp gate) -> speed it
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, cyber.first)
                return
            if early_eco and not nexus.is_idle:        # opening: ramp probes
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                return
            forge = self.structures(U.FORGE).ready
            if forge and not forge.first.is_idle:      # then upgrades (compound)
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, forge.first)
                return
            producers = [s for s in (self.structures(U.GATEWAY).ready
                                     | self.structures(U.ROBOTICSFACILITY).ready
                                     | self.structures(U.STARGATE).ready)
                         if not s.is_idle]
            if producers:                              # then production
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, producers[0])
                return
            if not nexus.is_idle and self.supply_workers < 44:
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

    # ---------------------------------------------------------------- army -----
    def _army(self, advice):
        self._scout()
        army = self.units.of_type(ARMY)
        if not army:
            return
        tac = advice.tactics
        rally = self._rally()

        # 1) defend: enemy units in/near any base -- always respond, with micro
        threat_base = self._threatened_base()
        if threat_base is not None:
            self._defend(threat_base, army, tac, advice)
            return

        # 2) preserve: library says hold -- don't move out, rally and plug the wall
        if tac.preserve_units and not self._should_attack(advice, army):
            self._hold(army, rally)
            return

        # 3) attack or hold from the engagement read
        if self._should_attack(advice, army):
            self._push(army, tac)
        else:
            self._hold(army, rally)

    def _defend(self, threat_base, army, tac, advice):
        """Defend a base with focus-fire and kite-back micro (not pure a-move)."""
        enemies = self.enemy_units.closer_than(30, threat_base)
        for u in army:
            # kite badly damaged units back to the base to preserve them
            if tac.kite_low_hp and self._low_hp(u, tac.retreat_threshold):
                u.move(threat_base.position)
                continue
            if tac.focus_fire and enemies:
                tgt = self._select_target(u, enemies, tac.target_priority)
                if tgt is not None:
                    u.attack(tgt)
                    continue
            # fall back to attacking the closest threat position
            tpos = (enemies.closest_to(threat_base).position if enemies
                    else threat_base.position)
            u.attack(tpos)
        # pull workers to hold when the base is breached and we're thin
        no_defense = (self.structures(U.PHOTONCANNON).ready.amount == 0
                      and self.supply_army < 6)
        if enemies and (advice.defense.pull_workers
                        or (advice.defense.emergency and no_defense)):
            tpos = enemies.closest_to(threat_base).position if enemies else threat_base.position
            self._pull_workers(threat_base, tpos)

    def _push(self, army, tac):
        """Concentrate into a ball, then commit with focus-fire micro.

        Feeding units piecemeal into the enemy is how even-favorable fights get
        lost -- the library's tactics plan says gather first, then commit. Once
        committed, focus-fire on specific targets to drop enemy DPS fast, and kite
        back damaged units to preserve value.
        """
        staging = self._staging()
        center = army.center
        concentrated = army.closer_than(11, center).amount >= tac.commit_ratio * army.amount
        # Gather into a ball first, but commit outright with overwhelming force.
        if concentrated or self.supply_army >= 55:
            target = self._attack_target(army)
            nearby = self.enemy_units.closer_than(18, center) if self.enemy_units else None
            for u in army:
                # kite low-hp units back toward staging to preserve them
                if tac.kite_low_hp and self._low_hp(u, tac.retreat_threshold):
                    u.move(staging)
                    continue
                # focus fire on a specific target when enemies are visible
                if tac.focus_fire and nearby:
                    tgt = self._select_target(u, nearby, tac.target_priority)
                    if tgt is not None:
                        u.attack(tgt)
                        continue
                u.attack(target)
        else:
            for u in army:
                u.move(staging)

    def _hold(self, army, rally):
        """Hold at the rally: plug the ramp wall gap, gather the rest at rally."""
        hold = self._wall_hold()
        plug = None
        if hold is not None and self._wall_gap_open() and army:
            plug = army.closest_to(hold)
            plug.attack(hold)
        for u in army:
            if plug is not None and u.tag == plug.tag:
                continue
            if u.distance_to(rally) > 8:
                u.move(rally)

    def _select_target(self, unit, enemies, priority):
        """Pick a target for focus-fire based on the library's target_priority."""
        if priority == "expensive":
            # target the highest-supply enemy (proxy for cost/value)
            return max(enemies, key=lambda e: ARMY_SUPPLY.get(e.type_id, 1))
        if priority == "air":
            air = enemies.of_type(AIR_ENEMY_UNITS)
            if air:
                return air.closest_to(unit)
            return enemies.closest_to(unit)
        # "closest" (default) -- kill the nearest unit to reduce surround DPS
        return enemies.closest_to(unit)

    def _low_hp(self, u, threshold):
        """Effective health fraction: (shield + hp) / (shield_max + hp_max)."""
        total = getattr(u, "shield", 0) + getattr(u, "health", 0)
        total_max = getattr(u, "shield_max", 0) + getattr(u, "health_max", 0)
        if total_max <= 0:
            return False
        return (total / total_max) < threshold

    def _staging(self):
        """Forward staging point: gather here before committing the attack."""
        if self.townhalls:
            base = self.townhalls.closest_to(self.enemy_start_locations[0])
            return base.position.towards(self.enemy_start_locations[0], 14)
        return self.start_location

    def _should_attack(self, advice, army):
        # Trust the library's engagement read: it already folds army ratio, the
        # upgrade edge, and composition into one verdict. Overriding it with raw
        # supply thresholds ("attack at 35 supply / at max") is what made the bot
        # feed -- it out-PRODUCED the enemy 1.78x yet its army on the field stayed
        # at 0.4x, because it threw every batch into a losing fight. Commit only
        # when the fight is favorable; otherwise hold and let production accumulate
        # into an actual field lead.
        eng = advice.engagement.verdict
        if advice.defense.hold_position:               # library says hold at home
            return False
        if eng == Engagement.ENGAGE:                   # favorable -- take the fight
            return True
        if eng in (Engagement.AVOID, Engagement.DEFEND):
            return False                               # behind/even -- don't feed
        # UNKNOWN (enemy army not scouted): don't sit floating a maxed army.
        if self.supply_used >= 190:
            return True
        return False

    def _attack_target(self, army):
        if self.enemy_structures:
            return self.enemy_structures.closest_to(army.center).position
        if self.enemy_units:
            return self.enemy_units.closest_to(self.start_location).position
        return self.enemy_start_locations[0]

    def _rally(self):
        hold = self._wall_hold()
        if hold is not None and self.townhalls.amount <= 1:
            return hold
        if self.townhalls:
            base = self.townhalls.closest_to(self.enemy_start_locations[0])
            return base.position.towards(self.game_info.map_center, 8)
        return self.start_location

    def _threatened_base(self):
        for th in self.townhalls:
            if self.enemy_units.filter(lambda u: u.can_attack and u.distance_to(th) < 30):
                return th
        return None

    def _pull_workers(self, base, target):
        # pull a portion of probes at the breached base; leave a few mining
        probes = self.workers.closer_than(20, base)
        n_fight = max(0, probes.amount - 4)
        for probe in probes[:n_fight]:
            probe.attack(target)

    def _scout(self):
        # Principle 5: scout constantly -- one early probe reveals the opening
        if not self.scout_sent and self.time > 20 and self.workers.amount > 12:
            probe = self.workers.random
            probe.move(self.enemy_start_locations[0])
            self.scout_tag = probe.tag
            self.scout_sent = True
        if self.scout_tag is not None:
            scout = self.workers.find_by_tag(self.scout_tag)
            if scout and scout.is_idle:
                scout.move(self.enemy_start_locations[0])

    # --------------------------------------------------------- wall + placement
    def _wall_layout(self):
        if self._wall is not None:
            return self._wall
        try:
            ramp = self.main_base_ramp
            pylon = ramp.protoss_wall_pylon
            builds = sorted(ramp.protoss_wall_buildings, key=lambda p: (round(p.x), round(p.y)))
            hold = ramp.protoss_wall_warpin
            self._wall = (pylon, builds, hold) if (pylon is not None and len(builds) >= 2) else (None, [], None)
        except Exception:
            self._wall = (None, [], None)
        return self._wall

    def _wall_pylon(self):
        return self._wall_layout()[0]

    def _wall_building(self, i):
        builds = self._wall_layout()[1]
        return builds[i] if len(builds) > i else None

    def _wall_hold(self):
        return self._wall_layout()[2]

    def _wall_gap_open(self):
        pylon, builds, _ = self._wall_layout()
        if pylon is None:
            return False
        placed = sum(
            1 for p in builds
            if self.structures.of_type({U.GATEWAY, U.CYBERNETICSCORE, U.FORGE})
            .closer_than(1.5, p))
        return placed < len(builds)

    def _mineral_line(self, base):
        mins = self.mineral_field.closer_than(10, base)
        if mins:
            return base.position.towards(mins.center, 4)
        return base.position.towards(self.game_info.map_center, -3)

    def _choke(self, base):
        try:
            return self.main_base_ramp.top_center.towards(base.position, 3)
        except Exception:
            return base.position.towards(self.game_info.map_center, 6)

    # ------------------------------------------------------------------ log ----
    def _log(self, advice):
        if self.time - self.last_log < 60:
            return
        self.last_log = self.time
        m = advice.macro
        t = advice.tactics
        print(f"[{int(self.time)}s] {advice.summary().splitlines()[0]} | "
              f"opp={advice.classification.archetype.value} "
              f"opening={self.enemy_opening or '?'} "
              f"counter={advice.counter.posture} "
              f"workers={self.supply_workers} army={int(self.supply_army)} "
              f"bases={self.townhalls.amount} "
              f"prod={m.target_production}(urg={m.spend_urgency:.1f}"
              f"{'!' if m.force_train else ''}) "
              f"tac={'ff' if t.focus_fire else '--'}"
              f"/{'kite' if t.kite_low_hp else '--'}"
              f"/{t.target_priority}"
              f"{'/preserve' if t.preserve_units else ''}")
