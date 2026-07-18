"""TwelvePoolBot: a fast 12-pool zergling rush (mimics 12PoolBot's timing).

Sparring partner to test anti-rush defense. ~12 drones -> Spawning Pool ->
mass Zerglings -> all-in.

Validated headless vs the VeryHard built-in AI: pool starts 0:39 on 14 drones,
first lings 2:08 (pool morph alone is ~46s, so earlier isn't physically
possible), 44 lings by 5:00 attacking in waves.
"""
from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId as U


class TwelvePoolBot(BotAI):
    async def on_step(self, iteration):
        if not self.townhalls:
            for ling in self.units(U.ZERGLING):
                ling.attack(self.enemy_start_locations[0])
            return
        hatch = self.townhalls.first

        # drones to 13, then pool
        if (not self.structures(U.SPAWNINGPOOL) and self.already_pending(U.SPAWNINGPOOL) == 0):
            if self.supply_workers < 13 and self.larva and self.can_afford(U.DRONE):
                self.larva.first.train(U.DRONE)
            elif self.can_afford(U.SPAWNINGPOOL):
                await self.build(U.SPAWNINGPOOL, near=hatch.position.towards(self.game_info.map_center, 5))
            return

        # overlords so we don't block
        if (self.supply_left < 2 and self.already_pending(U.OVERLORD) < 2
                and self.can_afford(U.OVERLORD) and self.larva):
            self.larva.first.train(U.OVERLORD)

        # mass zerglings from every larva
        if self.structures(U.SPAWNINGPOOL).ready:
            for larva in self.larva:
                if self.can_afford(U.ZERGLING) and self.supply_left > 0:
                    larva.train(U.ZERGLING)

        lings = self.units(U.ZERGLING)
        if lings.amount >= 6:
            target = (self.enemy_structures.random.position if self.enemy_structures
                      else self.enemy_start_locations[0])
            for ling in lings:
                ling.attack(target)

    async def on_end(self, result: Result):
        print(f"TwelvePoolBot game ended: {result}")
