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

from strategy_engine import Archetype
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
        # active. The bot CHANGES PATH reactively -- as soon as SCOUTING says the
        # opponent is doing something the greedy build isn't safe against (a rush
        # opening, an all-in/timing read from the advisor, or a live emergency) it
        # abandons the planned build and hands the game to the adaptive/defensive
        # managers. This fires on scouted *intent* (earlier than the army arriving
        # at the door), which is the whole point of scouting. With no threat, it
        # proceeds on the planned build.
        if self.build_script is not None and self.build_script.active:
            reason = self._threat_scouted(advice)
            if reason is not None:
                self.build_script.active = False
                print(f"[{int(self.time)}s] threat scouted ({reason}) -> abandoning "
                      f"scripted build '{self.build_script.build.title}', going adaptive")
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

    # scouted opponent openings that a greedy macro build must react to
    REACTIVE_OPENINGS = {
        "zerg_pool_rush", "protoss_proxy", "protoss_gate_allin",
        "protoss_forge_fast", "terran_proxy_rax", "terran_2rax",
    }

    def _threat_scouted(self, advice):
        """Why to abandon the scripted build now (perception-driven), or None.

        Ordered from earliest scouting signal to latest: the opponent's opening
        family (from classify_opening), the advisor's archetype read (all-in /
        timing from the scouted economy/army split), then the live emergency.
        """
        if self.enemy_opening in self.REACTIVE_OPENINGS:
            return self.enemy_opening
        arch = advice.classification.archetype
        if arch in (Archetype.CHEESE_ALLIN, Archetype.TIMING_ATTACK):
            return arch.value
        if advice.defense.emergency:
            return "emergency"
        return None

    async def on_end(self, result: Result):
        print(f"AthenaBot game ended: {result}")
