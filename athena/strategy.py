"""Strategy: bridge the bot to strategy_engine and expose one Advice per step.

Builds a GameState from the live bot plus the scouted enemy_memory, augments it
with a few Protoss-specific reads (detection on hand, composition vs. the enemy
race), and returns the advisor's Advice for the managers to act on.
"""

import os
import sys

# make the repo-root strategy_engine importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.data import Race

from strategy_engine import StrategicAdvisor, GameState

DETECTORS = {U.OBSERVER, U.PHOTONCANNON}


class Strategy:
    def __init__(self):
        self.advisor = StrategicAdvisor()

    def advise(self, bot):
        mem = dict(getattr(bot, "enemy_memory", {}) or {})

        # enemy race (for proactive rush insurance in the library)
        er = getattr(bot, "enemy_race", None)
        mem["enemy_race"] = er.name if er is not None and hasattr(er, "name") else None

        # detection on hand?
        mem["have_detection"] = (
            bot.units(U.OBSERVER).amount + bot.structures(U.PHOTONCANNON).ready.amount > 0
        )
        # composition read: mass-light Zerg wants splash; flag unfavorable if we
        # are stalker-heavy with no splash vs Zerg (the lishimin failure mode).
        if bot.enemy_race == Race.Zerg:
            splash = (bot.units(U.COLOSSUS).amount + bot.units(U.HIGHTEMPLAR).amount
                      + bot.units(U.ARCHON).amount)
            zealots = bot.units(U.ZEALOT).amount
            stalkers = bot.units(U.STALKER).amount
            mem["composition_favorable"] = (splash > 0 or zealots >= stalkers)

        state = GameState.from_bot(bot, mem)
        # production/idle-resource context the adapter can't see
        state.production_structures = (
            bot.structures(U.GATEWAY).amount + bot.structures(U.WARPGATE).amount
            + bot.structures(U.ROBOTICSFACILITY).amount + bot.structures(U.STARGATE).amount
        )
        state.idle_production = sum(
            1 for g in (bot.structures(U.GATEWAY).ready
                        | bot.structures(U.ROBOTICSFACILITY).ready) if g.is_idle
        )
        state.upgrade_structures = bot.structures(U.FORGE).ready.amount
        state.upgrades_done = bot.state.upgrades and len(bot.state.upgrades) or 0
        state.has_harass_units = bot.units.of_type({U.ORACLE, U.PHOENIX, U.DARKTEMPLAR}).amount > 0
        return self.advisor.advise(state)
