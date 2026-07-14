"""FourGateZealotBot: a scripted mimic of a 4-gate zealot all-in.

A "sparring partner" you can run your own bot against to reproduce losses to this
opening -- no opponent source code needed. The build is taken directly from a
real replay (see analysis/extract_build_order.py):

    Nexus, Pylon, Pylon, 4x Gateway (~1:35-2:00), NO gas, NO cyber core,
    pure gateway-train mass Zealot, ~18 probes then all-in. First Zealot ~3:18.

This reproduces the *build, composition, and timing* of the all-in faithfully.
It does not reproduce the original bot's exact micro -- for a scripted all-in
that is ~90% of the behavior, which is plenty to test defenses against.

Validated headless (sparring/run.py, real SC2 client): 4 gateways on one base
(~0:54 / 1:10 / 2:03 / 3:10), no gas, ~30 zealots, stalled at 18 probes, first
zealot ~2:37, then all-in -- a faithful reproduction of the source 4-gate. (The
real one massed 4 gates by ~2:00; ours lands the 4th ~1 min later on the same
18-probe/no-gas economy. Tune TARGET_PROBES / gate timing to taste.)
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


class FourGateZealotBot(BotAI):
    # Tunables (mirroring the extracted build order).
    TARGET_PROBES = 18          # opponent stalled ~18 workers -- committed all-in
    NUM_GATEWAYS = 4
    ATTACK_AT_ZEALOTS = 4       # push once this many zealots exist, then never stop

    async def on_start(self):
        self.attacking = False

    async def on_step(self, iteration):
        if not self.townhalls:
            # No base left -- throw everything at the enemy.
            for unit in self.units.of_type({UnitTypeId.ZEALOT, UnitTypeId.PROBE}):
                unit.attack(self.enemy_start_locations[0])
            return

        nexus = self.townhalls.first
        await self.build_supply(nexus)
        await self.build_gateways(nexus)   # gateways get first claim on minerals
        await self.build_probes(nexus)
        await self.make_zealots()
        await self.chrono(nexus)
        await self.attack()

    @property
    def _gateways_needed(self) -> bool:
        started = self.structures(UnitTypeId.GATEWAY).amount + self.already_pending(
            UnitTypeId.GATEWAY
        )
        return started < self.NUM_GATEWAYS

    # --- pylons ahead of supply (also serve as forward positions) -----------
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

    # --- probes to the all-in cap, but never at the cost of a gateway -------
    async def build_probes(self, nexus):
        if self.supply_workers >= self.TARGET_PROBES or not nexus.is_idle:
            return
        # While we still owe gateways, bank minerals for them instead of probing.
        if self._gateways_needed and self.minerals < 200:
            return
        if self.can_afford(UnitTypeId.PROBE):
            nexus.train(UnitTypeId.PROBE)

    # --- 4 gateways ASAP (no gas, no cyber -- pure gateway zealot) ----------
    async def build_gateways(self, nexus):
        if not self.structures(UnitTypeId.PYLON).ready:
            return
        gates = self.structures(UnitTypeId.GATEWAY)
        if gates.amount + self.already_pending(UnitTypeId.GATEWAY) >= self.NUM_GATEWAYS:
            return
        if self.can_afford(UnitTypeId.GATEWAY):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(
                UnitTypeId.GATEWAY,
                near=pylon.position.towards(self.game_info.map_center, 4),
            )

    # --- mass zealot straight from the gateways -----------------------------
    async def make_zealots(self):
        for gate in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.can_afford(UnitTypeId.ZEALOT):
                gate.train(UnitTypeId.ZEALOT)

    # --- chrono: a producing gateway, else early probes for faster income ---
    async def chrono(self, nexus):
        if nexus.energy < 50:
            return
        busy = [g for g in self.structures(UnitTypeId.GATEWAY).ready if not g.is_idle]
        if busy:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])
        elif not nexus.is_idle and self.supply_workers < self.TARGET_PROBES:
            # Early game: boost probe production to bank for the gateways faster.
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

    # --- all-in: once we have a few zealots, attack and never stop ----------
    async def attack(self):
        zealots = self.units(UnitTypeId.ZEALOT)
        if not self.attacking and zealots.amount >= self.ATTACK_AT_ZEALOTS:
            self.attacking = True
        if self.attacking:
            target = (
                self.enemy_structures.random.position
                if self.enemy_structures
                else self.enemy_start_locations[0]
            )
            for z in zealots:
                z.attack(target)

    async def on_end(self, result: Result):
        print(f"FourGateZealotBot game ended: {result}")
