"""Economy: probes, supply, gas, expansions, chrono -- gated by the advisor.

Follows the macro fundamentals: never stop probes (while safe), don't get supply
blocked, take gas for tech, and expand when the advisor says economy is the
priority and we aren't under threat.
"""

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U
from strategy_engine import Investment, Archetype


class Economy:
    async def step(self, bot, advice):
        await self._supply(bot, advice)
        self._probes(bot, advice)
        await self._gas(bot)
        await self._expand(bot, advice)
        self._chrono(bot)

    def _probes(self, bot, advice):
        cap = min(75, 22 * max(1, bot.townhalls.amount) + 6)
        if bot.supply_workers >= cap:
            return
        for nexus in bot.townhalls.ready.idle:
            if bot.can_afford(U.PROBE) and bot.supply_left > 0:
                nexus.train(U.PROBE)

    async def _supply(self, bot, advice):
        # Aggressive supply: idle production from a supply block is the #1 way a
        # macro Protoss floats minerals. Build well ahead of the block.
        production = max(1, bot.structures(U.GATEWAY).amount + bot.structures(U.WARPGATE).amount)
        threshold = 3 + 2 * production
        pending = bot.already_pending(U.PYLON)
        floating = bot.minerals > 400
        if (
            bot.supply_cap < 200
            and bot.townhalls
            and bot.can_afford(U.PYLON)
            and ((bot.supply_left <= threshold and pending < 3) or (floating and pending < 4))
        ):
            nexus = bot.townhalls.ready.random if bot.townhalls.ready else bot.townhalls.first
            await bot.build(U.PYLON, near=nexus.position.towards(bot.game_info.map_center, 6))

    async def _gas(self, bot):
        # two gas per base, but only once we have a gateway (no point before tech)
        if not bot.structures(U.GATEWAY):
            return
        want = min(2 * bot.townhalls.ready.amount, 6)
        have = bot.gas_buildings.amount + bot.already_pending(U.ASSIMILATOR)
        if have >= want or not bot.can_afford(U.ASSIMILATOR):
            return
        for nexus in bot.townhalls.ready:
            geysers = bot.vespene_geyser.closer_than(10, nexus)
            for g in geysers:
                if not bot.gas_buildings.closer_than(1, g):
                    worker = bot.select_build_worker(g.position)
                    if worker:
                        worker.build_gas(g)
                    return

    async def _expand(self, bot, advice):
        arch = advice.classification.archetype
        # Only a *genuine all-in* stops us expanding. A confirmed cheese halts all
        # expansion; a timing attack halts further expansion only while our army
        # is too thin to peel off and hold it.
        if arch == Archetype.CHEESE_ALLIN:
            return
        if arch == Archetype.TIMING_ATTACK and bot.supply_army < 15 and bot.time < 360:
            return
        if bot.townhalls.amount >= 4 or bot.already_pending(U.NEXUS) or not bot.can_afford(U.NEXUS):
            return
        # Take the natural early no matter what (Protoss macro fundamentals);
        # take later bases when saturated / floating / told to grow.
        take_natural = bot.townhalls.amount < 2 and bot.supply_workers >= 14
        saturated = bot.supply_workers >= 0.85 * 22 * bot.townhalls.amount
        economy_priority = Investment.ECONOMY in advice.investment.priority[:2]
        floating = bot.minerals > 500
        if take_natural or saturated or economy_priority or floating:
            await bot.expand_now()

    def _chrono(self, bot):
        for nexus in bot.townhalls.ready:
            if nexus.energy < 50:
                continue
            # priority: forge upgrade, then warpgate/robo/gateway production, then probes
            forge = bot.structures(U.FORGE).ready
            if forge and not forge.first.is_idle:
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, forge.first)
                return
            producers = [s for s in (bot.structures(U.GATEWAY).ready
                                     | bot.structures(U.ROBOTICSFACILITY).ready
                                     | bot.structures(U.CYBERNETICSCORE).ready)
                         if not s.is_idle]
            if producers:
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, producers[0])
                return
            if not nexus.is_idle and bot.supply_workers < 44:
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                return
