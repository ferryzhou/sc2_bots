import sc2
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3

from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from collections import deque
import random
import os
import json
from datetime import datetime

class SC2MLBot(BotAI):
    def __init__(self, model_name="sc2_ml_model"):
        super().__init__()
        self.model_name = model_name
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 32
        
        # State and action tracking
        self.last_state = None
        self.last_action = None
        self.current_game_memory = []
        
        # Metrics
        self.games_played = 0
        self.wins = 0
        self.total_score = 0
        self.training_history = []
        self.load_training_history()

        self.model = self._build_or_load_model()

    def _build_model(self):
        model = models.Sequential([
            layers.Dense(512, input_shape=(10,), activation='relu'),
            layers.Dense(512, activation='relu'),
            layers.Dense(256, activation='relu'),
            layers.Dense(5, activation='linear')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                     loss='mse')
        return model

    def _build_or_load_model(self):
        model_path = f"models/{self.model_name}"
        if os.path.exists(model_path):
            try:
                print(f"Loading existing model from {model_path}")
                return models.load_model(model_path)
            except Exception as e:
                print(f"Error loading model: {e}")
                print("Creating new model instead")
                return self._build_model()
        else:
            print("Creating new model")
            os.makedirs("models", exist_ok=True)
            return self._build_model()

    def choose_action(self, state):
        try:
            if np.random.rand() <= self.epsilon:
                return random.randrange(5)
            act_values = self.model.predict(state.reshape(1, -1), verbose=0)
            return np.argmax(act_values[0])
        except Exception as e:
            print(f"Error choosing action: {e}")
            return random.randrange(5)  # Return random action in case of error

    async def execute_action(self, action):
        #  print (f"executing action {action}")
        try:
            if action == 0:  # Build Marines
                await self.train_military(UnitTypeId.MARINE)
            elif action == 1:  # Build Marauders
                await self.train_military(UnitTypeId.MARAUDER)
            elif action == 2:  # Expand
                await self.expand()
            elif action == 3:  # Attack
                await self.manage_army()
            elif action == 4:  # Build SCV
                await self.train_worker()
        except Exception as e:
            print(f"Error executing action {action}: {e}")

    async def train_military(self, unit_type):
        try:
            # print (f"training military {unit_type}")
            for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
                print (f"found idle barracks, training military {unit_type}")
                if self.can_afford(unit_type) and self.supply_left > 2:
                    print (f"can afford {unit_type}, training")
                    barracks.train(unit_type)
                else:
                    print (f"cannot afford {unit_type}, or supply left is {self.supply_left}")
        except Exception as e:
            print(f"Error training military: {e}")

    async def expand(self):
        try:
            MAX_BASES = 8
            if len(self.townhalls) < MAX_BASES and self.can_afford(UnitTypeId.COMMANDCENTER):
                await self.expand_now()
        except Exception as e:
            print(f"Error expanding: {e}")

    async def train_batch(self):
        if len(self.memory) < self.batch_size:
            return
        
        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([transition[0] for transition in minibatch])
        actions = np.array([transition[1] for transition in minibatch])
        rewards = np.array([transition[2] for transition in minibatch])
        next_states = np.array([transition[3] for transition in minibatch])
        dones = np.array([transition[4] for transition in minibatch])

        # Current Q-values for all actions in the batch
        targets = self.model.predict(states, verbose=0)
        # Next Q-values for all actions in the batch
        next_q_values = self.model.predict(next_states, verbose=0)

        # Update Q-values for the actions that were taken
        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])

        # Train the model with updated Q-values
        self.model.fit(states, targets, epochs=1, verbose=0)

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    async def get_state(self):
        try:
            state = [
                self.minerals/1000,
                self.vespene/1000,
                self.supply_used/200,
                self.supply_cap/200,
                len(self.units(UnitTypeId.MARINE))/50,
                len(self.units(UnitTypeId.MARAUDER))/30,
                len(self.units(UnitTypeId.BARRACKS))/10,
                len(self.townhalls)/5,
                len(self.enemy_units)/50,
                self.time/1000
            ]
            return np.array(state)
        except Exception as e:
            print(f"Error getting state: {e}")
            return np.zeros(10)  # Return zero state in case of error


    def calculate_reward(self, current_state):
        # Base reward components
        military_value = (
            len(self.units(UnitTypeId.MARINE)) * 50 +
            len(self.units(UnitTypeId.MARAUDER)) * 100
        )
        
        economy_value = (
            self.minerals/100 +
            self.vespene/100 +
            len(self.workers) * 50
        )
        
        # Combat performance
        killed_value = (
            self.state.score.killed_minerals_army +
            self.state.score.killed_vespene_army
        ) / 100
        
        lost_value = (
            self.state.score.lost_minerals_army +
            self.state.score.lost_vespene_army
        ) / 100
        
        # Final reward calculation
        reward = (
            military_value +
            economy_value +
            killed_value -
            lost_value
        )
        
        # Additional rewards/penalties
        if len(self.townhalls) == 0:  # Severe penalty for losing all bases
            reward -= 5000
        
        if self.supply_used == self.supply_cap:  # Penalty for supply block
            reward -= 100
            
        return reward

    async def on_step(self, iteration):
        # Basic economy management
        await self.distribute_workers()
        
        # Get current state
        current_state = await self.get_state()
        
        # Choose action
        action = self.choose_action(current_state)
        
        # Execute chosen action
        await self.execute_action(action)
        
        # Calculate reward
        reward = self.calculate_reward(current_state)
        
        # Store transition in current game memory
        if self.last_state is not None:
            self.current_game_memory.append((
                self.last_state,
                self.last_action,
                reward,
                current_state,
                False  # not done yet
            ))
            
            # Add to main memory and train
            self.memory.append((
                self.last_state,
                self.last_action,
                reward,
                current_state,
                False
            ))
            await self.train_batch()
        
        # Update state and action
        self.last_state = current_state
        self.last_action = action
        
        # Additional game management
        if iteration % 10 == 0:  # Every 10 iterations
            print (f"iteration {iteration}")
            await self.manage_army()
            await self.manage_production()

    async def manage_army(self):
        if not self.should_attack():
            return

        # Should attack.
        # Get all military units
        military_units = self.units(UnitTypeId.MARINE) | self.units(UnitTypeId.MARAUDER)
        target = None
        if self.enemy_units:
            for unit in military_units:
                closest_enemy = self.enemy_units.closest_to(unit)
                unit.attack(closest_enemy)
            return
        elif self.enemy_structures:
            target = self.enemy_structures.random
        else:
            target = self.enemy_start_locations[0]
            
        print (f"attacking {target}")
        for unit in military_units:
            unit.attack(target)

    async def manage_production(self):
        print (f"manage_production")
        # Build supply depots if needed
        if (
            self.supply_left < 5 * self.townhalls.amount
            and not self.already_pending(UnitTypeId.SUPPLYDEPOT)
            and self.can_afford(UnitTypeId.SUPPLYDEPOT)
        ):
            await self.build(UnitTypeId.SUPPLYDEPOT, near=self.townhalls.first)

        # Lower completed supply depots
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
        
        # Raise if enemies nearby
        for depot in self.structures(UnitTypeId.SUPPLYDEPOTLOWERED).ready:
            if self.enemy_units:
                closest_enemy = self.enemy_units.closest_to(depot)
                if closest_enemy.distance_to(depot) < 10:
                    depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)

        await self.build_gas_if_needed()

        await self.build_barracks_if_needed()

        # Add Tech Lab to Barracks for Marauders
        await self.append_addon(UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING, UnitTypeId.BARRACKSTECHLAB)

    async def build_gas_if_needed(self):
        # Build refineries (on nearby vespene) when at least one barracks is in construction
        if (
            self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(UnitTypeId.BARRACKS) > 0
            and self.already_pending(UnitTypeId.REFINERY) < 1
        ):
            # Loop over all townhalls that are 100% complete
            for th in self.townhalls.ready:
                # Find all vespene geysers that are closer than range 10 to this townhall
                vgs = self.vespene_geyser.closer_than(10, th)
                for vg in vgs:
                    if await self.can_place_single(UnitTypeId.REFINERY, vg.position) and self.can_afford(
                        UnitTypeId.REFINERY
                    ):
                        workers = self.workers.gathering
                        if workers:  # same condition as above
                            worker = workers.closest_to(vg)
                            # Caution: the target for the refinery has to be the vespene geyser, not its position!
                            worker.build_gas(vg)

                            # Dont build more than one each frame
                            break

    async def append_addon(self, building_type, building_flying_type, add_on_type):
        def points_to_build_addon(building_position: Point2) -> list[Point2]:
            """Return all points that need to be checked when trying to build an addon. Returns 4 points."""
            addon_offset: Point2 = Point2((2.5, -0.5))
            addon_position: Point2 = building_position + addon_offset
            addon_points = [
                (addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)
            ]
            return addon_points

        for building in self.structures(building_type).ready.idle:
            print (f"{building} has_add_on {building.has_add_on}")
            if not building.has_add_on and self.can_afford(add_on_type):
                print (f"no add on, can aford, try building tech lab")
                addon_points = points_to_build_addon(building.position)
                if all(
                    self.in_map_bounds(addon_point)
                    and self.in_placement_grid(addon_point)
                    and self.in_pathing_grid(addon_point)
                    for addon_point in addon_points
                ):
                    print (f"all points are valid, building tech lab")
                    building.build(add_on_type)
                else:
                    print (f"points are not valid, lifting")
                    building(AbilityId.LIFT)
            else:
                print (f"has_add_on {building.has_add_on} and cannot afford tech lab")

        def land_positions(position: Point2) -> list[Point2]:
            """Return all points that need to be checked when trying to land at a location where there is enough space to build an addon. Returns 13 points."""
            land_positions = [(position + Point2((x, y))).rounded for x in range(-1, 2) for y in range(-1, 2)]
            return land_positions + points_to_build_addon(position)

        # Find a position to land for a flying starport so that it can build an addon
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

        # Show where it is flying to and show grid
        for sp in self.structures(building_type).filter(lambda unit: not unit.is_idle):
            if isinstance(sp.order_target, Point2):
                p = Point3((*sp.order_target, self.get_terrain_z_height(sp.order_target)))
                self.client.debug_box2_out(p, color=Point3((255, 0, 0)))

    async def on_end(self, result):
        # Calculate final reward based on game result
        final_reward = 5000 if result == sc2.Result.Victory else -5000
        
        # Add final transitions with done=True
        if self.current_game_memory:
            last_transition = self.current_game_memory[-1]
            final_transition = (
                last_transition[0],  # state
                last_transition[1],  # action
                final_reward,        # reward
                last_transition[3],  # next_state
                True                 # done
            )
            self.memory.append(final_transition)
        
        # Update metrics
        self.games_played += 1
        if result == sc2.Result.Victory:
            self.wins += 1
        
        # Save progress
        self.save_model()
        self.save_training_history()
        
        # Clear current game memory
        self.current_game_memory = []
        self.last_state = None
        self.last_action = None
        
        # Print game summary
        print(f"\nGame {self.games_played} finished!")
        print(f"Result: {result}")
        print(f"Win rate: {(self.wins/self.games_played)*100:.2f}%")
        print(f"Current epsilon: {self.epsilon}")

    def load_training_history(self):
        history_path = f"training_history/{self.model_name}_history.json"
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.training_history = json.load(f)
                print(f"Loaded training history from {history_path}")
            except Exception as e:
                print(f"Error loading training history: {e}")
                self.training_history = []
        else:
            print("No training history found, starting fresh")
            os.makedirs("training_history", exist_ok=True)
            self.training_history = []

    def save_training_history(self):
        history_path = f"training_history/{self.model_name}_history.json"
        try:
            with open(history_path, 'w') as f:
                json.dump(self.training_history, f)
            print(f"Saved training history to {history_path}")
        except Exception as e:
            print(f"Error saving training history: {e}")

    async def train_worker(self):
        # Hard cap at 80 workers total
        if self.workers.amount >= 80:
            return
        
        # Also stop at 15 * townhalls workers (existing logic)
        if self.workers.amount >= 15 * self.townhalls.amount:
            return
        
        try:
            for cc in self.townhalls.ready.idle:
                if self.can_afford(UnitTypeId.SCV) and self.supply_left > 0:
                    cc.train(UnitTypeId.SCV)
        except Exception as e:
            print(f"Error training worker: {e}")

    def should_attack(self):
        # Count total military units
        military_units = self.units.filter(
            lambda unit: unit.type_id in {
                UnitTypeId.MARINE,
                UnitTypeId.MARAUDER,
                UnitTypeId.REAPER
            }
        )
        
        # Check if we have enough military units
        if len(military_units) > 20 * self.townhalls.amount:
            print (f"enough military units, attacking")
            return True
            
        # Check if enemy is close to our base
        if self.townhalls:
            main_base = self.townhalls.first
            enemy_units = self.enemy_units | self.enemy_structures
            if enemy_units:
                closest_enemy = enemy_units.closest_to(main_base)
                if closest_enemy.distance_to(main_base) < 30:  # Defensive radius
                    print (f"enemy is close, attacking")
                    return True
                    
        # Check if we're at max supply (indicating a strong army)
        if self.supply_used > 190:
            print (f"supply used is max, attacking")
            return True
        
        return False

    async def build_barracks_if_needed(self):
        # Don't build if we can't afford it
        if not self.can_afford(UnitTypeId.BARRACKS):
            return
            
        # Get count of existing and in-progress barracks
        barracks_count = self.structures(UnitTypeId.BARRACKS).amount
        barracks_pending = self.already_pending(UnitTypeId.BARRACKS)

        # Stop building if have MAX_BARRACKS
        MAX_BARRACKS = 10
        if barracks_count + barracks_pending >= MAX_BARRACKS:
            return
        
        # Build if we have less than 3 barracks (including those in progress)
        if barracks_count + barracks_pending < 3 * self.townhalls.amount:
            print (f"{barracks_count} + {barracks_pending} < {3 * self.townhalls.amount}, building barracks")
            if self.townhalls:
                cc = self.townhalls.first
                # Try to build near command center
                pos = cc.position.towards(self.game_info.map_center, 8)
                await self.build(UnitTypeId.BARRACKS, near=pos)

def main():
    # Train the bot over multiple games
    bot = SC2MLBot()
    maps_pool = ["CatalystLE"]
    
    for _ in range(1):  # Train for 100 games
        current_map = random.choice(maps_pool)
        run_game(
            maps.get(current_map),
            [
                Bot(Race.Terran, bot),
                Computer(Race.Random, Difficulty.Medium)
            ],
            realtime=False
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())