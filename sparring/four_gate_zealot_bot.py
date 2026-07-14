"""FourGateZealotBot: a scripted mimic of a 4-gate zealot all-in.

A "sparring partner" you can run your own bot against to reproduce losses to this
opening -- no opponent source code needed. The build is taken directly from a
real replay (see analysis/extract_build_order.py):

    Nexus, Pylon @13, Pylon @15, 4x Gateway (1:35-2:01), NO gas, mass Zealot,
    warp-in pylons pushed forward, ~18 probes then all-in. First Zealot ~3:18.

This reproduces the *build, composition, and timing* of the all-in faithfully.
It does not reproduce the original bot's exact micro -- for a scripted all-in
that is ~90% of the behavior, which is plenty to test defenses against.

Run it via sparring/run.py.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2


class FourGateZealotBot(BotAI):
    # Tunables (mirroring the extracted build order).
    TARGET_PROBES = 18          # opponent stalled ~18 workers -- committed all-in
    NUM_GATEWAYS = 4
    ATTACK_AT_ZEALOTS = 4       # push once this many zealots exist, then never stop

    async def on_start(self):
        self.attacking = False

    async def on_step(self, iteration):
        if not self.townhalls:
            # No base left -- throw everything at the enemy.
            for unit in self.units.of_type({UnitTypeId.ZEALOT, UnitTypeId.PROBE}):
                unit.attack(self.enemy_start_locations[0])
            return

        nexus = self.townhalls.first

        await self.build_economy(nexus)
        await self.build_gateways(nexus)
        await self.research_warpgate()
        await self.make_zealots(nexus)
        await self.chrono(nexus)
        await self.attack()

    # --- economy: probes to the cap, pylons ahead of supply -----------------
    async def build_economy(self, nexus):
        if self.supply_workers < self.TARGET_PROBES and nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

        # Keep supply ahead; pylons double as forward warp-in points later.
        if (
            self.supply_left < 3
            and self.already_pending(UnitTypeId.PYLON) < 2
            and self.can_afford(UnitTypeId.PYLON)
        ):
            await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.game_info.map_center, 6))

    # --- 4 gateways ASAP ----------------------------------------------------
    async def build_gateways(self, nexus):
        if not self.structures(UnitTypeId.PYLON).ready:
            if not self.already_pending(UnitTypeId.PYLON) and self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.game_info.map_center, 6))
            return
        gates = self.structures.of_type({UnitTypeId.GATEWAY, UnitTypeId.WARPGATE})
        pending = self.already_pending(UnitTypeId.GATEWAY)
        if gates.amount + pending < self.NUM_GATEWAYS and self.can_afford(UnitTypeId.GATEWAY):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon.position.towards(self.game_info.map_center, 4))

    # --- warpgate (for the reinforcing warp-in surge) -----------------------
    async def research_warpgate(self):
        # Needs a cybernetics core; the pure-gate replay warped in off a fast core.
        if not self.structures(UnitTypeId.CYBERNETICSCORE):
            if (
                self.structures(UnitTypeId.PYLON).ready
                and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                and self.can_afford(UnitTypeId.CYBERNETICSCORE)
            ):
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            return
        core = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        if core and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0:
            if self.can_afford(UpgradeId.WARPGATERESEARCH):
                core.first.research(UpgradeId.WARPGATERESEARCH)

    # --- mass zealot: train from gateways, warp in from warpgates -----------
    async def make_zealots(self, nexus):
        # Gateways (pre-warpgate): straight train.
        for gate in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.can_afford(UnitTypeId.ZEALOT):
                gate.train(UnitTypeId.ZEALOT)

        # Warpgates: warp in near the most-forward pylon (toward the enemy).
        warpgates = self.structures(UnitTypeId.WARPGATE).ready
        if not warpgates:
            return
        pylons = self.structures(UnitTypeId.PYLON).ready
        if not pylons:
            return
        target_pylon = pylons.closest_to(self.enemy_start_locations[0])
        for wg in warpgates:
            abilities = await self.get_available_abilities(wg)
            if AbilityId.WARPGATETRAIN_ZEALOT not in abilities:
                continue
            if not self.can_afford(UnitTypeId.ZEALOT):
                break
            pos = target_pylon.position.to2.random_on_distance(4)
            placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, pos, placement_step=1)
            if placement:
                wg.warp_in(UnitTypeId.ZEALOT, placement)

    # --- chrono: warpgate research first, then a producing gateway ----------
    async def chrono(self, nexus):
        if nexus.energy < 50:
            return
        # Prioritize warpgate research while it is in progress.
        core = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        if core and 0.0 < self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) < 1.0:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, core.first)
            return
        # Otherwise speed up a gateway that is training.
        busy = [g for g in self.structures(UnitTypeId.GATEWAY).ready if not g.is_idle]
        if busy:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])

    # --- all-in: once we have a few zealots, attack and never stop ----------
    async def attack(self):
        zealots = self.units(UnitTypeId.ZEALOT)
        if not self.attacking and zealots.amount >= self.ATTACK_AT_ZEALOTS:
            self.attacking = True
        if self.attacking:
            target = self.enemy_structures.random.position if self.enemy_structures \
                else self.enemy_start_locations[0]
            for z in zealots:
                z.attack(target)

    async def on_end(self, result: Result):
        print(f"FourGateZealotBot game ended: {result}")
