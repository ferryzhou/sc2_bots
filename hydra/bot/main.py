"""HydraBot: an adaptive Zerg bot that switches between five strategies.

Architecture (one shared brain, generic executors):

    on_step:  perceive -> advise (strategy_engine) -> select strategy ->
              plan (profile + advice -> ExecutionPlan) -> execute (macro/tech/army)

The five strategies (cheese, timing, standard, greedy, turtle) live as
declarative profiles in ``zerg_strategies.yml``. The ``StrategySelector`` chooses
one from the engine's opponent read and switches mid-game; the ``Planner``
turns the chosen profile plus the live state into a fresh ``ExecutionPlan`` every
step, so behaviour is fully dynamic. The macro/tech/army executors are generic --
they carry out whatever plan they're given and contain no strategy of their own.

Nothing about "which strategy" is hard-coded in the executors: to change how the
bot plays, edit the strategy library or the planner's adaptation, not the
low-level code.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from loguru import logger
from sc2.bot_ai import BotAI
from sc2.data import Race, Result
from sc2.ids.unit_typeid import UnitTypeId as U

from strategy_engine import StrategicAdvisor, GameState

from bot.compat import patch_creation_abilities
from bot.perception import Perception
from bot.strategies import load_library
from bot.selector import StrategySelector
from bot.planner import Planner
from bot.macro import Macro
from bot.tech import Tech
from bot.army import Army

# Structures that count as "production" and "tech" for the engine's investment
# and idle-resource reasoning (Zerg produces army from larva, so production
# capacity is really larva-generation: hatcheries + queens).
DETECTORS = {U.OVERSEER, U.SPORECRAWLER}
HARASS_UNITS = {U.MUTALISK, U.ZERGLING}


class HydraBot(BotAI):
    def __init__(self, strategy: str | None = None, lock: bool = False):
        super().__init__()
        self.enemy_memory: dict = {}
        self.perception = Perception()
        self.advisor = StrategicAdvisor()
        self.library = load_library()
        initial = strategy or os.environ.get("HYDRA_STRATEGY") or "MacroRoachHydra"
        if initial not in self.library:
            initial = "MacroRoachHydra"
        # Did a human force the opening? If so, opponent-intel must not override it.
        self._forced_initial = bool(strategy) or bool(os.environ.get("HYDRA_STRATEGY"))
        locked = lock or bool(os.environ.get("HYDRA_LOCK"))
        self.selector = StrategySelector(self.library, initial, locked=locked)
        self.planner = Planner()
        self.macro = Macro()
        self.tech = Tech()
        self.army = Army()
        self._last_log = 0.0

    async def on_start(self) -> None:
        self.client.game_step = 4  # responsive without being wasteful
        # 4.10 client: register creation abilities for dummy/rich unit ids so
        # already_pending() can't crash the bot mid-game.
        patch_creation_abilities(self)
        await self._apply_opponent_intel()

    async def _apply_opponent_intel(self) -> None:
        """Pick the *starting* strategy from a pre-game prior on the opponent.

        On the AI Arena ladder the opponent is identified only by a stable
        ``game_display_id`` UUID passed as ``--OpponentId`` (our ladder wrapper
        stores it on ``self.opponent_id``); locally the harness passes the bot
        name. ``opponent_intel`` resolves either form to a known profile and
        recommends one of our five strategies. The mid-game ``StrategySelector``
        still refines this by live scouting -- the prior just sets a better
        opening than a blind default (see OPPONENTS.md, "load the prior first").

        Fully guarded: any failure leaves the default opening untouched (a crash
        here would forfeit the game).
        """
        if self._forced_initial:
            return
        opp_id = getattr(self, "opponent_id", None)
        try:
            from opponent_intel import recommend_for
            rec = recommend_for(opp_id)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"[opponent_intel] unavailable ({exc}); using default opening")
            return
        if rec.hydra_strategy != self.selector.current.name:
            self.selector.set_initial(rec.hydra_strategy)
        logger.info(f"[opponent_intel] {rec.summary()}")
        try:
            tag = rec.name if rec.known else "unknown opponent"
            await self.chat_send(
                f"(scouting) vs {tag}: opening {rec.hydra_strategy} [{rec.opp_style}]")
        except Exception:  # pragma: no cover - chat is best-effort
            pass

    async def on_step(self, iteration: int) -> None:
        if not self.townhalls:
            for drone in self.workers:
                drone.attack(self.enemy_start_locations[0])
            return

        # keep drones on minerals AND gas (3 per extractor) -- without this,
        # extractors sit unmanned and the army starves for gas
        await self.distribute_workers(resource_ratio=2)

        # perceive -> advise -> select -> plan
        self.perception.update(self)
        advice = self.advisor.advise(self._game_state())
        profile = self.selector.select(self, advice)
        plan = self.planner.plan(self, profile, advice)

        # execute: macro spends larva first (supply + drones), army gets the rest
        larvae = list(self.larva)
        await self.macro.step(self, plan, larvae)
        await self.tech.step(self, plan, larvae)
        self.army.step(self, plan, advice)

        if self.time - self._last_log > 45:
            self._last_log = self.time
            sc = self.state.score
            gas_workers = sum(g.assigned_harvesters for g in self.gas_buildings.ready)
            logger.info(
                f"[{int(self.time)}s] strat={profile.name}({profile.stance.value}) "
                f"stance={plan.combat_stance} drones={self.supply_workers} "
                f"army={int(self.supply_army)} bases={self.townhalls.amount} "
                f"| minc={int(sc.collection_rate_minerals)} gasc={int(sc.collection_rate_vespene)} "
                f"gasW={gas_workers} idleW={self.workers.idle.amount} "
                f"bank={self.minerals}/{self.vespene} gasBld={self.gas_buildings.amount} "
                f"| opp={advice.classification.archetype.value}"
            )

    async def on_end(self, result: Result) -> None:
        logger.info(f"HydraBot game ended: {result} "
                    f"(final strategy {self.selector.current.name})")

    # ------------------------------------------------------------------ brain
    def _game_state(self) -> GameState:
        """Build the engine's GameState from the live bot + scouted memory,
        adding the Zerg-specific reads the generic adapter can't infer."""
        mem = dict(self.enemy_memory)
        er = getattr(self, "enemy_race", None)
        mem["enemy_race"] = er.name if er is not None and hasattr(er, "name") else None

        state = GameState.from_bot(self, mem)
        # Zerg "production" is larva generation: hatcheries + queens (injects).
        state.production_structures = self.townhalls.amount + self.units(U.QUEEN).amount
        # larva sitting unused with money is our idle-production signal
        state.idle_production = self.larva.amount if self.minerals > 200 else 0
        state.tech_structures = self.structures.of_type(
            {U.LAIR, U.HIVE, U.HYDRALISKDEN, U.LURKERDENMP, U.SPIRE, U.GREATERSPIRE,
             U.INFESTATIONPIT, U.ULTRALISKCAVERN, U.ROACHWARREN, U.BANELINGNEST}
        ).amount
        state.upgrade_structures = self.structures(U.EVOLUTIONCHAMBER).ready.amount
        state.idle_upgrade_structures = self.structures(U.EVOLUTIONCHAMBER).ready.idle.amount
        state.upgrades_done = len(self.state.upgrades) if self.state.upgrades else 0
        state.have_detection = (
            self.units(U.OVERSEER).amount + self.structures(U.SPORECRAWLER).ready.amount > 0
        )
        state.has_harass_units = self.units.of_type(HARASS_UNITS).amount > 0
        # bases without a spine/spore or nearby army are exposed
        state.undefended_expansions = sum(
            1 for th in self.townhalls
            if not self.structures.of_type({U.SPINECRAWLER, U.SPORECRAWLER}).closer_than(10, th)
            and not self.units.of_type(HARASS_UNITS | {U.ROACH, U.HYDRALISK}).closer_than(12, th)
        )
        return state
