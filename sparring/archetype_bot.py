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
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId as U

from strategy_engine.macro import recommend_macro
from strategy_engine.openings import OPENINGS, BuildStep, Opening, OpeningExecutor, Placement
from strategy_engine.principles import Investment, recommend_investment
from strategy_engine.state import GameState

TOWNHALL = {U.DRONE: U.HATCHERY, U.PROBE: U.NEXUS, U.SCV: U.COMMANDCENTER}


def custom(race: str, *structures: str) -> Opening:
    steps = [BuildStep(i, s, Placement.MAIN, None, 100) for i, s in enumerate(structures)]
    return Opening("custom", race, 0, steps, None, None, 0, {}, {})


@dataclass
class Spec:
    opening: Opening
    worker: U
    supply: U
    army: U
    max_workers: int   # the archetype's own economy plan (cutoff or greed target)
    max_bases: int
    attack_at: int     # attack when this many army units exist
    queens: int = 0    # zerg macro archetypes: queens for larva injects
    production: U = None  # greedy archetypes: structure recommend_macro scales


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
        await self.distribute_workers()  # keep gas geysers actually worked
        state = GameState(
            game_time=self.time, worker_count=int(self.supply_workers),
            base_count=self.townhalls.amount, minerals=self.minerals,
            vespene=self.vespene, supply_used=int(self.supply_used),
            supply_cap=int(self.supply_cap), supply_left=int(self.supply_left),
            army_supply=self.supply_used - self.supply_workers,
            production_structures=(self.structures(spec.production).amount
                                   if spec.production else 0) or self.townhalls.amount,
        )
        inv = recommend_investment(state)

        # 1. supply, when the library's gate fires (pending allowance scales
        # with production so a 200-supply race is never supply-blocked)
        if (inv.top == Investment.SUPPLY and self.can_afford(spec.supply)
                and self.already_pending(spec.supply) < 1 + state.production_structures // 3):
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
            elif step.structure in ("Assimilator", "Extractor", "Refinery"):
                free = self.vespene_geyser.closer_than(12, th).filter(
                    lambda g: not self.gas_buildings.closer_than(1.0, g))
                if free and self.workers:
                    self.workers.random.build_gas(free.first)
            else:
                await self.build(U[step.structure.upper()],
                                 near=th.position.towards(self.game_info.map_center, 5))
        # 3. macro archetypes: expand (any race). Expansions are the income
        # ramp, so greedy specs keep two in flight; others one at a time.
        elif (self.townhalls.amount + self.already_pending(TOWNHALL[spec.worker])
                < spec.max_bases
                and self.can_afford(TOWNHALL[spec.worker])
                and self.already_pending(TOWNHALL[spec.worker])
                < (2 if spec.production else 1)):
            await self.expand_now()
        # 4. greedy archetypes: production count set by the library
        # (recommend_macro scales it with bases, saturation, and float).
        # Reserve the bank for the next expansion until the base count is met
        # -- without this, production siphons the nexus/CC money and the
        # 200-supply race stalls on two bases.
        elif spec.production and self.can_afford(spec.production) and (
                self.townhalls.amount >= spec.max_bases or self.minerals > 450) and (
                self.structures(spec.production).amount
                + self.already_pending(spec.production)
                < recommend_macro(state, inv).target_production
                and self.already_pending(spec.production)
                < recommend_macro(state, inv).allow_parallel_build):
            await self.build(spec.production,
                             near=th.position.towards(self.game_info.map_center, 5))
        # 5. workers up to the spec's cap -- the archetype's own economy plan
        # governs (a rush cuts at 13-22; a greedy spec drones to 66+); the
        # library keeps the supply gate, opening, and production scaling.
        elif self.supply_workers < spec.max_workers:
            if zerg and self.larva and self.can_afford(spec.worker):
                # drain the whole inject burst, not one larva per frame
                need = min(spec.max_workers - int(self.supply_workers),
                           self.minerals // 50, int(self.supply_left))
                for larva in self.larva[:max(0, need)]:
                    larva.train(spec.worker)
            elif not zerg and self.can_afford(spec.worker):
                for t in self.townhalls.ready.idle:
                    t.train(spec.worker)
                    break
        # 6. zerg macro: queens (scaled to hatch count) + inject hygiene --
        # injects don't stack, so cast one fresh inject per un-injected hatch
        if spec.queens and self.structures(U.SPAWNINGPOOL).ready:
            want = min(spec.queens, self.townhalls.ready.amount)
            if self.units(U.QUEEN).amount + self.already_pending(U.QUEEN) < want:
                for h in self.townhalls.ready.idle:
                    if self.can_afford(U.QUEEN):
                        h.train(U.QUEEN)
                        break
            free = self.units(U.QUEEN).filter(lambda q: q.energy >= 25)
            for h in self.townhalls.ready.filter(
                    lambda h: not h.has_buff(BuffId.QUEENSPAWNLARVATIMER)):
                if not free:
                    break
                q = free.closest_to(h)
                q(AbilityId.EFFECT_INJECTLARVA, h)
                free = free.filter(lambda u: u.tag != q.tag)
        # 7. army with everything left, attack at the archetype's timing.
        # Greedy specs spend excess into army (float or near worker cap);
        # rushes spend everything, always.
        reserve = 450 if self.townhalls.amount < spec.max_bases else 300
        eco_first = spec.production and self.minerals < reserve and (
            self.supply_workers < spec.max_workers - 4)
        train_from = spec.production or U.GATEWAY
        if eco_first:
            pass
        elif zerg and self.structures(U.SPAWNINGPOOL).ready:
            for larva in self.larva:
                if self.can_afford(spec.army) and self.supply_left > 0:
                    larva.train(spec.army)
        elif not zerg and self.tech_requirement_progress(spec.army) == 1:
            for g in self.structures(train_from).ready.idle:
                if self.can_afford(spec.army) and self.supply_left > 1:
                    g.train(spec.army)
            busy = self.structures(train_from).ready.filter(lambda g: not g.is_idle)
            for n in self.townhalls.filter(lambda n: n.energy >= 50):
                tgt = busy.first if busy else (n if not n.is_idle else None)
                if tgt:  # boost army production, else our own probe queue
                    n(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, tgt)
                    break
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


class OneBaseStalker2(ArchetypeSparringBot):
    """OneBaseStalkerBot (aiarena ~1614 Elo): one-base 4-gate mass stalker.

    Fingerprint from bot_profiles/OneBaseStalkerBot: 22 probes, 4 gateways,
    2 assimilators, 1 cybernetics core, no expansion, ~22 stalkers, push ~5-6min.
    """
    SPEC = Spec(custom("Protoss", "Pylon", "Gateway", "Assimilator", "CyberneticsCore",
                       "Assimilator", "Gateway", "Pylon", "Gateway", "Gateway"),
                U.PROBE, U.PYLON, U.STALKER, max_workers=22, max_bases=1, attack_at=8)


# Greedy archetypes: race to 200 supply (~9-11 min), army only from excess.
# Openings are the mined pro expand-first families (analysis/OPENING_PATTERNS.md:
# gate_expand / rax_expand / hatch_first, each ~100% expand-in-window across 66
# pro replays); expansion count, production scaling (recommend_macro), and the
# supply gate come from the library. Attack only near max.

class GreedyProtoss2(ArchetypeSparringBot):
    SPEC = Spec(OPENINGS["protoss_gate_expand"], U.PROBE, U.PYLON, U.ZEALOT,
                max_workers=66, max_bases=4, attack_at=50, production=U.GATEWAY)


class GreedyTerran2(ArchetypeSparringBot):
    SPEC = Spec(OPENINGS["terran_rax_expand"], U.SCV, U.SUPPLYDEPOT, U.MARINE,
                max_workers=66, max_bases=4, attack_at=100, production=U.BARRACKS)


class GreedyZerg2(ArchetypeSparringBot):
    # Gasless variant of the mined hatch_first family: greedyz spends zero gas
    # (drone/ling/hatch/queen are all minerals), so the family's Extractor is
    # dead money at the most timing-critical moment -- drop it and bake the
    # 3rd hatchery into the opening to pull the larva engine forward.
    SPEC = Spec(custom("Zerg", "Hatchery", "SpawningPool", "Hatchery"),
                U.DRONE, U.OVERLORD, U.ZERGLING,
                max_workers=75, max_bases=6, attack_at=150, queens=8,
                production=U.HATCHERY)  # macro hatcheries = larva engines
