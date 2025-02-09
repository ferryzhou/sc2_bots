import sc2
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

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
        print (f"executing action {action}")
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
            print (f"training military {unit_type}")
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
            if self.can_afford(UnitTypeId.COMMANDCENTER):
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
        if iteration % 100 == 0:  # Every 100 iterations
            await self.manage_army()
            await self.manage_production()

    async def manage_army(self):
        # Get all military units
        military_units = self.units(UnitTypeId.MARINE) | self.units(UnitTypeId.MARAUDER)
        
        # Attack logic based on army size
        if military_units.amount > 5:
            target = None
            if self.enemy_units:
                target = self.enemy_units.random
            elif self.enemy_structures:
                target = self.enemy_structures.random
            else:
                target = self.enemy_start_locations[0]
                
            for unit in military_units:
                unit.attack(target)

    async def manage_production(self):
        # Build supply depots if needed
        if (
            self.supply_left < 5 
            and not self.already_pending(UnitTypeId.SUPPLYDEPOT)
            and self.can_afford(UnitTypeId.SUPPLYDEPOT)
        ):
            await self.build(UnitTypeId.SUPPLYDEPOT, near=self.townhalls.first)

        # Build barracks if needed
        if (
            len(self.units(UnitTypeId.BARRACKS)) < 3
            and self.can_afford(UnitTypeId.BARRACKS)
            and not self.already_pending(UnitTypeId.BARRACKS)
        ):
            await self.build(UnitTypeId.BARRACKS, near=self.townhalls.first)

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
        try:
            for cc in self.townhalls.ready.idle:
                if self.can_afford(UnitTypeId.SCV) and self.supply_left > 0:
                    cc.train(UnitTypeId.SCV)
        except Exception as e:
            print(f"Error training worker: {e}")

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