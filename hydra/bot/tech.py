"""tech: the production executor -- structures, tech tiers, army, upgrades, defense.

This is the generic engine that realises a plan's army. It contains no strategy
and almost no hard-coded build logic; instead it reads the declarative tables in
``zerg_data`` to answer "what does this unit need, and how is it made", and drives
everything from the plan's ``army_composition`` / ``tech_targets`` /
``upgrade_targets``:

* build the prerequisite structures (in dependency order) for whatever the plan
  wants to produce, including morphing Hatchery->Lair->Hive when a higher tier is
  required and Spire->Greater Spire for broodlord tech;
* spend the remaining larva on the composition (redirecting a morph unit's demand
  onto its base larva unit), then morph the base units up (ling->bane, roach->
  ravager, hydra->lurker, corruptor->broodlord, overlord->overseer);
* research the plan's upgrades at whatever structure provides them;
* lay down the plan's static defense.

Change the plan (or the tables) and the behaviour changes with zero edits here.
"""

from __future__ import annotations

from typing import Dict, List

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit

from . import zerg_data
from .zerg_data import STRUCTURES, UNITS, Tier

# Which structure researches which upgrade. Only the upgrades the library uses
# need appear; unknown upgrades are simply skipped.
_UPGRADE_SOURCE: Dict[UpgradeId, U] = {
    UpgradeId.ZERGLINGMOVEMENTSPEED: U.SPAWNINGPOOL,
    UpgradeId.ZERGLINGATTACKSPEED: U.SPAWNINGPOOL,
    UpgradeId.ZERGMISSILEWEAPONSLEVEL1: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMISSILEWEAPONSLEVEL2: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMISSILEWEAPONSLEVEL3: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGGROUNDARMORSLEVEL1: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGGROUNDARMORSLEVEL2: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGGROUNDARMORSLEVEL3: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMELEEWEAPONSLEVEL1: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMELEEWEAPONSLEVEL2: U.EVOLUTIONCHAMBER,
    UpgradeId.ZERGMELEEWEAPONSLEVEL3: U.EVOLUTIONCHAMBER,
}


