"""Production: tech buildings, army, upgrades, and emergency defense.

Simple but adaptive: a gateway + robo core, composition that shifts with the
enemy race (zealot-heavy vs. Zerg mass-light, stalker/immortal otherwise), forge
upgrades (efficiency bought in advance), and static defense when the advisor
flags an all-in. Trains straight from gateways (no warpgate) for robustness.
"""

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId
from sc2.data import Race


class Production:
    async def step(self, bot, advice):
        if not bot.structures(U.PYLON).ready:
            return
        await self._tech(bot, advice)
        await self._defense(bot, advice)
        await self._upgrades(bot)
        self._train(bot, advice)

    def _pylon(self, bot):
        return bot.structures(U.PYLON).ready.random

    async def _tech(self, bot, advice):
        gates = bot.structures(U.GATEWAY)
        # Forge-FIRST when the library wants static defense (proactive insurance or
        # emergency). From analysis/REPLAY_FINDINGS.md: 12 Protoss wins vs
        # 12PoolBot / ZEALOCALYPSE opened Forge ~0:57 -> photon cannons ~1:30 --
        # cannons beat a shield battery (needs cyber) to the punch and need no
        # army. So the Forge goes down before the first gateway here.
        if (advice.defense.static_defense >= 1 and not bot.structures(U.FORGE)
                and bot.already_pending(U.FORGE) == 0 and bot.can_afford(U.FORGE)):
            await bot.build(U.FORGE, near=self._pylon(bot))
            return
        # first gateway -- on the ramp wall if we can
        if gates.amount + bot.already_pending(U.GATEWAY) == 0:
            if bot.can_afford(U.GATEWAY):
                wall_pos = bot.wall.building_pos(bot, 0)
                near = wall_pos if wall_pos is not None else self._pylon(bot).position.towards(bot.game_info.map_center, 5)
                await bot.build(U.GATEWAY, near=near)
            return
        # Under a real EMERGENCY, hold the rest of the tech until the cannons are
        # up -- let the minerals flow to static defense (built in _defense).
        # Under a real EMERGENCY, hold the rest of the tech until the cannons are
        # up -- let the minerals flow to static defense (built in _defense).
        if advice.defense.emergency:
            cannons = bot.structures(U.PHOTONCANNON).amount + bot.already_pending(U.PHOTONCANNON)
            if bot.structures(U.FORGE).ready and cannons < advice.defense.static_defense:
                if (gates.amount + bot.already_pending(U.GATEWAY) < 2
                        and bot.can_afford(U.GATEWAY) and bot.minerals > 320):
                    await bot.build(U.GATEWAY, near=self._pylon(bot).position.towards(bot.game_info.map_center, 5))
                return
        # cybernetics core after the first gateway -- completes the ramp wall
        if gates.ready and not bot.structures(U.CYBERNETICSCORE) and bot.already_pending(U.CYBERNETICSCORE) == 0:
            if bot.can_afford(U.CYBERNETICSCORE):
                wall_pos = bot.wall.building_pos(bot, 1)
                near = wall_pos if wall_pos is not None else self._pylon(bot)
                await bot.build(U.CYBERNETICSCORE, near=near)
            return
        if not bot.structures(U.CYBERNETICSCORE).ready:
            return
        # robotics for immortals + observer (detection, anti-armor)
        if not bot.structures(U.ROBOTICSFACILITY) and bot.already_pending(U.ROBOTICSFACILITY) == 0:
            if bot.can_afford(U.ROBOTICSFACILITY):
                await bot.build(U.ROBOTICSFACILITY, near=self._pylon(bot))
        # forge for upgrades
        if not bot.structures(U.FORGE) and bot.already_pending(U.FORGE) == 0:
            if bot.can_afford(U.FORGE) and bot.townhalls.amount >= 2:
                await bot.build(U.FORGE, near=self._pylon(bot))
        # twilight council -> charge (huge vs Zerg) / blink
        if (
            bot.structures(U.CYBERNETICSCORE).ready and bot.townhalls.amount >= 2
            and not bot.structures(U.TWILIGHTCOUNCIL) and bot.already_pending(U.TWILIGHTCOUNCIL) == 0
            and bot.can_afford(U.TWILIGHTCOUNCIL)
        ):
            await bot.build(U.TWILIGHTCOUNCIL, near=self._pylon(bot))
        # robotics bay -> colossus (splash vs mass-light Zerg)
        if (
            bot.enemy_race == Race.Zerg and bot.structures(U.ROBOTICSFACILITY).ready
            and not bot.structures(U.ROBOTICSBAY) and bot.already_pending(U.ROBOTICSBAY) == 0
            and bot.townhalls.amount >= 3 and bot.can_afford(U.ROBOTICSBAY)
        ):
            await bot.build(U.ROBOTICSBAY, near=self._pylon(bot))
        # army upgrades from the twilight council
        twi = bot.structures(U.TWILIGHTCOUNCIL).ready.idle
        if twi:
            up = UpgradeId.CHARGE if bot.enemy_race == Race.Zerg else UpgradeId.BLINKTECH
            if bot.already_pending_upgrade(up) == 0 and bot.can_afford(up):
                twi.first.research(up)
        # scale gateways with economy -- spend the money, don't float
        target_gates = min(10, 2 * bot.townhalls.ready.amount + 1)
        if advice.defense.prioritize_army:
            target_gates = min(10, target_gates + 2)   # library says defend -> more army production
        # allow two in flight, and build extra whenever minerals are piling up
        max_pending = 2 if bot.minerals > 350 else 1
        if (
            gates.amount + bot.already_pending(U.GATEWAY) < target_gates
            and bot.already_pending(U.GATEWAY) < max_pending
            and bot.can_afford(U.GATEWAY)
            and bot.minerals > 150
        ):
            await bot.build(U.GATEWAY, near=self._pylon(bot).position.towards(bot.game_info.map_center, 5))

    async def _defense(self, bot, advice):
        # The library decides how much to defend; we translate it into Protoss
        # structures. No hard-coded archetype logic here.
        plan = advice.defense
        want = plan.static_defense
        if want <= 0 and not plan.need_detection:
            return
        base = bot.townhalls.closest_to(bot.enemy_start_locations[0]) if bot.townhalls else None
        if base is None:
            return
        cannons = bot.structures(U.PHOTONCANNON).amount + bot.already_pending(U.PHOTONCANNON)
        batteries = bot.structures(U.SHIELDBATTERY).amount + bot.already_pending(U.SHIELDBATTERY)

        # Cannons are the primary hold (need only a Forge -> up fast, no micro).
        # Split them between the mineral line (ling/zealot runbys that dive workers)
        # and the ramp choke (a frontal push).
        if bot.structures(U.FORGE).ready and cannons < want and bot.can_afford(U.PHOTONCANNON):
            await bot.build(U.PHOTONCANNON, near=self._cannon_pos(bot, base, cannons))
            return
        # A couple of shield batteries sustain the wall/cannons once cyber is up
        # (great vs. zealots -- they heal shields). Place at the choke.
        if (plan.emergency and bot.structures(U.CYBERNETICSCORE).ready
                and batteries < 2 and bot.can_afford(U.SHIELDBATTERY)):
            await bot.build(U.SHIELDBATTERY, near=self._choke_pos(bot, base))
            return
        # detection: a cannon also detects -- cover the mineral line
        if (plan.need_detection and bot.structures(U.FORGE).ready
                and cannons < want + 1 and bot.can_afford(U.PHOTONCANNON)):
            await bot.build(U.PHOTONCANNON, near=self._mineral_line_pos(bot, base))

    def _mineral_line_pos(self, bot, base):
        mins = bot.mineral_field.closer_than(10, base)
        if mins:
            return base.position.towards(mins.center, 4)
        return base.position.towards(bot.game_info.map_center, -3)

    def _choke_pos(self, bot, base):
        try:
            return bot.main_base_ramp.top_center.towards(base.position, 3)
        except Exception:
            return base.position.towards(bot.game_info.map_center, 6)

    def _cannon_pos(self, bot, base, index):
        # Alternate, mineral line first (runby protection is what loses to lings),
        # then the choke; extras spread across both.
        return self._mineral_line_pos(bot, base) if index % 2 == 0 else self._choke_pos(bot, base)

    async def _upgrades(self, bot):
        forge = bot.structures(U.FORGE).ready.idle
        if not forge:
            return
        for up in (UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1, UpgradeId.PROTOSSGROUNDARMORSLEVEL1,
                   UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2, UpgradeId.PROTOSSGROUNDARMORSLEVEL2):
            if bot.already_pending_upgrade(up) == 0 and bot.can_afford(up):
                forge.first.research(up)
                return

    def _train(self, bot, advice):
        # robo: one observer for detection, then colossus (splash) or immortals
        robo = bot.structures(U.ROBOTICSFACILITY).ready.idle
        if robo:
            have_obs = bot.units(U.OBSERVER).amount + bot.already_pending(U.OBSERVER)
            if have_obs == 0 and bot.can_afford(U.OBSERVER):
                robo.first.train(U.OBSERVER)
            elif bot.structures(U.ROBOTICSBAY).ready and bot.can_afford(U.COLOSSUS):
                robo.first.train(U.COLOSSUS)
            elif bot.can_afford(U.IMMORTAL):
                robo.first.train(U.IMMORTAL)

        zealot_heavy = bot.enemy_race == Race.Zerg
        for gate in bot.structures(U.GATEWAY).ready.idle:
            stalkers = bot.units(U.STALKER).amount
            zealots = bot.units(U.ZEALOT).amount
            want_zealot = zealots <= stalkers if zealot_heavy else zealots * 2 <= stalkers
            can_stalk = bot.structures(U.CYBERNETICSCORE).ready and bot.can_afford(U.STALKER)
            if want_zealot and bot.can_afford(U.ZEALOT):
                gate.train(U.ZEALOT)
            elif can_stalk:
                gate.train(U.STALKER)
            elif bot.can_afford(U.ZEALOT):
                gate.train(U.ZEALOT)
