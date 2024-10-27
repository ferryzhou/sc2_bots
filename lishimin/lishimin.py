from sc2.bot_ai import BotAI
from sc2.data import Result

import random

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit

class LiShiMinBot(BotAI):

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    async def on_end(self, game_result: Result):
        print("Game ended.")
        # Do things here after the game ends

    # pylint: disable=R0912
    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(probe)(pylon)(cannon)(cannon)(gg)")

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

        # If we have no forge, build one near the pylon that is closest to our starting nexus
        if not self.structures(UnitTypeId.FORGE):
            pylon_ready = self.structures(UnitTypeId.PYLON).ready
            if pylon_ready:
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near=pylon_ready.closest_to(nexus))
                    return

        # If we have less than 2 pylons, build one at the enemy base
        if self.structures(UnitTypeId.PYLON).amount < 2:
            if self.can_afford(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) < 2:
                pos = self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 15))
                await self.build(UnitTypeId.PYLON, near=pos)
                return

        # If we have no cannons but at least 2 completed pylons, automatically find a placement location
        # and build them near enemy start location
        if not self.structures(UnitTypeId.PHOTONCANNON):
            if self.structures(UnitTypeId.PYLON).ready.amount >= 2 and self.can_afford(UnitTypeId.PHOTONCANNON):
                pylon = self.structures(UnitTypeId.PYLON).closer_than(20, self.enemy_start_locations[0]).random
                await self.build(UnitTypeId.PHOTONCANNON, near=pylon)
                return

        # If we have more than 5 cannons, build them (up to 3) at random location near our nexus to defend
        if (self.structures(UnitTypeId.PHOTONCANNON).amount > 5):
            if self.can_afford(UnitTypeId.PHOTONCANNON) and self.structures(UnitTypeId.PHOTONCANNON).closer_than(20, nexus).amount < 3:
                await self.build(UnitTypeId.PHOTONCANNON, near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
                return

        # Decide if we should make pylon or cannons, then build them at random location near enemy spawn
        if self.can_afford(UnitTypeId.PYLON) and self.can_afford(UnitTypeId.PHOTONCANNON):
            # Ensure "fair" decision
            for _ in range(20):
                pos = self.find_best_location_to_attack().random_on_distance(random.randrange(5, 12))
                building = UnitTypeId.PHOTONCANNON if self.state.psionic_matrix.covers(pos) else UnitTypeId.PYLON
                await self.build(building, near=pos)


    def find_best_location_to_attack(self) -> Point2:
        # Return the best location to build pylon and cannon to attack. 
        # Starting with start location, then closest to enemy nexus, then visible enemy buildings
        if not self.enemy_structures:
            # Didn't see any enemy structures, so build near start location
            #print("no enemy structures")
            # Cap max cannons near start location at 20.
            if (self.structures(UnitTypeId.PHOTONCANNON).closer_than(20, self.enemy_start_locations[0]).amount < 20):
                return self.enemy_start_locations[0]
            else:
                #print("too many cannons near start location")
                return self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 35))
            
        #print("enemy structure found")
        if self.enemy_structures(UnitTypeId.NEXUS):
            #print("enemy nexus found, attack nexus first")
            return self.enemy_structures(UnitTypeId.NEXUS)[0].position
        else:
            #print("other enemy structure found, attack structure")
            return self.enemy_structures[0].position
