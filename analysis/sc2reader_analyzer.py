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
except ImportError:
    print("sc2reader is not installed. Please install it with:")
    print("pip install sc2reader")
    sys.exit(1)


def format_time(seconds):
    """Format seconds into MM:SS format."""
    return str(timedelta(seconds=seconds))[2:7]


def analyze_replay(replay_path):
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


def main():
    parser = argparse.ArgumentParser(description="Analyze StarCraft II replays using sc2reader")
    parser.add_argument("replay_path", help="Path to the SC2Replay file")
    
    args = parser.parse_args()
    
    # Convert to absolute path if needed
    replay_path = Path(args.replay_path)
    if not replay_path.is_absolute():
        replay_path = Path(os.getcwd()) / replay_path
    
    if not replay_path.exists():
        print(f"Error: Replay file not found at {replay_path}")
        sys.exit(1)
    
    analyze_replay(replay_path)


if __name__ == "__main__":
    main() 