"""FourGateZealotBot: a scripted mimic of ZEALOCALYPSE's PROXY 4-gate zealot all-in.

A sparring partner to reproduce losses to this opening -- no opponent source
needed. Building placement was extracted from the real replay
(loss_ZEALOCALYPSE_*.SC2Replay) and it is the key to the timing:

    ZEALO start (72,171) -> Phoenix start (175,76), separation 140.
    Pylon @1:00 at (119,69)  -- 112 from own base, 56 from the ENEMY.
    4x Gateway @1:30-2:06 at ~(120,68) -- ~113 from own, ~55 from ENEMY.
    44 zealots, all GATE-TRAINED (not warp-in), ~18 probes.

i.e. all four gateways are built PROXY, at the enemy's doorstep, so zealots
spawn next to the enemy and flood continuously with no cross-map walk. That
proxy placement -- not warp-in re-flood -- is why the real flood hits with
~900 army by 4:00. An earlier version of this mimic built gateways at its own
base and walked zealots across the map; phoenix held that easily. This proxy
version reproduces the real threat.

Tunables: TARGET_PROBES, NUM_GATEWAYS, PROXY_FRACTION (how far toward the
enemy the proxy sits, 0=own base .. 1=enemy base).
"""

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


class FourGateZealotBot(BotAI):
    TARGET_PROBES = 18          # the real build's worker count (best economy/
                                # army balance; 13 starved income, 22 over-mined)
    NUM_GATEWAYS = 4
    PROXY_FRACTION = 0.72       # gates ~0.72 of the way to the enemy (~55/140)
    ATTACK_AT_ZEALOTS = 4       # trickle out immediately, then flood

    async def on_start(self):
        self.attacking = False
        self.proxy = self.start_location.towards(
            self.enemy_start_locations[0],
            self.start_location.distance_to(self.enemy_start_locations[0])
            * self.PROXY_FRACTION,
        )
        self.proxy_builder = None

    async def on_step(self, iteration):
        if not self.townhalls:
            for u in self.units.of_type({UnitTypeId.ZEALOT, UnitTypeId.PROBE}):
                u.attack(self.enemy_start_locations[0])
            return
        nexus = self.townhalls.first
        await self.home_supply(nexus)
        await self.proxy_pylon()
        await self.proxy_gateways()
        await self.build_probes(nexus)
        await self.make_zealots()
        await self.chrono(nexus)
        await self.attack()

    def _proxy_pylons(self):
        return self.structures(UnitTypeId.PYLON).closer_than(20, self.proxy)

    def _proxy_gates(self):
        return self.structures(UnitTypeId.GATEWAY).closer_than(20, self.proxy)

    # --- keep one probe forward to build the proxy ---------------------------
    def _get_builder(self):
        if self.proxy_builder and self.proxy_builder.tag in self.workers.tags:
            return self.workers.by_tag(self.proxy_builder.tag)
        w = self.workers.gathering
        if w:
            self.proxy_builder = w.closest_to(self.proxy)
            return self.proxy_builder
        return None

    # --- proxy pylon at the enemy's doorstep (built ASAP) -------------------
    async def proxy_pylon(self):
        if self._proxy_pylons() or self.already_pending(UnitTypeId.PYLON) and not self.structures(UnitTypeId.PYLON):
            return
        # one proxy pylon powers all 4 gates
        if self._proxy_pylons().amount + self._pending_near(UnitTypeId.PYLON) >= 1:
            return
        if not self.can_afford(UnitTypeId.PYLON):
            return
        builder = self._get_builder()
        if not builder:
            return
        if builder.distance_to(self.proxy) > 12:
            builder.move(self.proxy)
            return
        loc = await self.find_placement(UnitTypeId.PYLON, self.proxy, max_distance=10)
        if loc:
            builder.build(UnitTypeId.PYLON, loc)

    def _pending_near(self, tid):
        # count structures of tid under construction near the proxy
        return sum(1 for s in self.structures(tid).closer_than(20, self.proxy)
                   if s.build_progress < 1.0)

    # --- 4 gateways at the proxy pylon, built in PARALLEL -------------------
    async def proxy_gateways(self):
        pylon = self._proxy_pylons().ready
        if not pylon:
            return
        started = self._proxy_gates().amount + self.already_pending(UnitTypeId.GATEWAY)
        if started >= self.NUM_GATEWAYS or not self.can_afford(UnitTypeId.GATEWAY):
            return
        # pull a fresh nearby worker for EACH gate (parallel construction) and
        # pre-stage extra probes forward so all 4 gates go down fast
        loc = await self.find_placement(UnitTypeId.GATEWAY, pylon.first.position,
                                        max_distance=10)
        if not loc:
            return
        # build with the nearest worker already forward (or the proxy builder);
        # don't pre-stage idle probes - that starved the mineral line and made
        # the flood too slow
        near = self.workers.closer_than(35, self.proxy)
        builder = (near.closest_to(loc) if near
                   else self._get_builder() or self.workers.closest_to(loc))
        if builder:
            builder.build(UnitTypeId.GATEWAY, loc)

    # --- home supply so we don't block (also a fallback warp field) ---------
    async def home_supply(self, nexus):
        if (
            self.supply_left < 3
            and self.supply_cap < 200
            and self.already_pending(UnitTypeId.PYLON) - self._pending_near(UnitTypeId.PYLON) < 1
            and self.can_afford(UnitTypeId.PYLON)
        ):
            await self.build(UnitTypeId.PYLON,
                             near=nexus.position.towards(self.game_info.map_center, 6))

    async def build_probes(self, nexus):
        if self.supply_workers >= self.TARGET_PROBES or not nexus.is_idle:
            return
        # never at the cost of the proxy gates
        if self._proxy_gates().amount < self.NUM_GATEWAYS and self.minerals < 200:
            return
        if self.can_afford(UnitTypeId.PROBE):
            nexus.train(UnitTypeId.PROBE)

    async def make_zealots(self):
        for gate in self._proxy_gates().ready.idle:
            if self.can_afford(UnitTypeId.ZEALOT):
                gate.train(UnitTypeId.ZEALOT)

    async def chrono(self, nexus):
        if nexus.energy < 50:
            return
        busy = [g for g in self._proxy_gates().ready if not g.is_idle]
        if busy:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, busy[0])
        elif not nexus.is_idle and self.supply_workers < self.TARGET_PROBES:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)

    async def attack(self):
        zealots = self.units(UnitTypeId.ZEALOT)
        if not self.attacking and zealots.amount >= self.ATTACK_AT_ZEALOTS:
            self.attacking = True
        if self.attacking:
            target = (self.enemy_structures.closest_to(self.proxy).position
                      if self.enemy_structures else self.enemy_start_locations[0])
            for z in zealots:
                z.attack(target)

    async def on_end(self, result: Result):
        print(f"FourGateZealotBot game ended: {result}")
