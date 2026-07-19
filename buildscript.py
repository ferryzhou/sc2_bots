"""Shared build-script driver: follow a scripted opening across Protoss bots.

Reusable by any python-sc2 Protoss bot (AiurBot, AthenaBot, ...). It wraps the
sc2-free ``strategy_engine.build_guides.BuildExecutor`` (the decision engine --
what to build next, and whether it's due at the current supply/time) and
translates each ``BuildAction`` into concrete sc2 orders: place a structure,
train a unit, research an upgrade, take an expansion, or take gas.

The only bot-specific thing is *where* to place wall buildings, so that is
abstracted behind two hooks the bot implements:

    bot.bs_pylon_pos()  -> Point2 | None   # wall pylon spot (first pylon)
    bot.bs_wall_pos(i)  -> Point2 | None    # i-th wall building spot (0=gate, 1=core)

The script OWNS tech/army/expansion while active; a scouted all-in (emergency)
pauses it, and it hands the game back to the adaptive managers once complete or
past the opening window.
"""

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as Up

from strategy_engine import get_build, BuildExecutor

# tokens whose training producer isn't auto-resolved cleanly -> where to make them
GATEWAY_UNITS = {"ZEALOT", "STALKER", "ADEPT", "SENTRY", "HIGHTEMPLAR", "DARKTEMPLAR"}
ROBO_UNITS = {"IMMORTAL", "OBSERVER", "COLOSSUS", "WARPPRISM"}
STARGATE_UNITS = {"ORACLE", "PHOENIX", "VOIDRAY", "CARRIER", "TEMPEST"}


