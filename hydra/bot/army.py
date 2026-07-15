"""army: the combat executor -- defend, attack, harass, or hold per the plan.

Reads ``plan.combat_stance`` and the strategy_engine's engagement/defense reads
and translates them into orders. Defending the economy always comes first; beyond
that the stance decides whether we push the deathball, peel off a harass
detachment, or hold and keep macroing. It also runs the early overlord/drone
scout so perception has something to feed the classifier, and handles the small
amount of unit-specific control Zerg needs (lurker burrow, keeping overlords
safe).
"""

from __future__ import annotations

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U

from .planner import ATTACK, DEFEND, HARASS, HOLD

ARMY = {U.ZERGLING, U.BANELING, U.ROACH, U.RAVAGER, U.HYDRALISK, U.LURKERMP,
        U.LURKERMPBURROWED, U.MUTALISK, U.CORRUPTOR, U.BROODLORD, U.ULTRALISK,
        U.INFESTOR}
# fast units used for harassment detachments
RAIDERS = {U.ZERGLING, U.MUTALISK}


class Army:
    def __init__(self):
        self.scout_sent = False
        self.scout_tag = None
        self._committed = False   # attack-commit latch (deathball discipline)

    def step(self, bot, plan, advice) -> None:
        self._scout(bot)
        self._overlord_safety(bot)

        army = bot.units.of_type(ARMY)
        if not army:
            self._committed = False
            return

        # 1) defend a threatened base no matter the stance
        threat = self._threatened_base(bot)
        if threat is not None:
            self._defend(bot, plan, army, threat)
            return

        # 2) commit latch: once we commit the army we see the fight through until
        # it's spent below the regroup line, rather than dribbling units forward
        # and pulling back every time the read flickers (which feeds them away).
        if plan.combat_stance == ATTACK and not self._committed:
            if bot.supply_army >= 0.9 * plan.attack_supply or bot.supply_used >= 185:
                self._committed = True
        if self._committed and bot.supply_army < plan.regroup_supply:
            self._committed = False

        if self._committed:
            self._attack(bot, army)
        elif plan.combat_stance == HARASS:
            self._harass(bot, army)
        else:  # DEFEND / HOLD -- rally home and rebuild
            self._hold(bot, army)

    # ------------------------------------------------------------------ modes
    def _defend(self, bot, plan, army, base) -> None:
        enemies = bot.enemy_units.closer_than(30, base)
        target = enemies.closest_to(base) if enemies else base
        tpos = target.position if hasattr(target, "position") else target
        for u in army:
            if u.type_id in (U.LURKERMP, U.LURKERMPBURROWED):
                self._lurker(bot, u, tpos, hold=True)
            else:
                u.attack(tpos)
        # Queens hold the base too rather than idling on inject duty while it
        # burns -- they have a strong ground/air attack at close range.
        for q in bot.units(U.QUEEN).closer_than(20, base):
            q.attack(tpos)
        if enemies and plan.pull_workers:
            self._pull_workers(bot, base, tpos)

    def _attack(self, bot, army) -> None:
        # concentrate, then commit -- feeding units piecemeal into a defence loses
        center = army.center
        target = self._attack_target(bot)
        concentrated = army.closer_than(12, center).amount >= 0.6 * army.amount
        staging = self._staging(bot)
        for u in army:
            if u.type_id in (U.LURKERMP, U.LURKERMPBURROWED):
                self._lurker(bot, u, target, hold=False)
            elif concentrated or bot.supply_army >= 60:
                u.attack(target)
            elif u.distance_to(staging) > 8:
                u.move(staging)
            else:
                u.attack(target)

    def _harass(self, bot, army) -> None:
        raiders = army.of_type(RAIDERS)
        main = army - raiders
        if raiders:
            tgt = self._harass_target(bot)
            for u in raiders:
                u.attack(tgt)
        for u in main:
            self._rally_unit(bot, u)

    def _hold(self, bot, army) -> None:
        for u in army:
            if u.type_id in (U.LURKERMP, U.LURKERMPBURROWED):
                self._lurker(bot, u, self._rally(bot), hold=True)
            else:
                self._rally_unit(bot, u)

    # ----------------------------------------------------------------- helpers
    def _rally_unit(self, bot, u) -> None:
        rally = self._rally(bot)
        if u.distance_to(rally) > 7:
            u.move(rally)

    def _lurker(self, bot, u, target, hold: bool) -> None:
        near = bot.enemy_units.closer_than(9, u)
        burrowed = u.type_id == U.LURKERMPBURROWED
        if near and not burrowed:
            u(AbilityId.BURROWDOWN_LURKER)
        elif not near and burrowed and not hold:
            u(AbilityId.BURROWUP_LURKER)
        elif not burrowed:
            u.attack(target)

    def _staging(self, bot):
        if bot.townhalls:
            base = bot.townhalls.closest_to(bot.enemy_start_locations[0])
            return base.position.towards(bot.enemy_start_locations[0], 14)
        return bot.start_location

    def _rally(self, bot):
        if bot.townhalls:
            base = bot.townhalls.closest_to(bot.enemy_start_locations[0])
            return base.position.towards(bot.game_info.map_center, 7)
        return bot.start_location

    def _attack_target(self, bot):
        if bot.enemy_structures:
            return bot.enemy_structures.closest_to(bot.units.of_type(ARMY).center).position
        if bot.enemy_units:
            return bot.enemy_units.closest_to(bot.start_location).position
        return bot.enemy_start_locations[0]

    def _harass_target(self, bot):
        # aim at the enemy economy: a townhall / worker line if we can see one
        halls = bot.enemy_structures.of_type(
            {U.NEXUS, U.HATCHERY, U.LAIR, U.HIVE, U.COMMANDCENTER,
             U.ORBITALCOMMAND, U.PLANETARYFORTRESS})
        if halls:
            return halls.furthest_to(bot.start_location).position
        return self._attack_target(bot)

    def _threatened_base(self, bot):
        for th in bot.townhalls:
            if bot.enemy_units.filter(lambda u: u.can_attack and u.distance_to(th) < 28):
                return th
        return None

    def _pull_workers(self, bot, base, target) -> None:
        drones = bot.workers.closer_than(18, base)
        n_fight = max(0, drones.amount - 6)
        for d in drones[:n_fight]:
            d.attack(target)

    def _overlord_safety(self, bot) -> None:
        # keep overlords near home unless scouting; they die to any anti-air
        if bot.enemy_memory.get("enemy_has_air"):
            home = bot.start_location.towards(bot.game_info.map_center, -6)
            for ov in bot.units(U.OVERLORD):
                if ov.tag != self.scout_tag and ov.distance_to(home) > 18:
                    ov.move(home)

    def _scout(self, bot) -> None:
        # send the first overlord toward the enemy for an early read
        if not self.scout_sent:
            overlords = bot.units(U.OVERLORD)
            if overlords:
                ov = overlords.first
                ov.move(bot.enemy_start_locations[0].towards(bot.game_info.map_center, 12))
                self.scout_tag = ov.tag
                self.scout_sent = True
        # a drone poke a bit later fills in the base scout
        if bot.time > 75 and bot.workers.amount > 14 and not getattr(self, "_drone_scouted", False):
            self._drone_scouted = True
            bot.workers.random.move(bot.enemy_start_locations[0])
