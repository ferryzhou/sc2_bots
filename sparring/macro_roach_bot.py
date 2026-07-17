"""MacroRoachBot: a scripted mimic of a macro roach/ling Zerg (Lissy/Persephone).

A sparring partner to reproduce the *late-game* loss where we lead mid-game then
get army-wiped and out-remaxed. Build from Persephone's replay
(analysis/extract_build_order.py <replay> 2):

    3-hatch macro, SpawningPool ~2:00, gas, RoachWarren ~5:00, drone HARD
    (~100 drones), Zerglings early, mass Roach from ~7:00, remax off a huge
    economy, Hydralisk late. Queens inject for extra larva.

Unlike an all-in, the point here is ECONOMY + REMAX: it keeps droning, keeps
expanding, and rebuilds its roach army faster than we can after each fight.
Not a clone of the original's micro -- a faithful macro archetype to test our
late-game staying power against.

Tunables: DRONE_CAP, ATTACK_SUPPLY, MAX_HATCH.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId


class MacroRoachBot(BotAI):
    DRONE_CAP = 60          # drone hard, then pour larva into roaches
    ATTACK_SUPPLY = 60      # attack once the roach army is big, then remax
    MAX_HATCH = 4

    async def on_start(self):
        self.attacking = False

    async def on_step(self, iteration):
        if not self.townhalls:
            for u in self.units.of_type({UnitTypeId.ROACH, UnitTypeId.ZERGLING}):
                u.attack(self.enemy_start_locations[0])
            return

        await self.distribute_workers()
        await self.build_overlords()
        await self.build_pool()
        await self.build_gas()
        await self.build_queens_and_inject()
        await self.expand()
        await self.build_roach_warren()
        await self.make_units()
        await self.attack()

    @property
    def _hatches(self) -> int:
        return self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY)

    async def build_overlords(self):
        if (
            self.supply_left < 4
            and self.supply_cap < 200
            and self.already_pending(UnitTypeId.OVERLORD) < 2
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.larva
        ):
            self.larva.random.train(UnitTypeId.OVERLORD)

    async def build_pool(self):
        if (
            not self.structures(UnitTypeId.SPAWNINGPOOL)
            and not self.already_pending(UnitTypeId.SPAWNINGPOOL)
            and self.can_afford(UnitTypeId.SPAWNINGPOOL)
        ):
            await self.build(
                UnitTypeId.SPAWNINGPOOL,
                near=self.townhalls.first.position.towards(self.game_info.map_center, 5),
            )

    async def build_gas(self):
        # 1 extractor once pool is down, a 2nd once roach warren is up
        want = 1 if not self.structures(UnitTypeId.ROACHWARREN).ready else 3
        have = self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR)
        if have >= want or self.time < 90 or not self.can_afford(UnitTypeId.EXTRACTOR):
            return
        for th in self.townhalls.ready:
            for geyser in self.vespene_geyser.closer_than(10, th):
                if not self.gas_buildings.closer_than(1, geyser):
                    worker = self.select_build_worker(geyser.position)
                    if worker:
                        worker.build_gas(geyser)
                        return

    async def build_queens_and_inject(self):
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if (
                self.units(UnitTypeId.QUEEN).amount + self.already_pending(UnitTypeId.QUEEN)
                < min(self.townhalls.amount, 4)
                and self.can_afford(UnitTypeId.QUEEN)
            ):
                th = self.townhalls.idle.first if self.townhalls.idle else None
                if th:
                    th.train(UnitTypeId.QUEEN)
        # inject
        for queen in self.units(UnitTypeId.QUEEN).idle:
            if queen.energy >= 25:
                th = self.townhalls.closest_to(queen)
                if th and not th.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                    queen(AbilityId.EFFECT_INJECTLARVA, th)

    async def expand(self):
        if (
            self._hatches < self.MAX_HATCH
            and self.can_afford(UnitTypeId.HATCHERY)
            and self.already_pending(UnitTypeId.HATCHERY) < 1
        ):
            await self.expand_now()

    async def build_roach_warren(self):
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).ready
            and not self.structures(UnitTypeId.ROACHWARREN)
            and not self.already_pending(UnitTypeId.ROACHWARREN)
            and self.time > 180
            and self.can_afford(UnitTypeId.ROACHWARREN)
        ):
            await self.build(
                UnitTypeId.ROACHWARREN,
                near=self.townhalls.first.position.towards(self.game_info.map_center, 5),
            )

    async def make_units(self):
        if not self.larva:
            return
        # early: a few lings for presence/defense off the pool
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).ready
            and self.units(UnitTypeId.ZERGLING).amount < 6
            and self.supply_workers > 14
            and self.can_afford(UnitTypeId.ZERGLING)
        ):
            self.larva.random.train(UnitTypeId.ZERGLING)
            return
        # drone hard until the cap
        if (
            self.supply_workers < self.DRONE_CAP
            and self.can_afford(UnitTypeId.DRONE)
            and self.supply_left > 0
        ):
            self.larva.random.train(UnitTypeId.DRONE)
            return
        # then pour everything into roaches (remax fuel)
        if (
            self.structures(UnitTypeId.ROACHWARREN).ready
            and self.can_afford(UnitTypeId.ROACH)
        ):
            self.larva.random.train(UnitTypeId.ROACH)

    async def attack(self):
        roaches = self.units(UnitTypeId.ROACH)
        army = roaches + self.units(UnitTypeId.ZERGLING)
        if not self.attacking and self.get_total_supply(roaches) >= self.ATTACK_SUPPLY:
            self.attacking = True
        # once committed, keep attacking while we have a real army; fall back
        # to re-massing if the army is spent (remax, then re-engage)
        if self.attacking:
            if self.get_total_supply(roaches) < 20:
                self.attacking = False
                return
            target = (
                self.enemy_structures.random.position
                if self.enemy_structures
                else self.enemy_start_locations[0]
            )
            for u in army:
                u.attack(target)

    async def on_end(self, result: Result):
        print(f"MacroRoachBot game ended: {result}")