class BuildScript:
    def __init__(self, build_id, opening_seconds=300):
        self.build = get_build(int(build_id)) if build_id is not None else None
        self.executor = BuildExecutor(self.build) if self.build else None
        self.active = self.executor is not None
        self.opening_seconds = opening_seconds

    def _unit(self, token):
        try:
            return getattr(U, token)
        except AttributeError:
            return None

    def _upgrade(self, token):
        try:
            return getattr(Up, token)
        except AttributeError:
            return None

    def _have(self, bot):
        """Counts (built + pending) per token, so the executor advances."""
        have = {}
        for token in set(a.token for a in self.executor.actions if a.token):
            up = self._upgrade(token) if token in _UPGRADE_TOKENS else None
            if up is not None:
                have[token] = (1 if up in bot.state.upgrades
                               or bot.already_pending_upgrade(up) > 0 else 0)
                continue
            uid = self._unit(token)
            if uid is None:
                continue
            count = (bot.structures(uid).amount + bot.units(uid).amount
                     + bot.already_pending(uid))
            # A NEXUS build step means "expand" -- the starting base pre-exists
            # and is not a build step, so don't let it satisfy the first expand
            # (otherwise we never take the natural and later gas/steps deadlock).
            if token == "NEXUS":
                count = max(0, bot.townhalls.amount + bot.already_pending(U.NEXUS) - 1)
            have[token] = count
        # WarpGate morphs from Gateway -- count both toward GATEWAY
        if "GATEWAY" in have:
            have["GATEWAY"] += bot.structures(U.WARPGATE).amount
        return have

    async def step(self, bot, advice):
        if not self.active:
            return False
        # safety net: openings are ~3-5 min; if a step can't be met, don't stall
        # forever -- hand the game to the adaptive managers past the opening.
        if bot.time > self.opening_seconds:
            self.active = False
            return False
        # a scouted all-in pauses the script; the defense manager takes over
        if advice.defense.emergency:
            return True
        have = dict(self._have(bot))
        # Issue EVERY due + issuable step this tick (skipping blocked ones:
        # unaffordable, prereq/producer missing, no free geyser, can't expand),
        # tracking a running mineral/gas budget so we don't over-commit. Strict
        # serialization is the fidelity killer -- a slow step (3rd gas waiting on
        # the natural) otherwise cascade-delays everything after it.
        spent_m = spent_v = 0
        pending = False
        issued = set()
        for action, key, need in self.executor._required:
            if have.get(key, 0) >= need:
                continue
            pending = True
            if key in issued or not self._due(action, bot):
                continue
            cost = self._cost(bot, action)
            if cost is None:
                continue
            if bot.minerals - spent_m < cost[0] or bot.vespene - spent_v < cost[1]:
                continue
            if await self._issue(bot, action):
                spent_m += cost[0]
                spent_v += cost[1]
                issued.add(key)
        if not pending:
            self.active = False
        return True

    def _cost(self, bot, action):
        ent = (self._upgrade(action.token) if action.action == "research"
               else self._unit(action.token))
        if ent is None:
            return None
        c = bot.calculate_cost(ent)
        return (c.minerals, c.vespene)

    @staticmethod
    def _due(action, bot):
        # fire at the EARLIER of the supply or time benchmark (max timing
        # fidelity); affordability still gates the actual issue below.
        s, t = action.at_supply, action.at_second
        s_ok = s is None or bot.supply_used >= s
        t_ok = t is None or bot.time >= t
        return (s_ok or t_ok) if (s is not None and t is not None) else (s_ok and t_ok)

    async def _issue(self, bot, action):
        """Issue one order; return True iff an order was actually placed."""
        if action.action == "research":
            up = self._upgrade(action.token)
            if up is None or not bot.can_afford(up) or bot.already_pending_upgrade(up):
                return False
            for s in _RESEARCH_FROM.get(action.token, []):
                st = bot.structures(getattr(U, s)).ready.idle
                if st:
                    st.first.research(up)
                    if action.chrono:
                        self._boost(bot, st.first)
                    return True
            return False
        uid = self._unit(action.token)
        if uid is None or not bot.can_afford(uid):
            return False
        if action.action == "build":     # structure
            return await self._build_structure(bot, uid, action.token)
        return self._train(bot, uid, action.token, action.chrono)

    async def _build_structure(self, bot, uid, token):
        if token == "NEXUS":             # a townhall step means "expand"
            if bot.already_pending(U.NEXUS):
                return False
            await bot.expand_now()
            return True
        if token == "ASSIMILATOR":       # gas goes on a geyser, not "near"
            return self._build_gas(bot)
        if not bot.structures(U.PYLON).ready and token != "PYLON":
            return False
        if token != "PYLON" and bot.tech_requirement_progress(uid) < 1:
            return False
        near = self._placement(bot, token)
        if near is None:
            return False
        return bool(await bot.build(uid, near=near))

    def _placement(self, bot, token):
        if token == "PYLON":
            wp = bot.bs_pylon_pos()
            if wp is not None and not bot.structures(U.PYLON):
                return wp
            base = bot.townhalls.ready.random if bot.townhalls.ready else bot.townhalls.first
            return base.position.towards(bot.game_info.map_center, 6)
        if token == "GATEWAY":
            wp = bot.bs_wall_pos(0)
            return wp if wp is not None else self._near_pylon(bot)
        if token == "CYBERNETICSCORE":
            wp = bot.bs_wall_pos(1)
            return wp if wp is not None else self._near_pylon(bot)
        return self._near_pylon(bot)

    def _near_pylon(self, bot):
        if bot.structures(U.PYLON).ready:
            return bot.structures(U.PYLON).ready.random.position.towards(
                bot.game_info.map_center, 3)
        return bot.start_location.towards(bot.game_info.map_center, 5)

    def _build_gas(self, bot):
        for nexus in bot.townhalls.ready:
            for g in bot.vespene_geyser.closer_than(10, nexus):
                if not bot.gas_buildings.closer_than(1, g):
                    worker = bot.select_build_worker(g.position)
                    if worker:
                        worker.build_gas(g)
                        return True
        return False

    def _train(self, bot, uid, token, chrono=False):
        if token == "PROBE":
            for nx in bot.townhalls.ready.idle:
                nx.train(U.PROBE)
                return True
            return False
        if bot.tech_requirement_progress(uid) < 1:
            return False
        producers = None
        if token in GATEWAY_UNITS:
            producers = bot.structures(U.GATEWAY).ready.idle
        elif token in ROBO_UNITS:
            producers = bot.structures(U.ROBOTICSFACILITY).ready.idle
        elif token in STARGATE_UNITS:
            producers = bot.structures(U.STARGATE).ready.idle
        if producers:
            producers.first.train(uid)
            if chrono:
                self._boost(bot, producers.first)
            return True
        return False

    def _boost(self, bot, structure):
        for nx in bot.townhalls.ready:
            if nx.energy >= 50:
                nx(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, structure)
                return


_UPGRADE_TOKENS = {"WARPGATERESEARCH", "CHARGE", "BLINKTECH",
                   "PROTOSSGROUNDWEAPONSLEVEL1", "PROTOSSGROUNDARMORSLEVEL1"}
_RESEARCH_FROM = {
    "WARPGATERESEARCH": ["CYBERNETICSCORE"],
    "CHARGE": ["TWILIGHTCOUNCIL"], "BLINKTECH": ["TWILIGHTCOUNCIL"],
    "PROTOSSGROUNDWEAPONSLEVEL1": ["FORGE"], "PROTOSSGROUNDARMORSLEVEL1": ["FORGE"],
}
