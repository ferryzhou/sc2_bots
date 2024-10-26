from sc2.bot_ai import BotAI
from sc2.data import Result

import random

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer

class MultiPylonBot(BotAI):

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    async def on_end(self, game_result: Result):
        print("Game ended.")
        # Do things here after the game ends

    # pylint: disable=R0912
    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(probe)(pylon)(gg)")

        if not self.townhalls:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn
            # (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return

        nexus = self.townhalls.random

        # Make probes until we have 16 total
        if self.supply_workers < 16 and nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
                return

        # If we have no pylon, build one near starting nexus
        if not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)
                return

        # If we have less than 2 pylons, build one at next expansion location
        if self.structures(UnitTypeId.PYLON).amount < 2:
            if self.can_afford(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) < 2:
                location = await self.get_next_expansion()
                await self.build(UnitTypeId.PYLON, near=location)
                return

