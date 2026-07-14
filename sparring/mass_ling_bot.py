"""MassLingBot: a scripted mimic of a mass-zergling macro opponent.

A "sparring partner" you can run your bot against to reproduce losses to a
Zerg mass-ling macro style -- no opponent source code needed. Built from a real
replay (see analysis/extract_build_order.py -- the "Lissy" game that beat
lishimin):

    Hatch, Pool ~1:45, ling speed ~4:51, expand to 3-4 bases, queens + injects,
    mass Zergling (288 lings!) with a Roach/Hydra backbone, +weapon/armor
    upgrades, remax and attack in waves.

Reproduces the *economy shape, composition, and macro cadence* -- drone up,
inject, mass ling, attack. Not the original's exact engagement micro.

Validated headless (sparring/run.py --bot massling, real SC2 client): Pool ~1:15,
4 hatcheries, queens + injects, evo chamber, ~266 zerglings on ~75 drones, then
attacks -- matching the source (288 lings on 4 bases). It drones to saturation
before flooding lings (first ling ~7:00), so the ling pressure arrives later than
the source's ~3:18; tune DRONES_PER_BASE / ATTACK_SUPPLY for earlier aggression.

Run via sparring/run.py --bot massling.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId


class MassLingBot(BotAI):
    TARGET_BASES = 4
    DRONES_PER_BASE = 18
    MAX_DRONES = 66
    ATTACK_SUPPLY = 60          # push once army supply reaches this, then keep going

    async def on_start(self):
        self.attacking = False

    async def on_step(self, iteration):
        if not self.townhalls:
            for ling in self.units(UnitTypeId.ZERGLING):
                ling.attack(self.enemy_start_locations[0])
            return

        await self.inject_larva()
        await self.build_overlords()
        await self.build_queens()
        await self.build_pool_and_speed()
        await self.expand()
        await self.build_drones()
        await self.build_lings()
        await self.upgrades()
        await self.attack()

    # --- queen injects: the engine of Zerg larva economy --------------------
    async def inject_larva(self):
        for queen in self.units(UnitTypeId.QUEEN).idle:
            if queen.energy < 25:
                continue
            hall = self.townhalls.ready.closest_to(queen)
            if hall and not hall.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                queen(AbilityId.EFFECT_INJECTLARVA, hall)

    # --- supply: never get blocked ------------------------------------------
    async def build_overlords(self):
        if (
            self.supply_left < 4
            and self.supply_cap < 200
            and self.already_pending(UnitTypeId.OVERLORD) < 2
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.larva
        ):
            self.larva.first.train(UnitTypeId.OVERLORD)

    # --- one queen per hatchery for injects ---------------------------------
    async def build_queens(self):
        if not self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            return
        want = min(self.townhalls.amount, 5)
        have = self.units(UnitTypeId.QUEEN).amount + self.already_pending(UnitTypeId.QUEEN)
        if have < want:
            hall = self.townhalls.ready.idle
            if hall and self.can_afford(UnitTypeId.QUEEN):
                hall.first.train(UnitTypeId.QUEEN)

    # --- spawning pool + zergling speed -------------------------------------
    async def build_pool_and_speed(self):
        if (
            not self.structures(UnitTypeId.SPAWNINGPOOL)
            and self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0
            and self.can_afford(UnitTypeId.SPAWNINGPOOL)
        ):
            await self.build(UnitTypeId.SPAWNINGPOOL, near=self.townhalls.first.position.towards(self.game_info.map_center, 5))
            return
        pool = self.structures(UnitTypeId.SPAWNINGPOOL).ready
        if pool and self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0:
            if self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
                # need a gas for speed
                if self.vespene >= 100:
                    self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
                else:
                    await self.build_gas()

    async def build_gas(self):
        if self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) >= 1:
            return
        for th in self.townhalls.ready:
            geyser = self.vespene_geyser.closer_than(10, th).first if self.vespene_geyser.closer_than(10, th) else None
            if geyser and self.can_afford(UnitTypeId.EXTRACTOR):
                worker = self.select_build_worker(geyser.position)
                if worker:
                    worker.build_gas(geyser)
                return

    # --- expand to TARGET_BASES ---------------------------------------------
    async def expand(self):
        if (
            self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) < self.TARGET_BASES
            and self.can_afford(UnitTypeId.HATCHERY)
        ):
            await self.expand_now()

    # --- drones up to saturation --------------------------------------------
    async def build_drones(self):
        want = min(self.MAX_DRONES, self.DRONES_PER_BASE * self.townhalls.amount)
        if self.supply_workers >= want or not self.larva:
            return
        # Don't starve the pool/expansions; drone with spare larva.
        if self.can_afford(UnitTypeId.DRONE):
            self.larva.first.train(UnitTypeId.DRONE)

    # --- mass zerglings from all spare larva --------------------------------
    async def build_lings(self):
        if not self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            return
        for larva in self.larva:
            if self.can_afford(UnitTypeId.ZERGLING) and self.supply_left > 0:
                larva.train(UnitTypeId.ZERGLING)

    # --- ground weapon/armor upgrades ---------------------------------------
    async def upgrades(self):
        if self.townhalls.amount < 3:
            return
        if (
            not self.structures(UnitTypeId.EVOLUTIONCHAMBER)
            and self.already_pending(UnitTypeId.EVOLUTIONCHAMBER) == 0
            and self.can_afford(UnitTypeId.EVOLUTIONCHAMBER)
        ):
            await self.build(UnitTypeId.EVOLUTIONCHAMBER, near=self.townhalls.first.position.towards(self.game_info.map_center, 5))
            return
        for evo in self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready.idle:
            for up in (UpgradeId.ZERGMELEEWEAPONSLEVEL1, UpgradeId.ZERGGROUNDARMORSLEVEL1):
                if self.already_pending_upgrade(up) == 0 and self.can_afford(up):
                    self.research(up)
                    break

    # --- attack in waves once we have a critical mass -----------------------
    async def attack(self):
        lings = self.units(UnitTypeId.ZERGLING)
        army_supply = self.supply_used - self.supply_workers
        if not self.attacking and army_supply >= self.ATTACK_SUPPLY:
            self.attacking = True
        if self.attacking and lings:
            target = (
                self.enemy_structures.random.position
                if self.enemy_structures
                else self.enemy_start_locations[0]
            )
            for ling in lings:
                ling.attack(target)

    async def on_end(self, result: Result):
        print(f"MassLingBot game ended: {result}")
