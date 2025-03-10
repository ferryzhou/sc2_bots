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
from sc2.ids.upgrade_id import UpgradeId
import math

class SC2Bot(BotAI):
    async def on_step(self, iteration):
        # Basic economy management
        await self.distribute_workers()
        await self.build_supply_depot_if_needed()
        await self.train_workers()
        await self.expand_base()
        
        # Additional game management
        if iteration % 10 == 0:  # Every 10 iterations
            print(f"iteration {iteration}")
            await self.manage_production()
            await self.manage_army()

    async def manage_production(self):
        print(f"manage_production")
        await self.build_gas_if_needed()
        await self.build_factory_if_needed()
        await self.build_barracks_if_needed()
        await self.build_starport_if_needed()
        await self.build_engineering_bay_if_needed()
        await self.append_addons()
        await self.upgrade_army()
        await self.train_military_units()

    async def manage_army(self):
        # Get all military units
        military_units = self.units(UnitTypeId.MARINE) | self.units(UnitTypeId.MARAUDER)
        tanks = self.units(UnitTypeId.SIEGETANK) | self.units(UnitTypeId.SIEGETANKSIEGED)
        medivacs = self.units(UnitTypeId.MEDIVAC)
        ravens = self.units(UnitTypeId.RAVEN)
        
        await self.manage_medivacs(medivacs, military_units)
        await self.manage_ravens(ravens, military_units)
                
        if not self.should_attack():
            print(f"not attacking")
            await self.execute_defense(military_units, tanks)
            return

        print(f"attacking")
        await self.execute_attack(military_units, tanks)

    async def execute_defense(self, military_units, tanks):
        """Execute defensive positioning and micro for all military units."""
        if not (military_units or tanks):
            return
            
        # Determine rally point based on army size
        if self.get_military_supply() > 15:
            # Rally at the townhall closest to map center (most forward base)
            if self.townhalls.ready:
                forward_base = self.townhalls.ready.closest_to(self.game_info.map_center)
                rally_point = forward_base.position.towards(self.game_info.map_center, 8)
                print(f"Rallying at forward base: {rally_point}")
            else:
                # Fallback to main base ramp if no bases
                ramp = self.main_base_ramp
                rally_point = ramp.top_center
        else:
            # Default rally at main base ramp for smaller armies
            ramp = self.main_base_ramp
            rally_point = ramp.top_center
        
        # Position infantry at rally point
        for unit in military_units:
            if unit.distance_to(rally_point) > 3:
                unit.move(rally_point)
        
        # Handle tank micro
        for tank in tanks:
            enemies = self.enemy_units | self.enemy_structures
            if enemies:
                closest_enemy = enemies.closest_to(tank)
                # Siege if enemy is in range
                if closest_enemy.distance_to(tank) < 13 and tank.type_id == UnitTypeId.SIEGETANK:
                    tank(AbilityId.SIEGEMODE_SIEGEMODE)
                # Unsiege if enemy is too far
                elif closest_enemy.distance_to(tank) > 15 and tank.type_id == UnitTypeId.SIEGETANKSIEGED:
                    tank(AbilityId.UNSIEGE_UNSIEGE)
            else:
                # No enemies, but still manage tank positioning
                if tank.distance_to(rally_point) > 5:
                    # If tank is far from rally point, unsiege and move closer
                    if tank.type_id == UnitTypeId.SIEGETANKSIEGED:
                        tank(AbilityId.UNSIEGE_UNSIEGE)
                    elif tank.type_id == UnitTypeId.SIEGETANK:
                        tank.move(rally_point)
                else:
                    # Tank is at rally point, siege up for defense
                    if tank.type_id == UnitTypeId.SIEGETANK:
                        # Create a spread of siege positions around the rally point
                        tank_index = list(tanks).index(tank)
                        offset = Point2((tank_index % 3 - 1, tank_index // 3 - 1)) * 2
                        siege_position = rally_point + offset
                        
                        # Move to siege position then siege
                        if tank.distance_to(siege_position) > 1:
                            tank.move(siege_position)
                        else:
                            tank(AbilityId.SIEGEMODE_SIEGEMODE)

    async def execute_attack(self, military_units, tanks):
        """Execute attack logic for all military units."""
        # Split our forces based on enemy presence
        enemy_units = self.enemy_units
        enemy_structures = self.enemy_structures
        
        # Determine how many units to allocate to fighting enemy units
        if enemy_units and military_units:
            print(f"attacking units")
            # Calculate how many units we need to handle enemy units
            enemy_strength = sum(unit.health_max for unit in enemy_units)
            our_strength = sum(unit.health_max for unit in military_units)
            
            # Prevent division by zero
            if our_strength > 0:
                # Allocate between 40-100% of our forces to handle enemy units
                allocation_ratio = min(1.0, max(0.4, enemy_strength * 1.5 / our_strength))
                units_for_combat = int(len(military_units) * allocation_ratio)
                
                # Select units for combat (closest to enemy units)
                if units_for_combat > 0:
                    combat_units = military_units.sorted_by_distance_to(enemy_units.center)[:units_for_combat]
                    remaining_units = [unit for unit in military_units if unit not in combat_units]
                    
                    # Send combat units to attack enemy units
                    for unit in combat_units:
                        closest_enemy = enemy_units.closest_to(unit)
                        unit.attack(closest_enemy)
                else:
                    remaining_units = military_units
            else:
                # If our strength is 0, use all units
                remaining_units = military_units
        else:
            remaining_units = military_units
        
        # Handle tank micro during attack
        for tank in tanks:
            if enemy_units:
                closest_enemy = enemy_units.closest_to(tank)
                if closest_enemy.distance_to(tank) < 13 and tank.type_id == UnitTypeId.SIEGETANK:
                    tank(AbilityId.SIEGEMODE_SIEGEMODE)
                elif closest_enemy.distance_to(tank) > 15 and tank.type_id == UnitTypeId.SIEGETANKSIEGED:
                    tank(AbilityId.UNSIEGE_UNSIEGE)
                else:
                    tank.attack(closest_enemy)
            elif enemy_structures:
                closest_structure = enemy_structures.closest_to(tank)
                if closest_structure.distance_to(tank) < 13 and tank.type_id == UnitTypeId.SIEGETANK:
                    tank(AbilityId.SIEGEMODE_SIEGEMODE)
                elif tank.type_id == UnitTypeId.SIEGETANK:
                    tank.attack(closest_structure)
            else:
                # No visible enemies, attack enemy base
                target = self.enemy_start_locations[0]
                tank.attack(target)
        
        # Send remaining units to attack structures or enemy base
        if remaining_units:
            if enemy_structures:
                print(f"attacking structures with remaining units")
                # Split remaining units to attack different structures
                structure_targets = enemy_structures.random_group_of(min(len(remaining_units), len(enemy_structures)))
                
                for i, unit in enumerate(remaining_units):
                    if i < len(structure_targets):
                        unit.attack(structure_targets[i].position)
                    else:
                        # If we have more units than targets, send extras to random structures
                        unit.attack(enemy_structures.random.position)
            else:
                print(f"attacking start location with remaining units")
                # No structures, attack enemy base
                target = self.enemy_start_locations[0]
                
                # Send units to different parts of the base to spread damage
                for i, unit in enumerate(remaining_units):
                    offset = Point2((i % 5 - 2, i // 5 - 2))  # Create a grid of attack points
                    attack_point = target + offset * 2  # Spread units around the target
                    unit.attack(attack_point)

    async def manage_medivacs(self, medivacs, military_units):
        """Manage medivac movement to follow army units."""
        if not medivacs or not military_units:
            return

        enemies = self.enemy_units | self.enemy_structures
        if not enemies:
            # If no enemies, follow army center as before
            center = military_units.center
            for medivac in medivacs:
                if medivac.distance_to(center) > 5:
                    medivac.move(center)
            return

        # Get units that are close to enemies
        forward_units = military_units.filter(
            lambda unit: enemies.closest_to(unit).distance_to(unit) < 15
        )

        if not forward_units:
            # If no units close to enemies, follow army center
            center = military_units.center
            for medivac in medivacs:
                if medivac.distance_to(center) > 5:
                    medivac.move(center)
            return

        # Assign each medivac to a random forward unit
        for medivac in medivacs:
            target_unit = random.choice(forward_units)
            if medivac.distance_to(target_unit) > 3:
                medivac.move(target_unit.position)

    async def manage_ravens(self, ravens, military_units):
        """Manage raven movement to follow army units and use abilities."""
        if not ravens or not military_units:
            return

        enemies = self.enemy_units | self.enemy_structures
        if not enemies:
            # If no enemies, follow army center
            center = military_units.center
            for raven in ravens:
                if raven.distance_to(center) > 7:
                    raven.move(center)
            return

        # Get units that are close to enemies
        forward_units = military_units.filter(
            lambda unit: enemies.closest_to(unit).distance_to(unit) < 15
        )

        if not forward_units:
            # If no units close to enemies, follow army center
            center = military_units.center
            for raven in ravens:
                if raven.distance_to(center) > 7:
                    raven.move(center)
            return

        # Assign each raven to a random forward unit
        for raven in ravens:
            target_unit = random.choice(forward_units)
            if raven.distance_to(target_unit) > 5:
                raven.move(target_unit.position)

    async def build_supply_depot_if_needed(self):
        if self.supply_left < 6 * self.townhalls.amount:
            max_concurrent = 2 if self.townhalls.ready.amount > 1 else 1
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
        barracks_flying = self.structures(UnitTypeId.BARRACKSFLYING).amount
        barracks_pending = self.already_pending(UnitTypeId.BARRACKS)
        total_barracks = barracks_count + barracks_flying + barracks_pending
        
        if self.townhalls.amount < 3:
            if total_barracks >= 4:
                return
    
        if total_barracks >= self.workers.amount // 6:
            return
        
        if total_barracks >= 8:
            return
        
        if not self.townhalls:
            return
        
        # Get main base and its position
        cc = self.townhalls.first
        base_pos = cc.position
        
        # Try primary placement method
        pos = await self.find_placement(
            UnitTypeId.BARRACKS,
            near_position=base_pos,
            min_distance=6,
            max_distance=25,
            addon_space=True
        )
        
        if pos:
            print(f"Building barracks at position {pos}")
            await self.build(UnitTypeId.BARRACKS, near=pos)
        else:
            # Fallback method 1: Try direct placement
            print("Fallback: Using direct placement for barracks")
            potential_positions = [
                base_pos.towards(self.game_info.map_center, 8),
                base_pos.towards(self.game_info.map_center, 12),
                base_pos.towards(self.game_info.map_center, 16)
            ]
            
            for fallback_pos in potential_positions:
                if await self.can_place(UnitTypeId.BARRACKS, fallback_pos):
                    await self.build(UnitTypeId.BARRACKS, near=fallback_pos)
                    return
            
            # Fallback method 2: Just try the standard build method near base
            await self.build(UnitTypeId.BARRACKS, near=base_pos)

    async def build_factory_if_needed(self):
        # Need barracks before factory
        if not self.structures(UnitTypeId.BARRACKS).ready:
            return
        
        if not self.can_afford(UnitTypeId.FACTORY):
            return
        
        if not self.townhalls:
            return

        # Get current factory count (including flying factories)
        factories = self.structures(UnitTypeId.FACTORY).amount
        factories_flying = self.structures(UnitTypeId.FACTORYFLYING).amount
        factories_pending = self.already_pending(UnitTypeId.FACTORY)
        total_factories = factories + factories_flying + factories_pending

        # Always build first factory when we have enough military units
        if total_factories == 0 and self.get_military_supply() >= 10:
            # Find placement for factory with addon space
            pos = await self.find_placement(
                UnitTypeId.FACTORY,
                near_position=self.townhalls.first.position,
                min_distance=6,
                max_distance=25,
                addon_space=True
            )
            
            if pos:
                print(f"Building factory at position {pos}")
                await self.build(UnitTypeId.FACTORY, near=pos)
            else:
                print("Fallback: Using direct placement for factory")
                # Fallback: build near any barracks
                barracks = self.structures(UnitTypeId.BARRACKS).ready
                if barracks:
                    await self.build(UnitTypeId.FACTORY, near=barracks.random.position.towards(self.game_info.map_center, 7))
                else:
                    await self.build(UnitTypeId.FACTORY, near=self.townhalls.first)
            return

        # Only build second factory when we have a large ground army
        ground_units = self.units(UnitTypeId.MARINE).amount + self.units(UnitTypeId.MARAUDER).amount
        if total_factories == 1 and ground_units >= 30:
            pos = await self.find_placement(
                UnitTypeId.FACTORY,
                near_position=self.townhalls.first.position,
                min_distance=6,
                max_distance=25,
                addon_space=True
            )
            
            if pos:
                await self.build(UnitTypeId.FACTORY, near=pos)
            else:
                # Fallback: build near any barracks
                barracks = self.structures(UnitTypeId.BARRACKS).ready
                if barracks:
                    await self.build(UnitTypeId.FACTORY, near=barracks.random.position.towards(self.game_info.map_center, 7))

    async def build_starport_if_needed(self):
        # Need at least one factory before starport
        if not self.structures(UnitTypeId.FACTORY).ready:
            return
    
        if not self.can_afford(UnitTypeId.STARPORT):
            return
        
        if not self.townhalls:
            return

        # Check if we already have starports or one is in progress (including flying)
        starports = self.structures(UnitTypeId.STARPORT).amount
        starports_flying = self.structures(UnitTypeId.STARPORTFLYING).amount
        starports_pending = self.already_pending(UnitTypeId.STARPORT)
        total_starports = starports + starports_flying + starports_pending
        
        if total_starports >= 2:
            return

        # Find placement for starport with addon space
        pos = await self.find_placement(
            UnitTypeId.STARPORT,
            near_position=self.townhalls.first.position,
            min_distance=6,
            max_distance=25,
            addon_space=True
        )
        
        if pos:
            print(f"Building starport at position {pos}")
            await self.build(UnitTypeId.STARPORT, near=pos)
        else:
            print("Fallback: Using direct placement for starport")
            # Fallback: build near factory or barracks
            if self.structures(UnitTypeId.FACTORY).ready:
                await self.build(UnitTypeId.STARPORT, near=self.structures(UnitTypeId.FACTORY).ready.random.position)
            elif self.structures(UnitTypeId.BARRACKS).ready:
                await self.build(UnitTypeId.STARPORT, near=self.structures(UnitTypeId.BARRACKS).ready.random.position)
            else:
                await self.build(UnitTypeId.STARPORT, near=self.townhalls.first)

    async def build_engineering_bay_if_needed(self):
        # Only start upgrades when we have enough units
        if self.get_military_supply() < 30:
            return

        # Build Engineering Bays if we don't have them and can afford it
        if (len(self.structures(UnitTypeId.ENGINEERINGBAY)) + self.already_pending(UnitTypeId.ENGINEERINGBAY) < 2 and 
            self.can_afford(UnitTypeId.ENGINEERINGBAY)):
            
            # Find placement for engineering bay (no addon needed)
            pos = await self.find_placement(
                UnitTypeId.ENGINEERINGBAY,
                near_position=self.townhalls.first.position,
                min_distance=5,
                max_distance=20,
                addon_space=False
            )
            
            if pos:
                print(f"Building engineering bay at position {pos}")
                await self.build(UnitTypeId.ENGINEERINGBAY, near=pos)
            else:
                print("Fallback: Using direct placement for engineering bay")
                # Fallback method for engineering bay
                await self.build(UnitTypeId.ENGINEERINGBAY, near=self.townhalls.first.position.towards(self.game_info.map_center, 8))

    async def train_military_units(self):
        # Build tanks if we have enough military units and a factory with tech lab
        if self.get_military_supply() >= 10:
            for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
                if factory.has_add_on:
                    if factory.add_on_tag in self.structures(UnitTypeId.FACTORYTECHLAB).tags:
                        if self.can_afford(UnitTypeId.SIEGETANK) and self.supply_left > 4:
                            factory.train(UnitTypeId.SIEGETANK)

        # Build medivacs based on ground unit count
        ground_units = self.units(UnitTypeId.MARINE).amount + self.units(UnitTypeId.MARAUDER).amount
        desired_medivacs = ground_units // 8  # One medivac for every 8 ground units
        current_medivacs = self.units(UnitTypeId.MEDIVAC).amount

        if current_medivacs < desired_medivacs:
            for starport in self.structures(UnitTypeId.STARPORT).ready.idle:
                if self.can_afford(UnitTypeId.MEDIVAC) and self.supply_left > 2:
                    starport.train(UnitTypeId.MEDIVAC)

        # Build Ravens (up to 2)
        current_ravens = self.units(UnitTypeId.RAVEN).amount
        desired_ravens = 2
        
        if current_ravens < desired_ravens:
            for starport in self.structures(UnitTypeId.STARPORT).ready.idle:
                if starport.has_add_on:
                    if starport.add_on_tag in self.structures(UnitTypeId.STARPORTTECHLAB).tags:
                        if self.can_afford(UnitTypeId.RAVEN) and self.supply_left > 2:
                            starport.train(UnitTypeId.RAVEN)

        # Existing barracks training logic
        for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if barracks.has_add_on:
                if barracks.add_on_tag in self.structures(UnitTypeId.BARRACKSTECHLAB).tags:
                    if self.can_afford(UnitTypeId.MARAUDER) and self.supply_left > 2:
                        barracks.train(UnitTypeId.MARAUDER)
                elif barracks.add_on_tag in self.structures(UnitTypeId.BARRACKSREACTOR).tags:
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
        # Get our military units
        military_units = self.units.filter(
            lambda unit: unit.type_id in {
                UnitTypeId.MARINE,
                UnitTypeId.MARAUDER,
                UnitTypeId.REAPER,
                UnitTypeId.SIEGETANK,
                UnitTypeId.SIEGETANKSIEGED,
                UnitTypeId.MEDIVAC,
                UnitTypeId.RAVEN
            }
        )
        
        # Define worker unit types
        worker_types = {
            UnitTypeId.SCV,
            UnitTypeId.PROBE,
            UnitTypeId.DRONE,
            UnitTypeId.MULE
        }
        
        # Filter out workers and structures from enemy units
        enemy_combat_units = self.enemy_units.filter(
            lambda unit: not unit.is_structure and unit.type_id not in worker_types
        )
        
        # Check for numerical advantage based on unit cost (minerals + gas)
        if len(enemy_combat_units) > 5:
            # Calculate total value of enemy units
            enemy_army_value = sum(
                sum(self.get_unit_mineral_and_gas_cost(unit.type_id))  # Sum of minerals and gas
                for unit in enemy_combat_units
            )
            
            # Only count our units that are close enough to the enemy (within 30 distance)
            if enemy_combat_units:
                enemy_center = enemy_combat_units.center
                nearby_military_units = military_units.filter(
                    lambda unit: unit.distance_to(enemy_center) < 30
                )
                
                # Calculate our nearby military value
                our_nearby_army_value = sum(
                    sum(self.get_unit_mineral_and_gas_cost(unit.type_id))  # Sum of minerals and gas
                    for unit in nearby_military_units
                )
                
                # Attack if we have a significant army value advantage
                if our_nearby_army_value > enemy_army_value * 1.5:
                    print(f"Resource advantage detected: {our_nearby_army_value} vs {enemy_army_value}, attacking")
                    return True
        
        # Get total military supply for other conditions
        military_supply = self.get_military_supply()
        
        # Original attack conditions
        if military_supply > 20 * self.townhalls.ready.amount:
            print(f"Military supply {military_supply} > 20 * {self.townhalls.ready.amount}, attacking")
            return True
            
        if len(military_units) > 15 * min(4, self.townhalls.ready.amount):
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
        military_supply += self.units(UnitTypeId.SIEGETANK).amount * 4  # Siege Tank costs 3 supply
        military_supply += self.units(UnitTypeId.SIEGETANKSIEGED).amount * 4  # Include sieged tanks
        return military_supply

    async def append_addons(self):
        """Manage add-ons for barracks, factory, and starport."""
        # Handle barracks add-ons
        for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if not barracks.has_add_on and random.random() < 0.5:
                await self.append_addon(UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING, UnitTypeId.BARRACKSTECHLAB)
            else:
                await self.append_addon(UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING, UnitTypeId.BARRACKSREACTOR)

        # Add tech lab to factory for tanks
        for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
            if not factory.has_add_on:
                await self.append_addon(UnitTypeId.FACTORY, UnitTypeId.FACTORYFLYING, UnitTypeId.FACTORYTECHLAB)

        # Add tech lab to first starport for ravens, reactors to others
        starports = self.structures(UnitTypeId.STARPORT).ready.idle
        tech_lab_starports = self.structures(UnitTypeId.STARPORT).filter(
            lambda sp: sp.has_add_on and sp.add_on_tag in self.structures(UnitTypeId.STARPORTTECHLAB).tags
        )
        
        for starport in starports:
            if not starport.has_add_on:
                # Build tech lab if we don't have one yet
                if len(tech_lab_starports) < 1:
                    await self.append_addon(UnitTypeId.STARPORT, UnitTypeId.STARPORTFLYING, UnitTypeId.STARPORTTECHLAB)
                else:
                    await self.append_addon(UnitTypeId.STARPORT, UnitTypeId.STARPORTFLYING, UnitTypeId.STARPORTREACTOR)

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

    async def upgrade_army(self):
        # Only start upgrades when we have enough units
        if self.get_military_supply() < 30:
            return

        # Build Engineering Bays if we don't have them and can afford it
        if (len(self.structures(UnitTypeId.ENGINEERINGBAY)) + self.already_pending(UnitTypeId.ENGINEERINGBAY) < 2 and 
            self.can_afford(UnitTypeId.ENGINEERINGBAY)):
            await self.build_engineering_bay_if_needed()
            return

        # Build Factory if we don't have one (required for Armory)
        if (self.structures(UnitTypeId.BARRACKS).ready and
            not self.structures(UnitTypeId.FACTORY) and
            not self.already_pending(UnitTypeId.FACTORY) and
            self.can_afford(UnitTypeId.FACTORY)):
            await self.build_factory_if_needed()
            return

        # Build Armory for level 2 and 3 upgrades
        if (self.structures(UnitTypeId.ENGINEERINGBAY).ready and 
            self.structures(UnitTypeId.FACTORY).ready and  # Factory must be ready
            not self.structures(UnitTypeId.ARMORY) and 
            not self.already_pending(UnitTypeId.ARMORY) and 
            self.can_afford(UnitTypeId.ARMORY)):
            
            # Find placement for armory (no addon needed)
            if self.townhalls:
                pos = await self.find_placement(
                    UnitTypeId.ARMORY,
                    near_position=self.townhalls.first.position,
                    min_distance=5,
                    max_distance=20,
                    addon_space=False
                )
                
                if pos:
                    await self.build(UnitTypeId.ARMORY, near=pos)
            return

        # Get Engineering Bays
        ebays = self.structures(UnitTypeId.ENGINEERINGBAY).ready
        if not ebays:
            return

        has_armory = self.structures(UnitTypeId.ARMORY).ready.exists

        # Use first ebay for weapons
        if len(ebays) >= 1:
            if not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1):
                ebays[0].research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)
            elif has_armory and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2):
                ebays[0].research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2)
            elif has_armory and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3):
                ebays[0].research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3)

        # Use second ebay for armor
        if len(ebays) >= 2:
            if not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                ebays[1].research(UpgradeId.TERRANINFANTRYARMORSLEVEL1)
            elif has_armory and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL2):
                ebays[1].research(UpgradeId.TERRANINFANTRYARMORSLEVEL2)
            elif has_armory and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL3):
                ebays[1].research(UpgradeId.TERRANINFANTRYARMORSLEVEL3)

    async def find_placement(self, building_type, near_position, min_distance=7, max_distance=30, addon_space=False, placement_step=2):
        """
        Find a suitable placement for a building that ensures proper spacing and unit pathing.
        
        Args:
            building_type: The type of building to place
            near_position: The reference position to build near
            min_distance: Minimum distance from other buildings
            max_distance: Maximum distance from reference position
            addon_space: Whether to reserve space for an addon
            placement_step: Step size for the placement grid
            
        Returns:
            A Point2 position or None if no valid position found
        """
        # Increase min_distance to ensure better spacing between buildings
        # Original was 5-6, now using 7 by default (allows tanks to move through)
        
        # Create a list of potential positions in a spiral pattern
        positions = []
        for distance in range(7, max_distance, placement_step):
            for angle in range(0, 360, 20):  # Check every 20 degrees for more options
                radians = math.radians(angle)
                x = near_position.x + (distance * math.cos(radians))
                y = near_position.y + (distance * math.sin(radians))
                positions.append(Point2((x, y)))
        
        # Shuffle positions for more varied building placement
        random.shuffle(positions)
        
        # Get existing buildings
        existing_buildings = self.structures.not_flying
        
        # For buildings that need addon space, we need extra checking
        if addon_space:
            # Check these positions for both building and addon placement
            for pos in positions:
                # First check if we can place the building here
                if await self.can_place(building_type, pos):
                    # Check distance to other buildings (needs to be larger for better pathing)
                    if all(building.distance_to(pos) > min_distance for building in existing_buildings):
                        # Then check if we can place an addon (use supply depot as a proxy for addon size)
                        addon_pos = Point2((pos.x + 2.5, pos.y - 0.5))
                        if await self.can_place(UnitTypeId.SUPPLYDEPOT, addon_pos):
                            # Final check: verify pathing in the surrounding area
                            # Create a grid of points around the building to check for pathing
                            path_check_points = []
                            for x_offset in [-3, 0, 3]:
                                for y_offset in [-3, 0, 3]:
                                    if x_offset == 0 and y_offset == 0:
                                        continue  # Skip the center point (where building will be)
                                    path_check_points.append(Point2((pos.x + x_offset, pos.y + y_offset)))
                            
                            # Check if most of these points are in the pathing grid
                            valid_path_points = sum(1 for p in path_check_points if self.in_pathing_grid(p))
                            if valid_path_points >= 6:  # At least 6 of 8 points should be pathable
                                print(f"Found good placement for {building_type} with addon space at {pos}")
                                return pos
        else:
            # Regular building (no addon)
            for pos in positions:
                if await self.can_place(building_type, pos):
                    # Check distance to other buildings (needs to be larger for better pathing)
                    if all(building.distance_to(pos) > min_distance for building in existing_buildings):
                        # Verify pathing in the surrounding area
                        path_check_points = []
                        for x_offset in [-3, 0, 3]:
                            for y_offset in [-3, 0, 3]:
                                if x_offset == 0 and y_offset == 0:
                                    continue  # Skip the center
                                path_check_points.append(Point2((pos.x + x_offset, pos.y + y_offset)))
                        
                        valid_path_points = sum(1 for p in path_check_points if self.in_pathing_grid(p))
                        if valid_path_points >= 6:
                            print(f"Found good placement for {building_type} at {pos}")
                            return pos
        
        # If we get here, we couldn't find a position with our enhanced criteria
        print(f"Falling back to standard placement for {building_type}")
        # Fall back to standard placement but still with increased min_distance
        return await super().find_placement(building_type, near=near_position, placement_step=placement_step)

    def get_unit_mineral_and_gas_cost(self, unit_type_id: UnitTypeId) -> tuple[int, int]:
        """
        Get the mineral and gas cost of a unit type.
        Uses game data when possible, falls back to a comprehensive dictionary.
        
        Args:
            unit_type_id: The unit type ID to get costs for
            
        Returns:
            Tuple of (mineral_cost, gas_cost)
        """
        # Try to get from game data first
        try:
            unit_data = self._game_data.units[unit_type_id.value]
            if hasattr(unit_data, 'cost'):
                return (unit_data.cost.minerals, unit_data.cost.vespene)
        except (KeyError, AttributeError):
            pass
        
        # Comprehensive dictionary of unit costs (mineral, gas)
        unit_costs = {
            # Terran
            UnitTypeId.SCV: (50, 0),
            UnitTypeId.MARINE: (50, 0),
            UnitTypeId.MARAUDER: (100, 25),
            UnitTypeId.REAPER: (50, 50),
            UnitTypeId.GHOST: (150, 125),
            UnitTypeId.HELLION: (100, 0),
            UnitTypeId.HELLIONTANK: (100, 0),
            UnitTypeId.SIEGETANK: (150, 125),
            UnitTypeId.SIEGETANKSIEGED: (150, 125),
            UnitTypeId.CYCLONE: (150, 100),
            UnitTypeId.WIDOWMINE: (75, 25),
            UnitTypeId.WIDOWMINEBURROWED: (75, 25),
            UnitTypeId.THOR: (300, 200),
            UnitTypeId.THORAP: (300, 200),
            UnitTypeId.VIKINGFIGHTER: (150, 75),
            UnitTypeId.VIKINGASSAULT: (150, 75),
            UnitTypeId.MEDIVAC: (100, 100),
            UnitTypeId.LIBERATOR: (150, 150),
            UnitTypeId.LIBERATORAG: (150, 150),
            UnitTypeId.RAVEN: (100, 200),
            UnitTypeId.BANSHEE: (150, 100),
            UnitTypeId.BATTLECRUISER: (400, 300),
            
            # Protoss
            UnitTypeId.PROBE: (50, 0),
            UnitTypeId.ZEALOT: (100, 0),
            UnitTypeId.STALKER: (125, 50),
            UnitTypeId.SENTRY: (50, 100),
            UnitTypeId.ADEPT: (100, 25),
            UnitTypeId.HIGHTEMPLAR: (50, 150),
            UnitTypeId.DARKTEMPLAR: (125, 125),
            UnitTypeId.IMMORTAL: (275, 100),
            UnitTypeId.COLOSSUS: (300, 200),
            UnitTypeId.DISRUPTOR: (150, 150),
            UnitTypeId.ARCHON: (100, 300),  # Approximation (2 HTs)
            UnitTypeId.OBSERVER: (25, 75),
            UnitTypeId.WARPPRISM: (200, 0),
            UnitTypeId.PHOENIX: (150, 100),
            UnitTypeId.VOIDRAY: (250, 150),
            UnitTypeId.ORACLE: (150, 150),
            UnitTypeId.CARRIER: (350, 250),
            UnitTypeId.TEMPEST: (250, 175),
            UnitTypeId.MOTHERSHIP: (400, 400),
            
            # Zerg
            UnitTypeId.DRONE: (50, 0),
            UnitTypeId.ZERGLING: (25, 0),
            UnitTypeId.BANELING: (25, 25),  # Plus zergling cost
            UnitTypeId.ROACH: (75, 25),
            UnitTypeId.RAVAGER: (75, 75),  # Plus roach cost
            UnitTypeId.HYDRALISK: (100, 50),
            UnitTypeId.LURKER: (50, 100),  # Plus hydra cost
            UnitTypeId.INFESTOR: (100, 150),
            UnitTypeId.SWARMHOSTMP: (100, 75),
            UnitTypeId.ULTRALISK: (300, 200),
            UnitTypeId.OVERLORD: (100, 0),
            UnitTypeId.OVERSEER: (50, 50),  # Plus overlord cost
            UnitTypeId.MUTALISK: (100, 100),
            UnitTypeId.CORRUPTOR: (150, 100),
            UnitTypeId.BROODLORD: (150, 150),  # Plus corruptor cost
            UnitTypeId.VIPER: (100, 200),
        }
        
        # Return from dictionary if available, otherwise default to (100, 25)
        return unit_costs.get(unit_type_id, (100, 25))

def main():
    bot = SC2Bot()
    maps_pool = ["CatalystLE"]
    
    run_game(
        maps.get(maps_pool[0]),
        [
            Bot(Race.Terran, bot),
            Computer(Race.Protoss, Difficulty.Hard)
        ],
        realtime=False
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())