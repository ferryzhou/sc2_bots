"""Economy: probes, supply, gas, expansions, chrono -- gated by the advisor.

Follows the macro fundamentals: never stop probes (while safe), don't get supply
blocked, take gas for tech, and expand when the advisor says economy is the
priority and we aren't under threat.
"""

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U
from strategy_engine import Investment


class Economy:
    async def step(self, bot, advice, scripted=False):
        await self._supply(bot, advice)
        self._probes(bot, advice)
        self._chrono(bot)
        # while a --build script is running it owns gas + expansions; economy
        # keeps only worker/supply/chrono so the two don't double-build.
        if scripted:
            return
        await self._gas(bot)
        await self._expand(bot, advice)

    def _probes(self, bot, advice):
        cap = min(75, 22 * max(1, bot.townhalls.amount) + 6)
        if bot.supply_workers >= cap:
            return
        # Under an emergency with little army, save minerals for gateway units.
        if (advice.defense.prioritize_army and bot.supply_army < 8
                and bot.time < 240 and bot.minerals < 200):
            return
        # If the library wants static defense and the Forge isn't down yet, stop
        # probing once a pylon exists and bank for the Forge, so it lands ~0:55
        # (the winners' timing) instead of ~1:10.
        if (advice.defense.static_defense >= 1 and not bot.structures(U.FORGE)
                and bot.already_pending(U.FORGE) == 0 and bot.structures(U.PYLON)
                and bot.minerals < 150):
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
        # Extra "spend the float" pylons only once we're established -- never in
        # the opening, where pylon spam delays the first gateway.
        floating = bot.minerals > 500 and bot.supply_cap >= 32
        if (
            bot.supply_cap < 200
            and bot.townhalls
            and bot.can_afford(U.PYLON)
            and ((bot.supply_left <= threshold and pending < 2) or (floating and pending < 3))
        ):
            # First pylon goes on the ramp to power the wall; later pylons at base.
            wall_pylon = bot.wall.pylon_pos(bot)
            if wall_pylon is not None and not bot.structures(U.PYLON):
                await bot.build(U.PYLON, near=wall_pylon)
            else:
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
        # The library decides when we're too threatened to expand -- but if our
        # cannons/wall are holding and we have some army, take the map anyway:
        # out-scaling a thin-economy ling flood is how we win (bot_profiles/12PoolBot,
        # "then punish the thin economy"). Otherwise sit tight.
        if advice.defense.prioritize_army:
            cannons_up = bot.structures(U.PHOTONCANNON).ready.amount >= advice.defense.static_defense
            if not (cannons_up and bot.townhalls.amount < 3 and bot.supply_army >= 8):
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
