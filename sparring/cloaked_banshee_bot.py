"""CloakedBansheeBot: a scripted 1-base Terran cloaked-Banshee rush bot (the Hestia/cloak testbed).

Reproduces the zero-detection failure seen in the 2026-08-22 Hestia ladder loss
(and Lissy burrowed Lurkers): without an Observer or Photon Cannon, PhoenixBot
cannot attack cloaked Banshees at all and loses its mineral lines and army
while floating resources.

1-base fast Starport + TechLab + Banshee Cloak (~4:00), holding the main ramp
with Marines + a Bunker so the Banshees always reach Phoenix's bases.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as UP


class CloakedBansheeBot(BotAI):
    TARGET_SCVS = 22
    N_STARPORTS = 2

    async def on_step(self, it):
        if not self.townhalls:
            for u in self.units.of_type({U.BANSHEE, U.MARINE}):
                u.attack(self.enemy_start_locations[0])
            return
        await self.distribute_workers()
        cc = self.townhalls.first
        await self.depots(cc)
        await self.gas(cc)
        await self.tech(cc)
        await self.scvs()
        await self.train()
        await self.micro()

    async def depots(self, cc):
        if (self.supply_left < 5 and self.supply_cap < 200
                and self.already_pending(U.SUPPLYDEPOT) < 2
                and self.can_afford(U.SUPPLYDEPOT)):
            await self.build(
                U.SUPPLYDEPOT,
                near=cc.position.towards(self.game_info.map_center, 5),
            )

    async def gas(self, cc):
        if self.time < 20:
            return
        want = 2
        if self.gas_buildings.amount + self.already_pending(U.REFINERY) >= want:
            return
        if not self.can_afford(U.REFINERY):
            return
        for g in self.vespene_geyser.closer_than(10, cc):
            if not self.gas_buildings.closer_than(1, g):
                w = self.select_build_worker(g.position)
                if w:
                    w.build_gas(g)
                    return

    async def tech(self, cc):
        if not self.structures(U.SUPPLYDEPOT).ready:
            return
        pos = cc.position.towards(self.game_info.map_center, 4)
        if (self.structures(U.BARRACKS).amount + self.already_pending(U.BARRACKS) < 1
                and self.can_afford(U.BARRACKS)):
            await self.build(U.BARRACKS, near=pos)
        if (self.structures(U.BARRACKS).ready
                and self.structures(U.BUNKER).amount + self.already_pending(U.BUNKER) < 1
                and self.can_afford(U.BUNKER)):
            await self.build(
                U.BUNKER,
                near=self.main_base_ramp.top_center.towards(cc.position, 4),
            )
        if (self.structures(U.BARRACKS).ready
                and not self.structures(U.FACTORY)
                and not self.already_pending(U.FACTORY)
                and self.can_afford(U.FACTORY)):
            await self.build(U.FACTORY, near=pos)
        if (self.structures(U.FACTORY).ready
                and self.structures(U.STARPORT).amount
                + self.already_pending(U.STARPORT) < self.N_STARPORTS
                and self.can_afford(U.STARPORT)):
            await self.build(U.STARPORT, near=cc.position.towards(self.game_info.map_center, 2))
        for sp in self.structures(U.STARPORT).ready.idle:
            if not sp.has_add_on and self.can_afford(U.STARPORTTECHLAB):
                sp.build(U.STARPORTTECHLAB)
        for tl in self.structures(U.STARPORTTECHLAB).ready.idle:
            if (UP.BANSHEECLOAK not in self.state.upgrades
                    and not self.already_pending_upgrade(UP.BANSHEECLOAK)
                    and self.can_afford(UP.BANSHEECLOAK)):
                tl.research(UP.BANSHEECLOAK)

    async def scvs(self):
        if self.supply_workers >= self.TARGET_SCVS:
            return
        for cc in self.townhalls.ready.idle:
            if self.can_afford(U.SCV) and self.supply_left > 0:
                cc.train(U.SCV)

    async def train(self):
        for sp in self.structures(U.STARPORT).ready.idle:
            if sp.has_techlab and self.can_afford(U.BANSHEE) and self.supply_left >= 3:
                sp.train(U.BANSHEE)
        for rax in self.structures(U.BARRACKS).ready.idle:
            if self.units(U.MARINE).amount < 8 and self.can_afford(U.MARINE) and self.supply_left >= 1:
                rax.train(U.MARINE)

    async def micro(self):
        home = self.main_base_ramp.top_center
        bunkers = self.structures(U.BUNKER).ready
        enemies_near_home = self.enemy_units.closer_than(24, self.start_location)
        for m in self.units(U.MARINE):
            if bunkers and bunkers.first.cargo_left > 0 and m.distance_to(bunkers.first) < 12:
                m.smart(bunkers.first)
            elif enemies_near_home:
                m.attack(enemies_near_home.closest_to(m))
            elif m.distance_to(home) > 5:
                m.attack(home)

        cloak_ready = UP.BANSHEECLOAK in self.state.upgrades
        banshees = self.units(U.BANSHEE)
        if not banshees:
            return
        for b in banshees:
            if not cloak_ready:
                if b.distance_to(home) > 7:
                    b.move(home)
                continue
            near = self.enemy_units.closer_than(12, b)
            if near and not b.has_buff(BuffId.BANSHEECLOAK) and b.energy >= 25:
                b(AbilityId.BEHAVIOR_CLOAKON_BANSHEE)
            workers = self.enemy_units.of_type({U.PROBE, U.SCV, U.DRONE})
            if workers:
                b.attack(workers.closest_to(b))
            elif self.enemy_units:
                b.attack(self.enemy_units.closest_to(b))
            elif self.enemy_structures:
                b.attack(self.enemy_structures.closest_to(b).position)
            else:
                b.attack(self.enemy_start_locations[0])

    async def on_end(self, result: Result):
        print(f"CloakedBansheeBot game ended: {result}")
