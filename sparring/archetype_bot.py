"""Sparring archetypes regenerated from strategy_engine, declaratively.

The hand-scripted mimics in this package are 50-175 lines of bespoke logic
each. Here the same three behaviors come from one generic executor driven by
strategy_engine -- OpeningExecutor walks the build, recommend_investment
orders supply/economy/army each frame -- plus a one-line Spec per archetype
holding the deliberate principle-violations that define it (worker cutoff,
attack timing). Validated headless against the hand-scripted fingerprints.
"""
from dataclasses import dataclass

from sc2.bot_ai import BotAI
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U

from strategy_engine.openings import OPENINGS, BuildStep, Opening, OpeningExecutor, Placement
from strategy_engine.principles import Investment, recommend_investment
from strategy_engine.state import GameState


def custom(race: str, *structures: str) -> Opening:
    steps = [BuildStep(i, s, Placement.MAIN, None, 100) for i, s in enumerate(structures)]
    return Opening("custom", race, 0, steps, None, None, 0, {}, {})


@dataclass
class Spec:
    opening: Opening
    worker: U
    supply: U
    army: U
    max_workers: int   # the rush-defining economy cutoff
    max_bases: int
    attack_at: int     # attack when this many army units exist
    queens: int = 0    # zerg macro archetypes: queens for larva injects


class ArchetypeSparringBot(BotAI):
    SPEC: Spec

    async def on_step(self, iteration: int):
        spec = self.SPEC
        army = self.units(spec.army)
        if not self.townhalls:
            for u in army:
                u.attack(self.enemy_start_locations[0])
            return
        th, zerg = self.townhalls.first, spec.worker == U.DRONE
        state = GameState(
            game_time=self.time, worker_count=int(self.supply_workers),
            base_count=self.townhalls.amount, minerals=self.minerals,
            vespene=self.vespene, supply_used=int(self.supply_used),
            supply_cap=int(self.supply_cap), supply_left=int(self.supply_left),
            army_supply=self.supply_used - self.supply_workers,
            production_structures=self.structures(U.GATEWAY).amount or self.townhalls.amount,
        )
        inv = recommend_investment(state)

        # 1. supply, when the library's gate fires
        if (inv.top == Investment.SUPPLY and self.can_afford(spec.supply)
                and self.already_pending(spec.supply) < (2 if zerg else 1)):
            if zerg and self.larva:
                self.larva.first.train(U.OVERLORD)
            elif not zerg:
                await self.build(spec.supply, near=th.position.towards(self.game_info.map_center, 6))
        # 2. the archetype's opening build (OpeningExecutor decides what's next)
        have = {s.structure: self.structures(U[s.structure.upper()]).amount
                + int(self.already_pending(U[s.structure.upper()]))
                - (1 if s.structure in ("Hatchery", "Nexus", "CommandCenter") else 0)
                for s, _ in self._exec()._required}
        step = self._exec().next_step(have)
        if step and self.can_afford(U[step.structure.upper()]):
            if step.structure in ("Hatchery", "Nexus", "CommandCenter"):
                await self.expand_now()
            else:
                await self.build(U[step.structure.upper()],
                                 near=th.position.towards(self.game_info.map_center, 5))
        # 3. workers while the library ranks economy top AND the spec allows it
        elif inv.top == Investment.ECONOMY and self.supply_workers < spec.max_workers:
            if zerg and self.larva and self.can_afford(spec.worker):
                self.larva.first.train(spec.worker)
            elif not zerg and th.is_idle and self.can_afford(spec.worker):
                th.train(spec.worker)
        # 4. macro archetypes: expand behind it (one expansion in flight at a time)
        elif (self.townhalls.amount < spec.max_bases and self.can_afford(U.HATCHERY)
                and not self.already_pending(U.HATCHERY)):
            await self.expand_now()
        # 5. zerg macro: queens + injects
        if spec.queens and self.structures(U.SPAWNINGPOOL).ready:
            if self.units(U.QUEEN).amount + self.already_pending(U.QUEEN) < spec.queens:
                for h in self.townhalls.ready.idle:
                    if self.can_afford(U.QUEEN):
                        h.train(U.QUEEN)
                        break
            for q in self.units(U.QUEEN).filter(lambda q: q.energy >= 25):
                q(AbilityId.EFFECT_INJECTLARVA, self.townhalls.ready.closest_to(q))
        # 6. army with everything left, attack at the archetype's timing
        if zerg and self.structures(U.SPAWNINGPOOL).ready:
            for larva in self.larva:
                if self.can_afford(spec.army) and self.supply_left > 0:
                    larva.train(spec.army)
        elif not zerg:
            for g in self.structures(U.GATEWAY).ready.idle:
                if self.can_afford(spec.army) and self.supply_left > 1:
                    g.train(spec.army)
        if army.amount >= spec.attack_at:
            target = (self.enemy_structures.random.position if self.enemy_structures
                      else self.enemy_start_locations[0])
            for u in army.idle:
                u.attack(target)

    def _exec(self) -> OpeningExecutor:
        if not hasattr(self, "_executor"):
            self._executor = OpeningExecutor(self.SPEC.opening)
        return self._executor


class FourGate2(ArchetypeSparringBot):
    SPEC = Spec(custom("Protoss", "Pylon", "Gateway", "Pylon", "Gateway", "Gateway", "Gateway"),
                U.PROBE, U.PYLON, U.ZEALOT, max_workers=18, max_bases=1, attack_at=6)


class TwelvePool2(ArchetypeSparringBot):
    SPEC = Spec(OPENINGS["zerg_pool_rush"],
                U.DRONE, U.OVERLORD, U.ZERGLING, max_workers=13, max_bases=1, attack_at=6)


class MassLing2(ArchetypeSparringBot):
    SPEC = Spec(OPENINGS["zerg_pool_first"],
                U.DRONE, U.OVERLORD, U.ZERGLING, max_workers=70, max_bases=4,
                attack_at=60, queens=4)
