"""OneBaseStalkerBot: a scripted mimic of the one-base stalker all-in.

A sparring partner to reproduce losses to OneBaseStalkerBot's opening without
its source. Build taken from its replay (analysis/extract_build_order.py on
loss_OneBaseStalkerBot_*.SC2Replay):

    Nexus, Pylon @0:31, Gateway @1:00, 2x Assimilator @1:02/1:34, Pylon @1:44,
    Gateway @2:09, CyberneticsCore @2:30, Gateway @3:16, Gateway @4:25 -- one
    base, 2 gas, 4 gateways, cyber core, pure mass Stalker. First Stalker
    ~3:45, ~22 probes then all-in; ~33 stalkers produced.

Reproduces the build, composition, and timing of the all-in faithfully (not the
original's exact stalker micro -- for a scripted timing that's ~90% of it).

Tunables at the top of the class: TARGET_PROBES, NUM_GATEWAYS,
ATTACK_AT_STALKERS.
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


class OneBaseStalkerBot(BotAI):
    TARGET_PROBES = 22          # stalls ~22 workers on one base -- all-in
    NUM_GATEWAYS = 4
    ATTACK_AT_STALKERS = 6      # push once this many, then never stop

    async def on_start(self):
        self.attacking = False

    async def on_step(self, iteration):
        if not self.townhalls:
            for u in self.units.of_type({UnitTypeId.STALKER, UnitTypeId.PROBE}):
                u.attack(self.enemy_start_locations[0])
            return

        nexus = self.townhalls.first
        await self.build_supply(nexus)
        await self.build_gas(nexus)
        await self.build_gateways(nexus)
        await self.build_cyber(nexus)
        await self.build_probes(nexus)
        await self.make_stalkers()
        await self.chrono(nexus)
        await self.attack()

    @property
    def _gateways_started(self) -> int:
        return self.structures(UnitTypeId.GATEWAY).amount + self.already_pending(
            UnitTypeId.GATEWAY
        )

    async def build_supply(self, nexus):
        if (
            self.supply_left < 3
            and self.supply_cap < 200
            and self.already_pending(UnitTypeId.PYLON) < 2
            and self.can_afford(UnitTypeId.PYLON)
        ):
            await self.build(
                UnitTypeId.PYLON,
                near=nexus.position.towards(self.game_info.map_center, 6),
            )

    async def build_gas(self, nexus):
        # 2 assimilators (stalkers need gas), started early
        if self.structures(UnitTypeId.ASSIMILATOR).amount + self.already_pending(
            UnitTypeId.ASSIMILATOR
        ) >= 2:
            return
        if self.time < 60 or not self.can_afford(UnitTypeId.ASSIMILATOR):
            return
        for geyser in self.vespene_geyser.closer_than(12, nexus):
            if not self.gas_buildings.closer_than(1, geyser):
                worker = self.select_build_worker(geyser.position)
                if worker:
                    worker.build_gas(geyser)
                    break

    async def build_gateways(self, nexus):
        if not self.structures(UnitTypeId.PYLON).ready:
            return
        if self._gateways_started >= self.NUM_GATEWAYS:
            return
        # cadence: only start the 3rd/4th gateway once cyber is underway,
        # mirroring the replay (gateway 1-2 early, then cyber, then 3-4)
        if self._gateways_started >= 2 and not (
            self.structures(UnitTypeId.CYBERNETICSCORE)
            or self.already_pending(UnitTypeId.CYBERNETICSCORE)
        ):
            return
        if self.can_afford(UnitTypeId.GATEWAY):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(
                UnitTypeId.GATEWAY,
                near=pylon.position.towards(self.game_info.map_center, 4),
            )

    async def build_cyber(self, nexus):
        if (
            self.structures(UnitTypeId.GATEWAY).ready
            and not self.structures(UnitTypeId.CYBERNETICSCORE)
            and not self.already_pending(UnitTypeId.CYBERNETICSCORE)
            and self.can_afford(UnitTypeId.CYBERNETICSCORE)
        ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(
                UnitTypeId.CYBERNETICSCORE,
                near=pylon.position.towards(self.game_info.map_center, 4),
            )

    async def build_probes(self, nexus):
        if self.supply_workers >= self.TARGET_PROBES or not nexus.is_idle:
            return
        # don't starve gateways/cyber of minerals while they're owed
        if self._gateways_started < self.NUM_GATEWAYS and self.minerals < 150:
            return
        if self.can_afford(UnitTypeId.PROBE):
            nexus.train(UnitTypeId.PROBE)

    async def make_stalkers(self):
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            return
        for gate in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.can_afford(UnitTypeId.STALKER):
                gate.train(UnitTypeId.STALKER)

    async def chrono(self, nexus):
        if nexus.energy < 50:
            return
        # prioritise chrono on a producing gateway; else cyber; else probes
        busy_gates = [
            g for g in self.structures(UnitTypeId.GATEWAY).ready if not g.is_idle
        ]
        cyber = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        if busy_gates:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy_gates[0])
        elif not nexus.is_idle and self.supply_workers < self.TARGET_PROBES:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

    async def attack(self):
        stalkers = self.units(UnitTypeId.STALKER)
        if not self.attacking and stalkers.amount >= self.ATTACK_AT_STALKERS:
            self.attacking = True
        if self.attacking:
            target = (
                self.enemy_structures.random.position
                if self.enemy_structures
                else self.enemy_start_locations[0]
            )
            for s in stalkers:
                s.attack(target)

    async def on_end(self, result: Result):
        print(f"OneBaseStalkerBot game ended: {result}")
