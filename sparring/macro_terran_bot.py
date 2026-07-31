"""MacroTerranBot: a scripted mass-bio Terran (marine/marauder/medivac macro).

Reproduces the ladder's Terran-macro losses (Terranosaur, muravevTerran): phoenix
is even/ahead at 6:00 but a bio army out-scales its pure-stalker ball in the
lategame (298 marines in the Terranosaur replay). This mimic macros bio off two
bases with constant barracks production and waves, so phoenix must tech an AoE
answer (colossus) to survive -- pure stalker loses to massed marine.

Not micro-perfect (no stim dance / kiting), so it under-represents the real
bots' fights; treat a phoenix WIN here as necessary-but-not-sufficient.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U


class MacroTerranBot(BotAI):
    TARGET_SCVS = 44
    N_BARRACKS = 8
    ATTACK_SUPPLY = 40

    async def on_start(self):
        self.attacking = False

    async def on_step(self, it):
        if not self.townhalls:
            for u in self.units.of_type({U.MARINE, U.MARAUDER}):
                u.attack(self.enemy_start_locations[0])
            return
        cc = self.townhalls.first
        await self.depots(cc)
        await self.expand()
        await self.gas(cc)
        await self.rax(cc)
        await self.addons()
        await self.scvs()
        await self.units_train()
        await self.upgrades(cc)
        await self.mule(cc)
        await self.army()

    async def depots(self, cc):
        if (self.supply_left < 6 and self.supply_cap < 200
                and self.already_pending(U.SUPPLYDEPOT) < 2
                and self.can_afford(U.SUPPLYDEPOT)):
            await self.build(U.SUPPLYDEPOT,
                             near=cc.position.towards(self.game_info.map_center, 8))

    async def expand(self):
        if (self.townhalls.amount < 2 and self.time > 60
                and self.can_afford(U.COMMANDCENTER)
                and not self.already_pending(U.COMMANDCENTER)):
            await self.expand_now()

    async def gas(self, cc):
        want = 2 if self.townhalls.amount >= 1 else 1
        have = self.gas_buildings.amount + self.already_pending(U.REFINERY)
        if have >= min(4, want + self.townhalls.amount - 1):
            return
        if self.time < 25 or not self.can_afford(U.REFINERY):
            return
        for th in self.townhalls:
            for g in self.vespene_geyser.closer_than(10, th):
                if not self.gas_buildings.closer_than(1, g):
                    w = self.select_build_worker(g.position)
                    if w:
                        w.build_gas(g)
                        return

    async def rax(self, cc):
        if not self.structures(U.SUPPLYDEPOT).ready:
            return
        started = self.structures(U.BARRACKS).amount + self.already_pending(U.BARRACKS)
        if started >= self.N_BARRACKS or not self.can_afford(U.BARRACKS):
            return
        # throttle so we don't bankrupt the opening
        if started >= 2 and self.townhalls.amount < 2:
            return
        await self.build(U.BARRACKS,
                         near=cc.position.towards(self.game_info.map_center, 12))

    async def addons(self):
        for b in self.structures(U.BARRACKS).ready.idle:
            if b.add_on_tag == 0 and self.can_afford(U.BARRACKSREACTOR):
                b.build(U.BARRACKSREACTOR)

    async def scvs(self):
        if self.supply_workers >= self.TARGET_SCVS:
            return
        for cc in self.townhalls.idle:
            if self.can_afford(U.SCV) and self.supply_left > 0:
                cc.train(U.SCV)

    async def units_train(self):
        if not self.can_afford(U.MARINE) or self.supply_left <= 0:
            return
        for b in self.structures(U.BARRACKS).ready.idle:
            b.train(U.MARINE)

    async def upgrades(self, cc):
        # tech lab on one rax for stim/combat shield eventually (cheap flavor)
        pass

    async def mule(self, cc):
        for o in self.townhalls:
            if o.type_id == U.ORBITALCOMMAND and o.energy >= 50:
                mfs = self.mineral_field.closer_than(10, o)
                if mfs:
                    o(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mfs.random)
        # upgrade CC -> orbital for mules + scan
        for c in self.townhalls.idle:
            if c.type_id == U.COMMANDCENTER and self.can_afford(U.ORBITALCOMMAND) \
                    and self.structures(U.BARRACKS).ready:
                c(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)

    async def army(self):
        bio = self.units.of_type({U.MARINE, U.MARAUDER})
        if not self.attacking and self.supply_army >= self.ATTACK_SUPPLY:
            self.attacking = True
        if self.attacking and bio:
            target = (self.enemy_structures.closest_to(bio.center).position
                      if self.enemy_structures else self.enemy_start_locations[0])
            for m in bio:
                m.attack(target)

    async def on_end(self, result: Result):
        print(f"MacroTerranBot game ended: {result}")
