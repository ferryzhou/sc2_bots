"""Wall: seal the main ramp so a few units + probes can hold an all-in.

The classic Protoss hold: a Pylon + two buildings (gateway, cyber) on the ramp
leave a one-unit gap that a zealot plugs. python-sc2 computes the exact tiles;
we just place our first buildings there and post a unit at the gap.

This is *execution* of the library's DefensePlan ("defend"), not a new decision.
"""

from sc2.ids.unit_typeid import UnitTypeId as U


class Wall:
    def __init__(self):
        self._cache = None

    def layout(self, bot):
        """(pylon_pos, [building_pos, building_pos], hold_pos) or (None, [], None)."""
        if self._cache is not None:
            return self._cache
        try:
            ramp = bot.main_base_ramp
            pylon = ramp.protoss_wall_pylon
            builds = sorted(ramp.protoss_wall_buildings, key=lambda p: (round(p.x), round(p.y)))
            hold = ramp.protoss_wall_warpin
            if pylon is None or len(builds) < 2:
                self._cache = (None, [], None)
            else:
                self._cache = (pylon, builds, hold)
        except Exception:
            self._cache = (None, [], None)
        return self._cache

    def pylon_pos(self, bot):
        return self.layout(bot)[0]

    def building_pos(self, bot, index):
        builds = self.layout(bot)[1]
        return builds[index] if len(builds) > index else None

    def hold_pos(self, bot):
        return self.layout(bot)[2]

    def gap_open(self, bot):
        """True if the wall isn't fully built yet (needs a unit to plug the gap)."""
        pylon, builds, _ = self.layout(bot)
        if pylon is None:
            return False
        placed = sum(
            1 for p in builds
            if bot.structures.of_type({U.GATEWAY, U.CYBERNETICSCORE, U.FORGE})
            .closer_than(1.5, p)
        )
        return placed < len(builds)
