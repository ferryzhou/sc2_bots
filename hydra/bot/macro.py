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
    async def _gas(self, bot, plan) -> None:
        if not bot.structures(U.SPAWNINGPOOL) and bot.time < 120:
            return  # no point on gas before any tech building wants it
        have = bot.gas_buildings.amount + bot.already_pending(U.EXTRACTOR)
        if have >= plan.gas_target or not bot.can_afford(U.EXTRACTOR):
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
        if bot.townhalls.amount + bot.already_pending(U.HATCHERY) >= plan.base_target:
            return
        if not bot.can_afford(U.HATCHERY) or bot.already_pending(U.HATCHERY):
            return
        # Take the natural as soon as we have a small worker base; take later
        # bases when near saturation or floating minerals.
        saturated = bot.supply_workers >= 0.80 * 16 * bot.townhalls.amount
        take_natural = bot.townhalls.amount < 2 and bot.supply_workers >= 13
        floating = bot.minerals > 400
        if take_natural or saturated or floating:
            try:
                await bot.expand_now()
            except Exception:  # noqa: BLE001 - placement can transiently fail
                pass
