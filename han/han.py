import sc2
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3

from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId
import random

class SC2Bot(BotAI):
    async def on_step(self, iteration):
        # Basic economy management
        await self.distribute_workers()
        
        # Additional game management
        if iteration % 10 == 0:  # Every 10 iterations
            print(f"iteration {iteration}")
            await self.manage_army()
            await self.manage_production()

    async def manage_army(self):
        # Get all military units
        military_units = self.units(UnitTypeId.MARINE) | self.units(UnitTypeId.MARAUDER)
                
        if not self.should_attack():
            # If not attacking, gather units at the ramp
            if military_units:
                # Get main ramp position
                ramp = self.main_base_ramp
                rally_point = ramp.top_center
                
                # If units are too spread out, gather them at the ramp
                for unit in military_units:
                    if unit.distance_to(rally_point) > 3:
                        unit.move(rally_point)
                        return
            return

        # Attack logic
        target = None
        if self.enemy_units:
            for unit in military_units:
                closest_enemy = self.enemy_units.closest_to(unit)
                unit.attack(closest_enemy)
            return
        elif self.enemy_structures:
            for unit in military_units:
                closest_enemy = self.enemy_structures.closest_to(unit)
                unit.attack(closest_enemy)
            return
        else:
            target = self.enemy_start_locations[0]
            
        print(f"attacking {target}")
        for unit in military_units:
            unit.attack(target)

    async def manage_production(self):
        print(f"manage_production")
        await self.build_supply_depot_if_needed()
        await self.build_gas_if_needed()
        await self.build_barracks_if_needed()
        await self.append_addons()
        await self.train_military_units()
        await self.train_workers()
        await self.expand_base()

    async def build_supply_depot_if_needed(self):
        if self.supply_left < 5 * self.townhalls.amount:
            max_concurrent = 2 if self.townhalls.ready.amount > 2 else 1
            pending_depots = self.already_pending(UnitTypeId.SUPPLYDEPOT)
            
            while (
                pending_depots < max_concurrent 
                and self.can_afford(UnitTypeId.SUPPLYDEPOT)
            ):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=self.townhalls.first)
                pending_depots += 1

        # Lower completed supply depots
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
        
        # Raise if enemies nearby
        for depot in self.structures(UnitTypeId.SUPPLYDEPOTLOWERED).ready:
            if self.enemy_units:
                closest_enemy = self.enemy_units.closest_to(depot)
                if closest_enemy.distance_to(depot) < 10:
                    depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)

    async def build_gas_if_needed(self):
        if self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(UnitTypeId.BARRACKS) == 0:
            return

        total_refineries = self.structures(UnitTypeId.REFINERY).amount + self.already_pending(UnitTypeId.REFINERY)
        
        if self.townhalls.ready.amount == 1:
            if total_refineries >= 1:
                return

        if self.townhalls.ready.amount == 2:
            if total_refineries >= 3:
                return

        if total_refineries >= self.townhalls.ready.amount + 2:
            return

        for th in self.townhalls.ready:
            vgs = self.vespene_geyser.closer_than(10, th)
            for vg in vgs:
                if await self.can_place_single(UnitTypeId.REFINERY, vg.position) and self.can_afford(UnitTypeId.REFINERY):
                    workers = self.workers.gathering
                    if workers:
                        worker = workers.closest_to(vg)
                        worker.build_gas(vg)
                        return

    async def build_barracks_if_needed(self):
        if not self.can_afford(UnitTypeId.BARRACKS):
            return
            
        barracks_count = self.structures(UnitTypeId.BARRACKS).amount
        barracks_pending = self.already_pending(UnitTypeId.BARRACKS)
        total_barracks = barracks_count + barracks_pending
        
        if self.townhalls.amount < 3:
            if total_barracks >= 3:
                return
    
        if total_barracks < self.workers.amount // 6:
            if self.townhalls:
                cc = self.townhalls.first
                pos = cc.position.towards(self.game_info.map_center, 8)
                await self.build(UnitTypeId.BARRACKS, near=pos)

    async def train_military_units(self):
        for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if barracks.has_add_on:
                if barracks.add_on_tag in self.structures(UnitTypeId.BARRACKSTECHLAB).tags:
                    if self.can_afford(UnitTypeId.MARAUDER) and self.supply_left > 2:
                        barracks.train(UnitTypeId.MARAUDER)
                elif barracks.add_on_tag in self.structures(UnitTypeId.BARRACKSREACTOR).tags:
                    # Train two marines at once with reactor
                    for _ in range(2):
                        if self.can_afford(UnitTypeId.MARINE) and self.supply_left > 1:
                            barracks.train(UnitTypeId.MARINE)
            else:
                if self.can_afford(UnitTypeId.MARINE) and self.supply_left > 1:
                    barracks.train(UnitTypeId.MARINE)

    async def train_workers(self):
        if self.workers.amount >= 80:
            return
        
        if self.workers.amount >= 20 * self.townhalls.ready.amount:
            return
        
        for cc in self.townhalls.ready.idle:
            if self.can_afford(UnitTypeId.SCV) and self.supply_left > 0:
                cc.train(UnitTypeId.SCV)

    def should_attack(self):
        military_supply = self.get_military_supply()
        
        if military_supply > 20 * self.townhalls.ready.amount:
            print(f"Military supply {military_supply} > 20 * {self.townhalls.ready.amount}, attacking")
            return True
            
        military_units = self.units.filter(
            lambda unit: unit.type_id in {
                UnitTypeId.MARINE,
                UnitTypeId.MARAUDER,
                UnitTypeId.REAPER
            }
        )
        
        if len(military_units) > 15 * self.townhalls.ready.amount:
            print(f"enough military units, attacking")
            return True
            
        # Check if enemy is close to our base
        if self.townhalls:
            main_base = self.townhalls.first
            enemy_units = self.enemy_units | self.enemy_structures
            if enemy_units:
                closest_enemy = enemy_units.closest_to(main_base)
                if closest_enemy.distance_to(main_base) < 30:
                    print(f"enemy is close, attacking")
                    return True
                    
        if self.supply_used > 180:
            print(f"supply used is max, attacking")
            return True
        
        return False

    def get_military_supply(self):
        military_supply = 0
        military_supply += self.units(UnitTypeId.MARINE).amount * 1
        military_supply += self.units(UnitTypeId.MARAUDER).amount * 2
        military_supply += self.units(UnitTypeId.REAPER).amount * 1
        return military_supply

    async def append_addons(self):
        """Manage add-ons for barracks, randomly choosing between tech lab and reactor."""
        for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if not barracks.has_add_on and random.random() < 0.5:
                await self.append_addon(UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING, UnitTypeId.BARRACKSTECHLAB)
            else:
                await self.append_addon(UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING, UnitTypeId.BARRACKSREACTOR)

    async def append_addon(self, building_type, building_flying_type, add_on_type):
        def points_to_build_addon(building_position: Point2) -> list[Point2]:
            addon_offset: Point2 = Point2((2.5, -0.5))
            addon_position: Point2 = building_position + addon_offset
            addon_points = [
                (addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)
            ]
            return addon_points

        for building in self.structures(building_type).ready.idle:
            if not building.has_add_on and self.can_afford(add_on_type):
                addon_points = points_to_build_addon(building.position)
                if all(
                    self.in_map_bounds(addon_point)
                    and self.in_placement_grid(addon_point)
                    and self.in_pathing_grid(addon_point)
                    for addon_point in addon_points
                ):
                    building.build(add_on_type)
                else:
                    building(AbilityId.LIFT)

        def land_positions(position: Point2) -> list[Point2]:
            land_positions = [(position + Point2((x, y))).rounded for x in range(-1, 2) for y in range(-1, 2)]
            return land_positions + points_to_build_addon(position)

        for building in self.structures(building_flying_type).idle:
            possible_land_positions_offset = sorted(
                (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                key=lambda point: point.x**2 + point.y**2,
            )
            offset_point: Point2 = Point2((-0.5, -0.5))
            possible_land_positions = (building.position.rounded + offset_point + p for p in possible_land_positions_offset)
            for target_land_position in possible_land_positions:
                land_and_addon_points: list[Point2] = land_positions(target_land_position)
                if all(
                    self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos) and self.in_pathing_grid(land_pos)
                    for land_pos in land_and_addon_points
                ):
                    building(AbilityId.LAND, target_land_position)
                    break

    async def expand_base(self):
        try:
            MAX_BASES = 8
            
            # Don't expand if we can't afford it
            if not self.can_afford(UnitTypeId.COMMANDCENTER):
                return
                
            # Don't expand if we're at max bases
            if len(self.townhalls) >= MAX_BASES:
                return
                
            # Check if current bases are saturated (16 workers per base is optimal)
            for th in self.townhalls.ready:
                if len(self.workers.closer_than(10, th)) < 16:
                    return  # Don't expand if current bases aren't fully utilized
                    
            # Check if we're already expanding
            if self.already_pending(UnitTypeId.COMMANDCENTER):
                return
                
            # All checks passed, try to expand
            await self.expand_now()
                
        except Exception as e:
            print(f"Error expanding base: {e}")

def main():
    bot = SC2Bot()
    maps_pool = ["CatalystLE"]
    
    run_game(
        maps.get(maps_pool[0]),
        [
            Bot(Race.Terran, bot),
            Computer(Race.Random, Difficulty.Hard)
        ],
        realtime=False
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())