class Tech:
    async def step(self, bot, plan, larvae: List[Unit]) -> None:
        await self._structures(bot, plan)
        await self._tier(bot, plan)
        self._train_army(bot, plan, larvae)
        self._morphs(bot, plan)
        self._upgrades(bot, plan)
        await self._static_defense(bot, plan)

    # --------------------------------------------------------------- helpers
    @staticmethod
    def _ready(bot, struct: U) -> bool:
        """Is a prerequisite structure available (tier morphs count upward)?"""
        if struct == U.HATCHERY:
            return bot.townhalls.ready.exists
        if struct == U.LAIR:
            return bot.structures(U.LAIR).ready.exists or bot.structures(U.HIVE).ready.exists
        if struct == U.HIVE:
            return bot.structures(U.HIVE).ready.exists
        if struct == U.SPIRE:
            return bot.structures(U.SPIRE).ready.exists or bot.structures(U.GREATERSPIRE).ready.exists
        return bot.structures(struct).ready.exists

    @staticmethod
    def _count(bot, struct: U) -> int:
        return bot.structures(struct).amount + bot.already_pending(struct)

    def _prereqs_ready(self, bot, struct: U) -> bool:
        spec = STRUCTURES.get(struct)
        if not spec:
            return True
        return all(self._ready(bot, dep) for dep in spec.needs)

    def _build_near_base(self, bot, struct: U):
        base = bot.townhalls.ready.random if bot.townhalls.ready else bot.townhalls.first
        pos = base.position.towards(bot.game_info.map_center, 6)
        return bot.build(struct, near=pos)

    # ------------------------------------------------------------ structures
    async def _structures(self, bot, plan) -> None:
        # A Spawning Pool underpins queens, injects, lings and static defense --
        # every strategy wants it, so ensure it regardless of composition.
        wanted: List[U] = [U.SPAWNINGPOOL]
        wanted += [s for s in plan.prerequisite_structures if s not in wanted]
        # Evolution chamber(s) when the plan carries ground weapon/armor upgrades.
        if any(_UPGRADE_SOURCE.get(up) == U.EVOLUTIONCHAMBER for up in plan.upgrade_targets):
            wanted.append(U.EVOLUTIONCHAMBER)

        for struct in wanted:
            spec = STRUCTURES.get(struct)
            if spec is None or spec.morph_from is not None:
                continue  # morph structures handled in _tier / _morphs
            want = 2 if struct == U.EVOLUTIONCHAMBER else 1
            if self._count(bot, struct) >= want:
                continue
            if not self._prereqs_ready(bot, struct):
                continue
            if bot.can_afford(struct) and bot.workers.exists:
                try:
                    await self._build_near_base(bot, struct)
                except Exception:  # noqa: BLE001 - placement can transiently fail
                    pass
                return  # one structure per step keeps drone pulls sane

    # ------------------------------------------------------------ tech tiers
    async def _tier(self, bot, plan) -> None:
        target = plan.tier_target
        has_lair = bot.structures(U.LAIR).ready.exists or bot.structures(U.HIVE).exists
        has_hive = bot.structures(U.HIVE).exists

        # Hatchery -> Lair
        if target.value >= Tier.LAIR.value and not (has_lair or bot.already_pending(U.LAIR)):
            if bot.structures(U.SPAWNINGPOOL).ready and bot.can_afford(U.LAIR):
                hatch = next((h for h in bot.townhalls.ready.idle), None) or (
                    bot.townhalls.ready.first if bot.townhalls.ready else None)
                if hatch:
                    hatch(zerg_data.STRUCTURES[U.LAIR].morph_ability)
                    return

        # Lair -> Hive (needs an Infestation Pit)
        if (target.value >= Tier.HIVE.value and not has_hive
                and not bot.already_pending(U.HIVE)
                and bot.structures(U.INFESTATIONPIT).ready
                and bot.structures(U.LAIR).ready and bot.can_afford(U.HIVE)):
            lair = bot.structures(U.LAIR).ready.first
            lair(zerg_data.STRUCTURES[U.HIVE].morph_ability)
            return

        # Spire -> Greater Spire (broodlord tech), when the plan needs it
        if (U.GREATERSPIRE in plan.prerequisite_structures and has_hive
                and bot.structures(U.SPIRE).ready
                and not bot.structures(U.GREATERSPIRE).exists
                and not bot.already_pending(U.GREATERSPIRE)
                and bot.can_afford(U.GREATERSPIRE)):
            bot.structures(U.SPIRE).ready.first(
                zerg_data.STRUCTURES[U.GREATERSPIRE].morph_ability)

    # -------------------------------------------------------------- army/larva
    def _train_army(self, bot, plan, larvae: List[Unit]) -> None:
        comp = plan.army_composition
        if not comp or not larvae:
            return

        # Redirect each morph unit's demand onto the larva unit it morphs from
        # (bane<-ling, ravager<-roach, lurker<-hydra, brood<-corruptor).
        larva_weights: Dict[U, float] = {}
        for unit, weight in comp.items():
            spec = UNITS[unit]
            base = unit
            if spec.morph_from and spec.morph_from != U.OVERLORD:
                base = spec.morph_from
                base_spec = UNITS.get(base)
                if base_spec is None or base_spec.morph_from:  # only larva bases
                    continue
            larva_weights[base] = larva_weights.get(base, 0.0) + weight

        buildable = [u for u in larva_weights if self._buildable(bot, u)]
        if not buildable:
            return

        counts = {u: bot.units(u).amount for u in larva_weights}
        total = max(1, sum(counts.values()))

        while larvae:
            # pick the buildable unit furthest below its target share
            def deficit(u):
                return larva_weights[u] - counts.get(u, 0) / total
            pick = max((u for u in buildable if bot.can_afford(u)),
                       key=deficit, default=None)
            if pick is None or bot.supply_left <= 0:
                break
            larvae.pop().train(pick)
            counts[pick] = counts.get(pick, 0) + 1
            total += 1

    def _buildable(self, bot, unit: U) -> bool:
        spec = UNITS.get(unit)
        if not spec:
            return False
        return all(self._ready(bot, s) for s in spec.needs)

    def _morphs(self, bot, plan) -> None:
        comp = plan.army_composition
        army_count = max(1, sum(bot.units(u).amount for u in comp))
        for unit, weight in comp.items():
            spec = UNITS[unit]
            if not spec.morph_from or spec.morph_from == U.OVERLORD:
                continue
            if not all(self._ready(bot, s) for s in spec.needs):
                continue
            if not bot.can_afford(unit):
                continue
            have = bot.units(unit).amount + bot.already_pending(unit)
            want = max(1, round(weight * army_count))
            bases = bot.units(spec.morph_from).ready
            morphed = 0
            for base_unit in bases:
                if have + morphed >= want or morphed >= 2:
                    break
                if not bot.can_afford(unit):
                    break
                base_unit(spec.morph_ability)
                morphed += 1

        # Overseer for detection: morph one overlord when the plan needs it.
        if plan.need_detection and self._ready(bot, U.LAIR):
            have_os = bot.units(U.OVERSEER).amount + bot.already_pending(U.OVERSEER)
            spare = bot.units(U.OVERLORD).ready
            if have_os == 0 and spare and bot.can_afford(U.OVERSEER):
                spare.random(UNITS[U.OVERSEER].morph_ability)

    # ---------------------------------------------------------------- upgrades
    def _upgrades(self, bot, plan) -> None:
        for up in plan.upgrade_targets:
            source = _UPGRADE_SOURCE.get(up)
            if source is None:
                continue
            if bot.already_pending_upgrade(up) > 0 or up in bot.state.upgrades:
                continue
            builders = bot.structures(source).ready.idle
            if builders and bot.can_afford(up):
                builders.first.research(up)
                return  # one research per step

    # ---------------------------------------------------------- static defense
    async def _static_defense(self, bot, plan) -> None:
        if not bot.structures(U.SPAWNINGPOOL).ready:
            return
        base = self._forward_base(bot)
        if base is None:
            return
        if plan.spines > self._count(bot, U.SPINECRAWLER) and bot.can_afford(U.SPINECRAWLER):
            await self._build_defense(bot, U.SPINECRAWLER, base)
            return
        if plan.spores > self._count(bot, U.SPORECRAWLER) and bot.can_afford(U.SPORECRAWLER):
            await self._build_defense(bot, U.SPORECRAWLER, base)

    def _forward_base(self, bot):
        if not bot.townhalls:
            return None
        return bot.townhalls.closest_to(bot.enemy_start_locations[0])

    async def _build_defense(self, bot, struct: U, base) -> None:
        # spines guard the choke side, spores the mineral line (air/detection)
        if struct == U.SPINECRAWLER:
            pos = base.position.towards(bot.game_info.map_center, 6)
        else:
            mins = bot.mineral_field.closer_than(10, base)
            pos = base.position.towards(mins.center, 3) if mins else base.position
        try:
            await bot.build(struct, near=pos)
        except Exception:  # noqa: BLE001
            pass
