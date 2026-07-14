"""Army: defend, and attack or hold based on the advisor's engagement read.

Acts on the combat/engagement decision from strategy_engine: defend the economy
first, then attack when the engagement is favorable / the counter stance is
aggressive / we are maxed, otherwise hold at a rally and keep macroing. Also runs
an early probe scout so perception has something to feed the classifier.
"""

from sc2.ids.unit_typeid import UnitTypeId as U
from strategy_engine import Engagement

ARMY = {U.ZEALOT, U.STALKER, U.IMMORTAL, U.ARCHON, U.ADEPT, U.SENTRY,
        U.HIGHTEMPLAR, U.DARKTEMPLAR, U.COLOSSUS}


class Army:
    def __init__(self):
        self.scout_tag = None
        self.scout_sent = False

    def step(self, bot, advice):
        self._scout(bot)
        army = bot.units.of_type(ARMY)
        if not army:
            self._observer(bot, army)
            return

        rally = self._rally(bot)

        # 1) defend: enemy units in/near any base
        threat_base = self._threatened_base(bot)
        if threat_base is not None:
            enemies = bot.enemy_units.closer_than(30, threat_base)
            target = enemies.closest_to(threat_base) if enemies else threat_base
            for u in army:
                u.attack(target.position if hasattr(target, "position") else target)
            self._observer(bot, army)
            return

        # 2) attack or hold from the engagement read
        if self._should_attack(bot, advice, army):
            target = self._attack_target(bot)
            for u in army:
                u.attack(target)
        else:
            for u in army:
                if u.distance_to(rally) > 8:
                    u.move(rally)
        self._observer(bot, army)

    def _should_attack(self, bot, advice, army):
        eng = advice.engagement.verdict
        # Committed all-in defense: never leave home while a real all-in is live.
        if advice.investment.posture == "safe" and bot.time < 300 and bot.supply_army < 25:
            return False
        if bot.supply_used >= 175:            # near max -- move out before we cap
            return True
        if eng == Engagement.ENGAGE:
            return True
        if eng == Engagement.AVOID and bot.supply_army < 30:
            return False
        if advice.counter.posture == "aggressive" and army.amount >= 10:
            return True
        # Otherwise take the map with a healthy army rather than turtling forever.
        if bot.supply_army >= 35:
            return True
        return False

    def _attack_target(self, bot):
        if bot.enemy_structures:
            return bot.enemy_structures.closest_to(bot.units.of_type(ARMY).center).position
        if bot.enemy_units:
            return bot.enemy_units.closest_to(bot.start_location).position
        return bot.enemy_start_locations[0]

    def _rally(self, bot):
        if bot.townhalls:
            base = bot.townhalls.closest_to(bot.enemy_start_locations[0])
            return base.position.towards(bot.game_info.map_center, 8)
        return bot.start_location

    def _threatened_base(self, bot):
        for th in bot.townhalls:
            if bot.enemy_units.filter(lambda u: u.can_attack and u.distance_to(th) < 30):
                return th
        return None

    def _observer(self, bot, army):
        obs = bot.units(U.OBSERVER)
        if not obs:
            return
        target = army.center if army else bot.start_location
        for o in obs:
            if o.distance_to(target) > 10:
                o.move(target)

    def _scout(self, bot):
        # send one early probe to the enemy base to reveal the opening
        if not self.scout_sent and bot.time > 20 and bot.workers.amount > 12:
            probe = bot.workers.random
            probe.move(bot.enemy_start_locations[0])
            self.scout_tag = probe.tag
            self.scout_sent = True
        # keep the scout circling the enemy base if alive
        if self.scout_tag is not None:
            scout = bot.workers.find_by_tag(self.scout_tag)
            if scout and scout.is_idle:
                scout.move(bot.enemy_start_locations[0])
