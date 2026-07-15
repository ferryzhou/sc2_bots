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
            tpos = target.position if hasattr(target, "position") else target
            for u in army:
                u.attack(tpos)
            # Pull workers to hold when the base is breached and we're thin -- or
            # when a rush hits before any cannon is ready (buys time on any map;
            # this is what saved the fastest deaths, e.g. PylonAIE_v4).
            no_defense = (bot.structures(U.PHOTONCANNON).ready.amount == 0
                          and bot.supply_army < 6)
            if enemies and (advice.defense.pull_workers
                            or (advice.defense.emergency and no_defense)):
                self._pull_workers(bot, threat_base, tpos)
            self._observer(bot, army)
            return

        # 2) attack or hold from the engagement read
        if self._should_attack(bot, advice, army):
            self._push(bot, army)
        else:
            # plug the ramp wall gap with a zealot while it's still open
            hold = bot.wall.hold_pos(bot)
            plug = None
            if hold is not None and bot.wall.gap_open(bot) and army:
                plug = army.closest_to(hold)
                plug.attack(hold)
            for u in army:
                if plug is not None and u.tag == plug.tag:
                    continue
                if u.distance_to(rally) > 8:
                    u.move(rally)
        self._observer(bot, army)

    def _should_attack(self, bot, advice, army):
        eng = advice.engagement.verdict
        # Library says hold at home (defending an all-in) -> never move out.
        if advice.defense.hold_position:
            return False
        if bot.supply_used >= 175:            # near max -- move out before we cap
            return True
        if eng == Engagement.ENGAGE:
            return True
        if eng == Engagement.AVOID and bot.supply_army < 30:
            return False
        if advice.counter.posture == "aggressive" and army.amount >= 10:
            return True
        # Take the map with a healthy army. Prefer having splash (colossus) vs
        # Zerg but don't turtle forever waiting for it -- being too passive just
        # lets the flood out-macro us. Push at 35; the deathball forms in _push.
        if bot.supply_army >= 35:
            return True
        return False

    def _push(self, bot, army):
        # Concentrate into a deathball, THEN commit -- feeding units piecemeal
        # into a ling flood is how the stalemate/loss happens. Gather at a forward
        # staging point until the ball is formed, then a-move the whole ball in.
        staging = self._staging(bot)
        center = army.center
        concentrated = army.closer_than(11, center).amount >= 0.6 * army.amount
        # Gather into a ball first, but commit outright with overwhelming force --
        # don't stall gathering while the enemy out-macros us.
        if concentrated or bot.supply_army >= 55:
            target = self._attack_target(bot)
            for u in army:
                u.attack(target)
        else:
            for u in army:
                u.move(staging)

    def _staging(self, bot):
        if bot.townhalls:
            base = bot.townhalls.closest_to(bot.enemy_start_locations[0])
            return base.position.towards(bot.enemy_start_locations[0], 14)
        return bot.start_location

    def _attack_target(self, bot):
        if bot.enemy_structures:
            return bot.enemy_structures.closest_to(bot.units.of_type(ARMY).center).position
        if bot.enemy_units:
            return bot.enemy_units.closest_to(bot.start_location).position
        return bot.enemy_start_locations[0]

    def _rally(self, bot):
        # Hold the ramp choke while we're on one base (defends the wall).
        hold = bot.wall.hold_pos(bot)
        if hold is not None and bot.townhalls.amount <= 1:
            return hold
        if bot.townhalls:
            base = bot.townhalls.closest_to(bot.enemy_start_locations[0])
            return base.position.towards(bot.game_info.map_center, 8)
        return bot.start_location

    def _threatened_base(self, bot):
        for th in bot.townhalls:
            if bot.enemy_units.filter(lambda u: u.can_attack and u.distance_to(th) < 30):
                return th
        return None

    def _pull_workers(self, bot, base, target):
        # Pull a portion of the probes at the breached base to fight; leave a few
        # mining so the economy isn't wiped by the pull itself.
        probes = bot.workers.closer_than(20, base)
        n_fight = max(0, probes.amount - 4)
        for probe in probes[:n_fight]:
            probe.attack(target)

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
