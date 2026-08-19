"""VoidRayBot: a scripted mass Void Ray Protoss (the Arpy pattern).

Reproduces the 26-min Arpy ladder loss: 42 Void Rays ground Phoenix down while
Phoenix teched immortals + colossus -- neither can shoot up, so every robo
mineral was wasted. Void rays are the most scriptable air composition (no micro
needed: they charge up in combat and a-move well), which makes this the
verification testbed for the anti-air comp guard: vs this bot Phoenix should
stay on pure stalkers (its only scalable AA) and skip robo splash entirely.

2-base economy, 3 stargates, waves of void rays with continuous reinforcement.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U


class VoidRayBot(BotAI):
    TARGET_PROBES = 44
    N_STARGATES = 3
    ATTACK_AT_VOIDS = 6      # push in waves, keep reinforcing

    async def on_start(self):
        self.attacking = False

    async def on_step(self, it):
        if not self.townhalls:
            for u in self.units(U.VOIDRAY):
                u.attack(self.enemy_start_locations[0])
            return
        nexus = self.townhalls.first
        await self.distribute_workers()
        await self.supply(nexus)
        await self.expand()
        await self.gas()
        await self.gateway_core(nexus)
        await self.stargates(nexus)
        await self.probes()
        await self.voids()
        await self.chrono(nexus)
        await self.attack()

    async def supply(self, nexus):
        if (self.supply_left < 5 and self.supply_cap < 200
                and self.already_pending(U.PYLON) < 2
                and self.can_afford(U.PYLON)):
            await self.build(U.PYLON,
                             near=nexus.position.towards(self.game_info.map_center, 7))

    async def expand(self):
        if (self.townhalls.amount < 2 and self.time > 80
                and self.can_afford(U.NEXUS)
                and self.already_pending(U.NEXUS) == 0):
            await self.expand_now()

    async def gas(self):
        # void rays are gas-heavy: take all 4 geysers across 2 bases
        want = 2 * self.townhalls.ready.amount
        if self.gas_buildings.amount + self.already_pending(U.ASSIMILATOR) >= min(4, want):
            return
        if self.time < 40 or not self.can_afford(U.ASSIMILATOR):
            return
        for th in self.townhalls.ready:
            for g in self.vespene_geyser.closer_than(12, th):
                if not self.gas_buildings.closer_than(1, g):
                    w = self.select_build_worker(g.position)
                    if w:
                        w.build_gas(g)
                        return

    async def gateway_core(self, nexus):
        if not self.structures(U.PYLON).ready:
            return
        if not self.structures(U.GATEWAY) and not self.already_pending(U.GATEWAY) \
                and self.can_afford(U.GATEWAY):
            pylon = self.structures(U.PYLON).ready.random
            await self.build(U.GATEWAY,
                             near=pylon.position.towards(self.game_info.map_center, 4))
        if (self.structures(U.GATEWAY).ready
                and not self.structures(U.CYBERNETICSCORE)
                and not self.already_pending(U.CYBERNETICSCORE)
                and self.can_afford(U.CYBERNETICSCORE)):
            pylon = self.structures(U.PYLON).ready.random
            await self.build(U.CYBERNETICSCORE,
                             near=pylon.position.towards(self.game_info.map_center, 4))

    async def stargates(self, nexus):
        if not self.structures(U.CYBERNETICSCORE).ready:
            return
        started = self.structures(U.STARGATE).amount + self.already_pending(U.STARGATE)
        if started >= self.N_STARGATES or not self.can_afford(U.STARGATE):
            return
        pylon = self.structures(U.PYLON).ready.random
        await self.build(U.STARGATE,
                         near=pylon.position.towards(self.game_info.map_center, 5))

    async def probes(self):
        if self.supply_workers >= self.TARGET_PROBES:
            return
        for nx in self.townhalls.idle:
            if self.can_afford(U.PROBE) and self.supply_left > 0:
                nx.train(U.PROBE)

    async def voids(self):
        for sg in self.structures(U.STARGATE).ready.idle:
            if self.can_afford(U.VOIDRAY) and self.supply_left >= 4:
                sg.train(U.VOIDRAY)

    async def chrono(self, nexus):
        for nx in self.townhalls:
            if nx.energy < 50:
                continue
            busy = [s for s in self.structures(U.STARGATE).ready if not s.is_idle]
            if busy:
                nx(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])
                break

    async def attack(self):
        voids = self.units(U.VOIDRAY)
        if not self.attacking and voids.amount >= self.ATTACK_AT_VOIDS:
            self.attacking = True
        if self.attacking and voids.amount < 3:
            self.attacking = False   # wave spent: re-mass
        if self.attacking:
            target = (self.enemy_structures.closest_to(voids.center).position
                      if self.enemy_structures and voids
                      else self.enemy_start_locations[0])
            for v in voids:
                v.attack(target)
        else:
            home = self.start_location.towards(self.game_info.map_center, 10)
            for v in voids.further_than(16, home):
                v.move(home)

    async def on_end(self, result: Result):
        print(f"VoidRayBot game ended: {result}")
