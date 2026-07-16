"""AthenaBot: a modular, adaptive Protoss bot driven by strategy_engine.

Each step: perceive (scout -> enemy_memory) -> advise (strategy_engine) ->
act (economy, production, army). The managers are independent modules; the
advisor is the shared brain that makes the bot adapt to the game situation
(opponent archetype, engagement odds, investment priority, all-in detection).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sc2.bot_ai import BotAI
from sc2.data import Result

from perception import Perception
from strategy import Strategy
from economy import Economy
from production import Production
from army import Army
from wall import Wall


class AthenaBot(BotAI):
    def __init__(self):
        super().__init__()
        self.enemy_memory = {}
        self.enemy_opening = None
        self.force_build_id = None   # set by run.py --build; a spawningtool id
        self.build_script = None
        self.wall = Wall()
        self.perception = Perception()
        self.strategy = Strategy()
        self.economy = Economy()
        self.production = Production()
        self.army = Army()
        self.last_log = 0

    async def on_start(self):
        self.client.game_step = 4  # responsive without being wasteful
        if self.force_build_id is not None:
            from buildscript import BuildScript
            self.build_script = BuildScript(self.force_build_id)
            if self.build_script.active:
                print(f"reproducing build: {self.build_script.build.title}")

    async def on_step(self, iteration):
        if not self.townhalls:
            # last-ditch: everything attacks
            for w in self.workers:
                w.attack(self.enemy_start_locations[0])
            return

        await self.distribute_workers()
        self.perception.update(self)
        advice = self.strategy.advise(self)

        # scripted opening (--build): the script drives tech/army structure while
        # active. A scouted all-in makes the bot CHANGE PATH -- it abandons the
        # planned build for good and hands the game to the adaptive/defensive
        # managers (following a greedy pro build into a rush is how you die). With
        # no emergency, it proceeds on the planned build.
        if (self.build_script is not None and self.build_script.active
                and advice.defense.emergency):
            self.build_script.active = False
            print(f"[{int(self.time)}s] EMERGENCY -> abandoning scripted build "
                  f"'{self.build_script.build.title}', going adaptive")
        scripted = self.build_script is not None and self.build_script.active
        if scripted:
            await self.build_script.step(self, advice)
            await self.economy.step(self, advice, scripted=True)
        else:
            await self.economy.step(self, advice)
            await self.production.step(self, advice)
        self.army.step(self, advice)

        if self.time - self.last_log > 60:
            self.last_log = self.time
            print(f"[{int(self.time)}s] {advice.summary().splitlines()[0]} | "
                  f"opp={advice.classification.archetype.value} "
                  f"opening={self.enemy_opening or '?'} "
                  f"counter={advice.counter.posture} "
                  f"workers={self.supply_workers} army={int(self.supply_army)} bases={self.townhalls.amount}")

    async def on_end(self, result: Result):
        print(f"AthenaBot game ended: {result}")
