#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import timedelta

try:
    import sc2reader
    from sc2reader.engine.plugins import SelectionTracker, APMTracker
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Required packages not installed. Please install them with:")
    print("pip install sc2reader matplotlib numpy")
    sys.exit(1)


def format_time(seconds):
    """Format seconds into MM:SS format."""
    return str(timedelta(seconds=seconds))[2:7]


def analyze_replay(replay_path, generate_graphs=True):
    """Analyze a replay file using sc2reader."""
    print(f"Analyzing replay: {replay_path}")
    
    # Load the replay
    replay = sc2reader.load_replay(str(replay_path), load_level=4)
    replay.load_map()
    replay.load_all_details()
    
    # Add tracker plugins
    sc2reader.engine.register_plugin(SelectionTracker())
    sc2reader.engine.register_plugin(APMTracker())
    
    # Basic replay info
    print("\n=== Replay Information ===")
    print(f"Map: {replay.map_name}")
    print(f"Game Length: {format_time(replay.game_length.seconds)}")
    print(f"Game Version: {replay.release_string}")
    print(f"Game Date: {replay.date}")
    
    # Player information
    print("\n=== Players ===")
    for player in replay.players:
        print(f"Player: {player.name} ({player.play_race})")
#        print(f"  APM: {player.avg_apm}")
        print(f"  Result: {player.result}")
    
    # Build orders
    print("\n=== Build Orders ===")
    build_orders = defaultdict(list)
    
    for event in replay.events:
        if event.name == "UnitBornEvent" and event.control_pid > 0:
            player = replay.player[event.control_pid]
            game_time = format_time(event.second)
            unit_name = event.unit.name
            
            # Skip worker units after early game (optional)
            if event.second > 300 and unit_name in ["SCV", "Probe", "Drone"]:
                continue
                
            # Supply information isn't directly available in UnitBornEvent
            build_orders[player.name].append((event.second, game_time, unit_name))
    
    # Print build orders by player
    for player_name, builds in build_orders.items():
        print(f"\nBuild Order for {player_name}:")
        print(f"{'Time':8} {'Unit':25}")
        print("-" * 35)
        
        # Sort by time
        for _, game_time, unit_name in sorted(builds, key=lambda x: x[0]):
            print(f"{game_time:8} {unit_name:25}")
    
    # Analyze unit production
    print("\n=== Unit Production Summary ===")
    unit_counts = defaultdict(lambda: defaultdict(int))
    
    for event in replay.events:
        if event.name == "UnitBornEvent" and event.control_pid > 0:
            player = replay.player[event.control_pid]
            unit_counts[player.name][event.unit.name] += 1
    
    for player_name, units in unit_counts.items():
        print(f"\nUnits for {player_name}:")
        for unit_name, count in sorted(units.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {unit_name:25}: {count}")
    
    # Analyze upgrades
    print("\n=== Upgrades ===")
    upgrades = defaultdict(list)
    
    for event in replay.events:
        if event.name == "UpgradeCompleteEvent":
            player = replay.player[event.pid]
            game_time = format_time(event.second)
            upgrade_name = event.upgrade_type_name
            
            upgrades[player.name].append((event.second, game_time, upgrade_name))
    
    for player_name, player_upgrades in upgrades.items():
        print(f"\nUpgrades for {player_name}:")
        print(f"{'Time':8} {'Upgrade':30}")
        print("-" * 40)
        
        # Sort by time
        for _, game_time, upgrade_name in sorted(player_upgrades, key=lambda x: x[0]):
            print(f"{game_time:8} {upgrade_name:30}")

    # Generate graphs if requested
    if generate_graphs:
        generate_resource_graph(replay)
        generate_units_graph(replay)


def generate_resource_graph(replay):
    """Generate a graph showing resource collection over time."""
    print("\n=== Generating Resource Graph ===")
    
    # Initialize data structures
    timestamps = []
    minerals_by_player = defaultdict(list)
    vespene_by_player = defaultdict(list)
    
    # Collect resource data
    for event in replay.events:
        if event.name == "PlayerStatsEvent":
            player = replay.player[event.pid]
            timestamps.append(event.second / 60.0)  # Convert to minutes
            minerals_by_player[player.name].append(event.minerals_collection_rate)
            vespene_by_player[player.name].append(event.vespene_collection_rate)
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Plot minerals
    plt.subplot(1, 2, 1)
    for player_name, minerals in minerals_by_player.items():
        plt.plot(timestamps[:len(minerals)], minerals, label=f"{player_name} Minerals")
    
    plt.title("Mineral Collection Rate")
    plt.xlabel("Game Time (minutes)")
    plt.ylabel("Collection Rate")
    plt.legend()
    plt.grid(True)
    
    # Plot vespene
    plt.subplot(1, 2, 2)
    for player_name, vespene in vespene_by_player.items():
        plt.plot(timestamps[:len(vespene)], vespene, label=f"{player_name} Vespene")
    
    plt.title("Vespene Collection Rate")
    plt.xlabel("Game Time (minutes)")
    plt.ylabel("Collection Rate")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    output_path = Path(replay.filename).with_suffix('.resources.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Resource graph saved to: {output_path}")


def generate_units_graph(replay):
    """Generate a graph showing unit counts over time."""
    print("\n=== Generating Units Graph ===")
    
    # Initialize data structures
    max_time = int(replay.game_length.total_seconds())
    time_points = list(range(0, max_time + 60, 60))  # Every minute
    
    # Track units by player and type over time
    units_over_time = defaultdict(lambda: defaultdict(lambda: [0] * len(time_points)))
    
    # Process unit creation and destruction events
    for event in replay.events:
        if event.name == "UnitBornEvent" and event.control_pid > 0:
            player = replay.player[event.control_pid]
            unit_name = event.unit.name
            time_index = min(len(time_points) - 1, event.second // 60)
            
            # Increment unit count for all time points after this one
            for i in range(time_index, len(time_points)):
                units_over_time[player.name][unit_name][i] += 1
                
        elif event.name == "UnitDiedEvent" and hasattr(event, 'unit') and hasattr(event.unit, 'owner'):
            if event.unit.owner:
                player_name = event.unit.owner.name
                unit_name = event.unit.name
                time_index = min(len(time_points) - 1, event.second // 60)
                
                # Decrement unit count for all time points after this one
                for i in range(time_index, len(time_points)):
                    if units_over_time[player_name][unit_name][i] > 0:
                        units_over_time[player_name][unit_name][i] -= 1
    
    # Filter out worker units and common units to make the graph more readable
    common_units = {"SCV", "Probe", "Drone", "Larva", "Egg", "Overlord"}
    
    # Create a plot for each player
    for player_name, unit_data in units_over_time.items():
        plt.figure(figsize=(14, 8))
        
        # Filter to important units (exclude workers and have at least 1 at some point)
        important_units = {unit: counts for unit, counts in unit_data.items() 
                          if unit not in common_units and max(counts) > 0}
        
        # Sort units by their maximum count
        sorted_units = sorted(important_units.items(), key=lambda x: max(x[1]), reverse=True)
        
        # Limit to top 10 units for readability
        for unit_name, counts in sorted_units[:10]:
            plt.plot(np.array(time_points) / 60, counts, label=unit_name)
        
        plt.title(f"Unit Counts Over Time for {player_name}")
        plt.xlabel("Game Time (minutes)")
        plt.ylabel("Unit Count")
        plt.legend()
        plt.grid(True)
        
        output_path = Path(replay.filename).with_suffix(f'.{player_name}.units.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Units graph for {player_name} saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze StarCraft II replays using sc2reader")
    parser.add_argument("replay_path", help="Path to the SC2Replay file")
    parser.add_argument("--no-graphs", action="store_true", help="Skip generating graphs")
    
    args = parser.parse_args()
    
    # Convert to absolute path if needed
    replay_path = Path(args.replay_path)
    if not replay_path.is_absolute():
        replay_path = Path(os.getcwd()) / replay_path
    
    if not replay_path.exists():
        print(f"Error: Replay file not found at {replay_path}")
        sys.exit(1)
    
    analyze_replay(replay_path, not args.no_graphs)


if __name__ == "__main__":
    main() 