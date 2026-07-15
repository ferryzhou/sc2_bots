"""Follow a scripted opening (a spawningtool build) via strategy_engine.

When AthenaBot is launched with ``--build <id>`` it reproduces that exact
published build for the opening -- issuing each structure / unit / upgrade at its
supply benchmark via ``strategy_engine.build_guides.BuildExecutor`` -- then hands
the game back to the adaptive managers once the script is done.

The script OWNS tech/army structure decisions while active; the defense advisor
still overrides it (an emergency pauses the script so the anti-rush behaviour we
built isn't undone), and once the script completes the normal production manager
resumes.
"""

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId as Up

from strategy_engine import get_build, BuildExecutor

# tokens whose training producer isn't auto-resolved cleanly -> where to make them
GATEWAY_UNITS = {"ZEALOT", "STALKER", "ADEPT", "SENTRY", "HIGHTEMPLAR", "DARKTEMPLAR"}
ROBO_UNITS = {"IMMORTAL", "OBSERVER", "COLOSSUS", "WARPPRISM"}
STARGATE_UNITS = {"ORACLE", "PHOENIX", "VOIDRAY", "CARRIER", "TEMPEST"}


class BuildScript:
    def __init__(self, build_id):
        self.build = get_build(int(build_id)) if build_id is not None else None
        self.executor = BuildExecutor(self.build) if self.build else None
        self.active = self.executor is not None

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
        # safety net: openings are ~3-4 min; if a step can't be met, don't stall
        # forever -- hand the game to the adaptive managers past the opening.
        if bot.time > 300:
            self.active = False
            return False
        # a scouted all-in pauses the script; the defense manager takes over
        if advice.defense.emergency:
            return True
        have = self._have(bot)
        action = self.executor.next_action(have)
        if action is None:
            self.active = False
            return False
        if not BuildExecutor.is_due(action, bot.supply_used, bot.time):
            return True
        await self._issue(bot, action)
        return True

    async def _issue(self, bot, action):
        if action.action == "research":
            up = self._upgrade(action.token)
            if up is None or not bot.can_afford(up):
                return
            for s in _RESEARCH_FROM.get(action.token, []):
                st = bot.structures(getattr(U, s)).ready.idle
                if st:
                    st.first.research(up)
                    return
            return
        uid = self._unit(action.token)
        if uid is None or not bot.can_afford(uid):
            return
        if action.action == "build":     # structure
            await self._build_structure(bot, uid, action.token)
        else:                            # train a unit
            self._train(bot, uid, action.token)

    async def _build_structure(self, bot, uid, token):
        if token == "NEXUS":             # a townhall step means "expand"
            if not bot.already_pending(U.NEXUS):
                await bot.expand_now()
            return
        if token == "ASSIMILATOR":       # gas goes on a geyser, not "near"
            self._build_gas(bot)
            return
        if not bot.structures(U.PYLON).ready and token != "PYLON":
            return
        near = self._placement(bot, token)
        if near is not None:
            await bot.build(uid, near=near)

    def _placement(self, bot, token):
        wall = bot.wall
        if token == "PYLON":
            wp = wall.pylon_pos(bot)
            if wp is not None and not bot.structures(U.PYLON):
                return wp
            base = bot.townhalls.ready.random if bot.townhalls.ready else bot.townhalls.first
            return base.position.towards(bot.game_info.map_center, 6)
        if token == "GATEWAY":
            wp = wall.building_pos(bot, 0)
            return wp if wp is not None else self._near_pylon(bot)
        if token == "CYBERNETICSCORE":
            wp = wall.building_pos(bot, 1)
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

    def _train(self, bot, uid, token):
        if token == "NEXUS":
            return  # expansions are issued by _build_structure path below
        if token == "PROBE":
            for nx in bot.townhalls.ready.idle:
                nx.train(U.PROBE)
                return
            return
        producers = None
        if token in GATEWAY_UNITS:
            producers = bot.structures(U.GATEWAY).ready.idle
        elif token in ROBO_UNITS:
            producers = bot.structures(U.ROBOTICSFACILITY).ready.idle
        elif token in STARGATE_UNITS:
            producers = bot.structures(U.STARGATE).ready.idle
        if producers:
            producers.first.train(uid)


_UPGRADE_TOKENS = {"WARPGATERESEARCH", "CHARGE", "BLINKTECH",
                   "PROTOSSGROUNDWEAPONSLEVEL1", "PROTOSSGROUNDARMORSLEVEL1"}
_RESEARCH_FROM = {
    "WARPGATERESEARCH": ["CYBERNETICSCORE"],
    "CHARGE": ["TWILIGHTCOUNCIL"], "BLINKTECH": ["TWILIGHTCOUNCIL"],
    "PROTOSSGROUNDWEAPONSLEVEL1": ["FORGE"], "PROTOSSGROUNDARMORSLEVEL1": ["FORGE"],
}
