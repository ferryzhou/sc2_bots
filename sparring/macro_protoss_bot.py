"""MacroProtossBot: a scripted STANDARD macro Protoss (gateway-expand).

A false-positive control for phoenix's scout-driven OneBaseDefense switch. This
bot takes its natural EARLY (~2:00) -- the opposite of a one-base all-in -- so
phoenix must NOT switch to the one-base defense against it (get_enemy_expanded
goes true, and the committed-one-base read requires no natural). It then macros
on two bases into a stalker/immortal army. If phoenix ever switches to
OneBaseDefense here, that is a false positive costing it the economic game.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


class MacroProtossBot(BotAI):
    async def on_start(self):
        self.expanded = False

    async def on_step(self, iteration):
        if not self.townhalls:
            for u in self.units.of_type({UnitTypeId.STALKER, UnitTypeId.ZEALOT}):
                u.attack(self.enemy_start_locations[0])
            return
        await self.distribute_workers()
        nexus = self.townhalls.first
        await self.supply(nexus)
        await self.expand()
        await self.gas(nexus)
        await self.gates(nexus)
        await self.cyber(nexus)
        await self.probes()
        await self.robo()
        await self.army()
        await self.chrono(nexus)
        await self.attack()

    async def supply(self, nexus):
        if (self.supply_left < 4 and self.supply_cap < 200
                and self.already_pending(UnitTypeId.PYLON) < 2
                and self.can_afford(UnitTypeId.PYLON)):
            await self.build(UnitTypeId.PYLON,
                             near=nexus.position.towards(self.game_info.map_center, 6))

    async def expand(self):
        # take the natural EARLY (~2:00) -- this is the macro tell that must
        # keep phoenix OFF the one-base defense
        if (not self.expanded and self.time > 75 and self.townhalls.amount < 2
                and self.can_afford(UnitTypeId.NEXUS)):
            await self.expand_now()
            self.expanded = True

    async def gas(self, nexus):
        if self.structures(UnitTypeId.ASSIMILATOR).amount + self.already_pending(
                UnitTypeId.ASSIMILATOR) >= 2:
            return
        if self.time < 40 or not self.can_afford(UnitTypeId.ASSIMILATOR):
            return
        for g in self.vespene_geyser.closer_than(12, nexus):
            if not self.gas_buildings.closer_than(1, g):
                w = self.select_build_worker(g.position)
                if w:
                    w.build_gas(g)
                    break

    async def gates(self, nexus):
        if not self.structures(UnitTypeId.PYLON).ready:
            return
        want = 4 if self.townhalls.amount >= 2 else 1
        started = self.structures(UnitTypeId.GATEWAY).amount + self.already_pending(
            UnitTypeId.GATEWAY)
        if started >= want or not self.can_afford(UnitTypeId.GATEWAY):
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        await self.build(UnitTypeId.GATEWAY,
                         near=pylon.position.towards(self.game_info.map_center, 4))

    async def cyber(self, nexus):
        if (self.structures(UnitTypeId.GATEWAY).ready
                and not self.structures(UnitTypeId.CYBERNETICSCORE)
                and not self.already_pending(UnitTypeId.CYBERNETICSCORE)
                and self.can_afford(UnitTypeId.CYBERNETICSCORE)):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.CYBERNETICSCORE,
                             near=pylon.position.towards(self.game_info.map_center, 4))

    async def probes(self):
        if self.supply_workers >= 44 or not self.townhalls.idle:
            return
        for nx in self.townhalls.idle:
            if self.can_afford(UnitTypeId.PROBE):
                nx.train(UnitTypeId.PROBE)

    async def robo(self):
        # DemsTossV2 pattern: tech immortals behind the pressure (13 immortals
        # in the 08-18 ladder loss while Phoenix sat in emergency zealots)
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            return
        if (not self.structures(UnitTypeId.ROBOTICSFACILITY)
                and not self.already_pending(UnitTypeId.ROBOTICSFACILITY)
                and self.can_afford(UnitTypeId.ROBOTICSFACILITY)
                and self.townhalls.amount >= 2):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.ROBOTICSFACILITY,
                             near=pylon.position.towards(self.game_info.map_center, 5))
        for rb in self.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
            if self.can_afford(UnitTypeId.IMMORTAL):
                rb.train(UnitTypeId.IMMORTAL)

    async def army(self):
        # a few zealots FIRST (early poke keeps the defender's threat
        # detection hot - the DemsTossV2 grind pinned Phoenix in emergency
        # lockdown), then stalkers once the core finishes
        core = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        for gate in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if not core or self.units(UnitTypeId.ZEALOT).amount < 4:
                if self.can_afford(UnitTypeId.ZEALOT):
                    gate.train(UnitTypeId.ZEALOT)
            elif self.can_afford(UnitTypeId.STALKER):
                gate.train(UnitTypeId.STALKER)

    async def chrono(self, nexus):
        if nexus.energy < 50:
            return
        busy = [g for g in self.structures(UnitTypeId.GATEWAY).ready if not g.is_idle]
        if busy:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])

    async def attack(self):
        zealots = self.units(UnitTypeId.ZEALOT)
        stalkers = self.units(UnitTypeId.STALKER)
        immortals = self.units(UnitTypeId.IMMORTAL)
        # early zealot poke at the enemy's natural (~2:30-4:00): enough combat
        # units near their base to read as aggression, keeping the emergency on
        if self.time > 150 and zealots and stalkers.amount < 6:
            poke = self.enemy_start_locations[0].towards(
                self.game_info.map_center, 14)
            for z in zealots:
                z.attack(poke)
        # main push once the immortal/stalker ball is real, reinforce forever
        ball = stalkers.amount + 2 * immortals.amount
        if ball >= 20:
            for u in (stalkers + immortals + zealots):
                u.attack(self.enemy_start_locations[0])

    async def on_end(self, result: Result):
        print(f"MacroProtossBot game ended: {result}")
