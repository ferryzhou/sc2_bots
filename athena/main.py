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
        self.wall = Wall()
        self.perception = Perception()
        self.strategy = Strategy()
        self.economy = Economy()
        self.production = Production()
        self.army = Army()
        self.last_log = 0

    async def on_start(self):
        self.client.game_step = 4  # responsive without being wasteful

    async def on_step(self, iteration):
        if not self.townhalls:
            # last-ditch: everything attacks
            for w in self.workers:
                w.attack(self.enemy_start_locations[0])
            return

        await self.distribute_workers()
        self.perception.update(self)
        advice = self.strategy.advise(self)

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
