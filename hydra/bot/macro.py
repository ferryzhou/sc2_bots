"""macro: the economy executor -- drones, overlords, queens, injects, gas, bases.

Pure execution of the plan. It reads targets off the ``ExecutionPlan``
(drone_target, queen_target, gas_target, base_target, expand_now_ok) and issues
the Zerg orders that move toward them. It holds no strategy: swap the plan and the
same code saturates to a different drone count, expands to a different base count,
etc.

Larva is a shared, scarce resource, so the bot allocates it once per step: this
executor runs first and spends larva on overlords (supply) and drones (economy)
up to the plan's targets; whatever remains is handed to the army executor.
"""

from __future__ import annotations

import math
from typing import List

from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.unit import Unit


class Macro:
    async def step(self, bot, plan, larvae: List[Unit]) -> None:
        self._overlords(bot, plan, larvae)
        self._drones(bot, plan, larvae)
        await self._queens(bot, plan)
        self._inject(bot)
        await self._gas(bot, plan)
        await self._expand(bot, plan)

    # ------------------------------------------------------------------ supply
    def _overlords(self, bot, plan, larvae: List[Unit]) -> None:
        if bot.supply_cap >= 200:
            return
        # Larva is precious; get ahead of the block but don't over-make. Scale the
        # lead with how fast we're spending supply (more bases/production = faster).
        lead = 2 + bot.townhalls.amount * 2
        pending = bot.already_pending(U.OVERLORD)
        if bot.supply_left + pending * 8 <= lead and larvae and bot.can_afford(U.OVERLORD):
            larvae.pop().train(U.OVERLORD)

    # ------------------------------------------------------------------ drones
    def _drones(self, bot, plan, larvae: List[Unit]) -> None:
        want = plan.drone_target - bot.supply_workers - bot.already_pending(U.DRONE)
        # Spend only the planned economy share of this step's larva on drones so
        # the army executor keeps getting larva -- never hoard the whole larva
        # bank into drones (which starves army until full saturation).
        budget = len(larvae) if plan.larva_econ_share >= 1.0 else \
            math.ceil(len(larvae) * plan.larva_econ_share)
        built = 0
        while (want > 0 and built < budget and larvae
               and bot.can_afford(U.DRONE) and bot.supply_left > 0):
            larvae.pop().train(U.DRONE)
            want -= 1
            built += 1

    # ------------------------------------------------------------------ queens
    async def _queens(self, bot, plan) -> None:
        if not bot.structures(U.SPAWNINGPOOL).ready:
            return
        have = bot.units(U.QUEEN).amount + bot.already_pending(U.QUEEN)
        if have >= plan.queen_target:
            return
        for hatch in bot.townhalls.ready.idle:
            if bot.can_afford(U.QUEEN) and bot.supply_left > 0:
                hatch.train(U.QUEEN)
                return

    def _inject(self, bot) -> None:
        # Injects are the core of Zerg larva economy: every idle-energy queen
        # should keep a hatchery pumping extra larva.
        queens = [q for q in bot.units(U.QUEEN) if q.energy >= 25]
        if not queens:
            return
        used = set()
        for hatch in bot.townhalls.ready:
            if hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                continue
            free = [q for q in queens if q.tag not in used]
            if not free:
                break
            queen = min(free, key=lambda q: q.distance_to(hatch))
            queen(AbilityId.EFFECT_INJECTLARVA, hatch)
            used.add(queen.tag)

    # -------------------------------------------------------------------- gas
    def _desired_gas(self, bot, plan) -> int:
        """How many extractors we want *now*: ramp gas with the mineral economy
        instead of maxing it out immediately. Each extractor pulls 3 drones off
        minerals, so taking 2 gas at 1:30 on 15 drones cripples early income and
        floats gas we can't yet spend. ~1 extractor per 16 drones, capped by the
        profile's gas_target, keeps minerals saturated first."""
        ramp = 1 + bot.supply_workers // 16
        # ease off gas entirely when it's already piling up (mineral income is
        # the real constraint for a mineral-heavy Zerg army)
        if bot.vespene > 400:
            ramp = min(ramp, bot.gas_buildings.amount)
        return min(plan.gas_target, ramp)

    async def _gas(self, bot, plan) -> None:
        if not bot.structures(U.SPAWNINGPOOL).ready:
            return  # no point on gas before the pool (nothing needs it yet)
        have = bot.gas_buildings.amount + bot.already_pending(U.EXTRACTOR)
        if have >= self._desired_gas(bot, plan) or not bot.can_afford(U.EXTRACTOR):
            return
        for hatch in bot.townhalls.ready:
            for geyser in bot.vespene_geyser.closer_than(10, hatch):
                if bot.gas_buildings.closer_than(1.0, geyser):
                    continue
                worker = bot.select_build_worker(geyser.position)
                if worker:
                    worker.build_gas(geyser)
                    return

    # ----------------------------------------------------------------- expand
    async def _expand(self, bot, plan) -> None:
        if not plan.expand_now_ok:
            return
        if not bot.can_afford(U.HATCHERY) or bot.already_pending(U.HATCHERY):
            return
        bases = bot.townhalls.amount + bot.already_pending(U.HATCHERY)
        saturated = bot.supply_workers >= 0.80 * 16 * bot.townhalls.amount
        take_natural = bot.townhalls.amount < 2 and bot.supply_workers >= 13

        if bases < plan.base_target:
            # up to the plan's base count: take the natural early, later bases
            # when near saturation, floating minerals, or once we have an army to
            # cover the expansion (take the map behind the army -- a turtle that
            # never expands strangles itself on one base)
            if take_natural or saturated or bot.minerals > 400 or bot.supply_army >= 18:
                await self._build_hatch(bot)
            return

        # Beyond the plan: a maxed economy floating minerals is larva-limited,
        # not resource-limited. A *macro hatchery at home* turns the banked
        # minerals into larva (injected like any base) without contesting a new
        # expansion the army has to defend -- the reliable Zerg answer to a float.
        # a float of *either* resource on a maxed economy means we're
        # larva-limited (can't convert income to army fast enough)
        floating_hard = (bot.minerals > 450 or bot.vespene > 500) and saturated
        total_hatch = bot.structures.of_type(
            {U.HATCHERY, U.LAIR, U.HIVE}).amount + bot.already_pending(U.HATCHERY)
        if floating_hard and total_hatch < plan.base_target + 3:
            base = bot.townhalls.ready.random if bot.townhalls.ready else bot.townhalls.first
            try:
                await bot.build(
                    U.HATCHERY, near=base.position.towards(bot.game_info.map_center, 7))
            except Exception:  # noqa: BLE001
                pass

    async def _build_hatch(self, bot) -> None:
        try:
            await bot.expand_now()
        except Exception:  # noqa: BLE001 - placement can transiently fail
            pass
