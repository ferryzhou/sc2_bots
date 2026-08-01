"""MacroTerranBot: a strong scripted bio Terran (marine/marauder/medivac macro).

Reproduces the ladder Terran-macro losses (Terranosaur ~298 marines,
muravevTerran ~172): phoenix is even/ahead at 6:00 but a bio ball out-scales its
pure-stalker army in the lategame. To out-scale (and survive stalker kiting
without perfect micro) this version leans on the things that make bio strong
WITHOUT frame-perfect play:
  - 3 bases, ~60 SCVs, 12+ barracks (reactors) for volume,
  - Engineering-bay infantry weapon/armor upgrades + Combat Shield + Stim
    (passive power that a-move marines keep),
  - Medivacs for heal/sustain,
  - stim-on-engage and CONTINUOUS reinforcement (mass to a critical ball, then
    never stop feeding), instead of one suicide push.

Still not micro-perfect (no marine split / kite), so treat a phoenix WIN as
necessary-but-not-sufficient and a phoenix LOSS as a genuine reproduction.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as UP


class MacroTerranBot(BotAI):
    TARGET_SCVS = 60
    N_BARRACKS = 12
    MAX_BASES = 3
    PUSH_AT = 60           # supply of army to first commit
    MARAUDER_EVERY = 4     # 1 in 4 bio is a marauder (armored punch)

    async def on_start(self):
        self.committed = False

    async def on_step(self, it):
        if not self.townhalls:
            for u in self.units.of_type({U.MARINE, U.MARAUDER}):
                u.attack(self.enemy_start_locations[0])
            return
        cc = self.townhalls.first
        await self.depots(cc)
        await self.expand()
        await self.gas()
        await self.orbital_and_mule()
        await self.rax(cc)
        await self.addons()
        await self.ebay_and_upgrades(cc)
        await self.techlab_research()
        await self.starport(cc)
        await self.scvs()
        await self.train()
        await self.army()

    async def depots(self, cc):
        if (self.supply_left < 7 and self.supply_cap < 200
                and self.already_pending(U.SUPPLYDEPOT) < 3
                and self.can_afford(U.SUPPLYDEPOT)):
            await self.build(U.SUPPLYDEPOT,
                             near=cc.position.towards(self.game_info.map_center, 8))

    async def expand(self):
        if (self.townhalls.amount < self.MAX_BASES and self.time > 50
                and self.can_afford(U.COMMANDCENTER)
                and self.already_pending(U.COMMANDCENTER) == 0):
            await self.expand_now()

    async def gas(self):
        if self.time < 25:
            return
        want = 2 * self.townhalls.ready.amount
        if self.gas_buildings.amount + self.already_pending(U.REFINERY) >= min(6, want):
            return
        if not self.can_afford(U.REFINERY):
            return
        for th in self.townhalls.ready:
            for g in self.vespene_geyser.closer_than(10, th):
                if not self.gas_buildings.closer_than(1, g):
                    w = self.select_build_worker(g.position)
                    if w:
                        w.build_gas(g)
                        return

    async def orbital_and_mule(self):
        for cc in self.townhalls.idle:
            if cc.type_id == U.COMMANDCENTER and self.can_afford(U.ORBITALCOMMAND) \
                    and self.structures(U.BARRACKS).ready:
                cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
        for o in self.townhalls:
            if o.type_id == U.ORBITALCOMMAND and o.energy >= 50:
                mfs = self.mineral_field.closer_than(10, o)
                if mfs:
                    o(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mfs.closest_to(o))

    async def rax(self, cc):
        if not self.structures(U.SUPPLYDEPOT).ready:
            return
        started = self.structures(U.BARRACKS).amount + self.already_pending(U.BARRACKS)
        cap = 2 if self.townhalls.amount < 2 else self.N_BARRACKS
        if started >= cap or not self.can_afford(U.BARRACKS):
            return
        await self.build(U.BARRACKS,
                         near=cc.position.towards(self.game_info.map_center, 12))

    async def addons(self):
        # first rax gets a tech lab (stim/shield), the rest reactors (2 marines)
        techlabs = self.structures(U.BARRACKSTECHLAB).amount \
            + self.already_pending(U.BARRACKSTECHLAB)
        for b in self.structures(U.BARRACKS).ready.idle:
            if b.add_on_tag != 0:
                continue
            if techlabs < 1 and self.can_afford(U.BARRACKSTECHLAB):
                b.build(U.BARRACKSTECHLAB)
                techlabs += 1
            elif self.can_afford(U.BARRACKSREACTOR):
                b.build(U.BARRACKSREACTOR)

    async def ebay_and_upgrades(self, cc):
        if self.time < 150:
            return
        ebays = self.structures(U.ENGINEERINGBAY)
        if ebays.amount + self.already_pending(U.ENGINEERINGBAY) < 2 \
                and self.can_afford(U.ENGINEERINGBAY):
            await self.build(U.ENGINEERINGBAY,
                             near=cc.position.towards(self.game_info.map_center, 6))
        for e in ebays.ready.idle:
            for up in (UP.TERRANINFANTRYWEAPONSLEVEL1, UP.TERRANINFANTRYARMORSLEVEL1,
                       UP.TERRANINFANTRYWEAPONSLEVEL2, UP.TERRANINFANTRYARMORSLEVEL2,
                       UP.TERRANINFANTRYWEAPONSLEVEL3, UP.TERRANINFANTRYARMORSLEVEL3):
                if self.already_pending_upgrade(up) == 0 and self.can_afford(up):
                    e.research(up)
                    break

    async def techlab_research(self):
        for tl in self.structures(U.BARRACKSTECHLAB).ready.idle:
            for up in (UP.SHIELDWALL, UP.STIMPACK, UP.PUNISHERGRENADES):  # shield, stim, conc
                if self.already_pending_upgrade(up) == 0 and self.can_afford(up):
                    tl.research(up)
                    break

    async def starport(self, cc):
        if self.time < 200 or not self.structures(U.BARRACKS).ready:
            return
        sp = self.structures(U.STARPORT)
        if sp.amount + self.already_pending(U.STARPORT) < 1 and self.can_afford(U.STARPORT):
            await self.build(U.STARPORT,
                             near=cc.position.towards(self.game_info.map_center, 10))

    async def scvs(self):
        if self.supply_workers >= self.TARGET_SCVS or self.supply_left <= 0:
            return
        for cc in self.townhalls.idle:
            if self.can_afford(U.SCV):
                cc.train(U.SCV)

    async def train(self):
        if self.supply_left <= 0:
            return
        # a few medivacs from the starport
        for s in self.structures(U.STARPORT).ready.idle:
            if self.units(U.MEDIVAC).amount < 4 and self.can_afford(U.MEDIVAC):
                s.train(U.MEDIVAC)
        # bio from barracks: mostly marines, some marauders
        have_tl = self.structures(U.BARRACKSTECHLAB).ready
        for b in self.structures(U.BARRACKS).ready.idle:
            if (have_tl and b.has_techlab
                    and self.units(U.MARAUDER).amount * self.MARAUDER_EVERY
                    < self.units(U.MARINE).amount
                    and self.can_afford(U.MARAUDER)):
                b.train(U.MARAUDER)
            elif self.can_afford(U.MARINE):
                b.train(U.MARINE)

    async def army(self):
        bio = self.units.of_type({U.MARINE, U.MARAUDER})
        medivacs = self.units(U.MEDIVAC)
        if not self.committed and self.supply_army >= self.PUSH_AT:
            self.committed = True
        if not self.committed:
            # gather at the natural / ramp until the ball is ready
            rally = self.townhalls.first.position.towards(self.game_info.map_center, 8)
            for m in bio.idle:
                m.move(rally)
            return
        target = (self.enemy_structures.closest_to(bio.center).position
                  if self.enemy_structures and bio
                  else self.enemy_start_locations[0])
        for m in bio:
            # stim when close to the fight (cheap, no split micro)
            if (m.type_id in (U.MARINE, U.MARAUDER)
                    and not m.has_buff(BuffId.STIMPACK)
                    and self.enemy_units and m.health_percentage > 0.5
                    and self.enemy_units.closer_than(7, m)):
                m(AbilityId.EFFECT_STIM)
            m.attack(target)
        for md in medivacs:
            md.attack(bio.center if bio else target)

    async def on_end(self, result: Result):
        print(f"MacroTerranBot game ended: {result} "
              f"(marines made ~{self.units(U.MARINE).amount} alive)")
