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

from strategy_engine import get_build, BuildExecutor, Want, plan_spend

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

    async def step(self, bot, advice, manage_workers=False, worker_cap=80):
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
        # Build a PRIORITY-ORDERED want list (build order), then let the generic
        # allocator (strategy_engine.spending) bank toward each blocking want so a
        # cheap step can't starve an expensive one. The one deviation from raw build
        # order is SUPPLY FIRST: a supply block stalls EVERYTHING, so when a block
        # looms the pylon is banked above probes and every build step -- worker/army
        # spam starving the pylon into a block is the opening's #1 tempo killer.
        # (Expansions are NOT force-sorted ahead of army: banking the whole Nexus
        # over all unit production leaves us defenceless into a timing attack. The
        # build order already places the natural early; the supply fix lets the
        # improved economy afford the later expansions on time on its own.)
        wants = []
        by_key = {}
        for action, key, need in self.executor._required:
            if have.get(key, 0) >= need or key in by_key:
                continue
            if key == "PYLON" or not self._due(action, bot) or not self._ready(bot, action):
                continue
            cost = self._cost(bot, action)
            if cost is None:
                continue
            wants.append(Want(key, cost[0], cost[1], blocking=True))
            by_key[key] = action
        if manage_workers and bot.townhalls.ready.idle and bot.supply_workers < worker_cap:
            # Where the auto-probe sits in priority. Pro guides list NO continuous
            # probe production -- the listed army/tech/expansion steps sit ON TOP of
            # an assumed baseline worker pump. So we reproduce that: the plan's
            # explicit ARMY steps (the pro's on-time Adepts) rank ABOVE the auto-probe
            # -- else worker spam starves them (we made 2 Adepts by 5:00 vs the pro's
            # 6). The probe is the BASELINE beneath them, but still above EXPANSIONS
            # so a 400 Nexus bank can't freeze the worker pump. At/above saturation it
            # drops to the very bottom and only spends the surplus.
            saturated = bot.supply_workers >= 16 * max(1, bot.townhalls.amount)
            army = [w for w in wants if by_key[w.key].action == "train"]
            other = [w for w in wants if by_key[w.key].action != "train"]  # tech + expansions
            probe = Want("PROBE", 50, 0, blocking=not saturated)
            # army > probe > tech/expansions (build order). At saturation the probe
            # drops to the bottom (surplus only). Keeping tech+expansions BELOW the
            # baseline probe protects the worker ramp -- the economy is the
            # foundation everything else is paid from.
            wants = (army + other + [probe]) if saturated else (army + [probe] + other)
        # supply: bank a pylon the instant a block looms, ABOVE everything -- probes
        # can't starve it into a block. (The driver owns supply while manage_workers,
        # so the bot's own supply manager sits out; a block stalls all production.)
        if manage_workers and self._supply_needed(bot):
            wants.insert(0, Want("PYLON", 100, 0, blocking=True))
        # pre-send the builder probe while banking a Nexus, so it's placed the
        # instant we can afford it (travel overlaps banking).
        if any(w.key == "NEXUS" for w in wants) and hasattr(bot, "bs_prep_expansion"):
            await bot.bs_prep_expansion()
        for key in plan_spend(bot.minerals, bot.vespene, wants):
            if key == "PROBE":
                bot.townhalls.ready.idle.first.train(U.PROBE)
            elif key == "PYLON":
                await self._build_structure(bot, U.PYLON, "PYLON")
            else:
                await self._issue(bot, by_key[key])
        if not any(have.get(k, 0) < n for _, k, n in self.executor._required):
            self.active = False
        return True

    @staticmethod
    def _supply_needed(bot):
        """True when a supply block is near: build a pylon well ahead of the cap,
        scaling the lead with how fast we can spend supply (more producers + bases
        raise the buffer, so a fast worker/warp-in ramp never runs into the cap)."""
        if bot.supply_cap >= 200 or not bot.townhalls.ready:
            return False
        producers = bot.structures(U.GATEWAY).amount + bot.structures(U.WARPGATE).amount
        buffer = 3 + 2 * (producers + bot.townhalls.ready.amount)
        pending = bot.already_pending(U.PYLON) * 8
        return bot.supply_left + pending <= buffer

    def _ready(self, bot, action):
        """Cheap prereq check: could this step be issued if we could afford it?
        Keeps unbuildable steps out of the allocator so they don't reserve (and
        needlessly pause probes) while waiting on a producer/prereq/geyser."""
        token = action.token
        if action.action == "research":
            up = self._upgrade(token)
            if up is None or bot.already_pending_upgrade(up):
                return False
            return any(bot.structures(getattr(U, s)).ready.idle
                       for s in _RESEARCH_FROM.get(token, []))
        uid = self._unit(token)
        if uid is None:
            return False
        if action.action == "build":
            if token == "NEXUS":
                return bot.already_pending(U.NEXUS) == 0
            if token == "ASSIMILATOR":
                return any(not bot.gas_buildings.closer_than(1, g)
                           for nx in bot.townhalls.ready
                           for g in bot.vespene_geyser.closer_than(10, nx))
            if not bot.structures(U.PYLON).ready or bot.tech_requirement_progress(uid) < 1:
                return False
            return True
        if token == "PROBE":
            return bool(bot.townhalls.ready.idle)
        if bot.tech_requirement_progress(uid) < 1:
            return False
        for group, producer in ((GATEWAY_UNITS, U.GATEWAY), (ROBO_UNITS, U.ROBOTICSFACILITY),
                                (STARGATE_UNITS, U.STARGATE)):
            if token in group:
                return bool(bot.structures(producer).ready.idle)
        return False

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
            if hasattr(bot, "bs_expand"):    # bot can pre-send the builder probe
                return await bot.bs_expand()
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
