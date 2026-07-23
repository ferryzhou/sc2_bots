"""RandomSparringBot: Random race, random archetype.

Registers as Race.Random so the SC2 engine assigns the actual race at game
start. In on_start the bot reads its assigned race and randomly picks one of
the strategy_engine-driven archetype Specs of that race; from then on it *is*
that archetype (ArchetypeSparringBot's executor is driven entirely by SPEC).

One opponent, many looks: rush, timing push, or greed, in any race -- useful
for testing a bot's adaptability without knowing what's coming.

    python sparring/run.py --bot random

Set SPARRING_ARCHETYPE=<class name> (e.g. GreedyZerg2) to force the pick when
the assigned race matches -- handy for reproducing a specific game.
"""
import os
import random

from sc2.data import Race

from archetype_bot import (ArchetypeSparringBot, FourGate2, GreedyProtoss2,
                           GreedyTerran2, GreedyZerg2, MassLing2,
                           OneBaseStalker2, TwelvePool2)

ARCHETYPES = {
    Race.Protoss: [FourGate2, OneBaseStalker2, GreedyProtoss2],
    Race.Terran: [GreedyTerran2],
    Race.Zerg: [TwelvePool2, MassLing2, GreedyZerg2],
}


class RandomSparringBot(ArchetypeSparringBot):
    async def on_start(self):
        pool = ARCHETYPES[self.race]
        forced = os.environ.get("SPARRING_ARCHETYPE")
        pick = next((c for c in pool if c.__name__ == forced), None) or random.choice(pool)
        self.SPEC = pick.SPEC
        self.archetype = pick.__name__
        print(f"RandomSparringBot: race={self.race.name} archetype={self.archetype}")
