"""Run PhoenixBot against a sparring partner in-process (reliable, headless).

Unlike harness/versus.py (two ladder-client subprocesses, flaky), this runs
both bots in one SC2 instance via run_game -- deterministic and fast, ideal for
reproducing a specific loss and testing a fix.

    python sparring/vs_phoenix.py --bot stalker --map PylonAIE_v4
    python sparring/vs_phoenix.py --bot macroroach --games 3

Bots: fourgate (P zealot all-in), stalker (P one-base stalker all-in),
      massling (Z ling all-in), macroroach (Z roach/ling macro).
"""
import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PHOENIX = REPO / "phoenix"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "sparring"))
sys.path.insert(0, str(PHOENIX))
# PhoenixBot reads config.yml / protoss_builds.yml / data from phoenix/
os.chdir(PHOENIX)

from sc2 import maps
from sc2.data import Race, Result
from sc2.main import run_game
from sc2.player import Bot

from bot.main import PhoenixBot
from four_gate_zealot_bot import FourGateZealotBot
from mass_ling_bot import MassLingBot
from one_base_stalker_bot import OneBaseStalkerBot
from macro_roach_bot import MacroRoachBot

SPARRING = {
    "fourgate": (FourGateZealotBot, Race.Protoss),
    "stalker": (OneBaseStalkerBot, Race.Protoss),
    "massling": (MassLingBot, Race.Zerg),
    "macroroach": (MacroRoachBot, Race.Zerg),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bot", default="stalker", choices=sorted(SPARRING))
    ap.add_argument("--map", default="PylonAIE_v4")
    ap.add_argument("--games", type=int, default=1)
    ap.add_argument("--save-replay", action="store_true")
    args = ap.parse_args()

    bot_cls, race = SPARRING[args.bot]
    results = []
    for i in range(args.games):
        replay = (str(REPO / f"sparring_phoenix_vs_{args.bot}_{i}.SC2Replay")
                  if args.save_replay else None)
        r = run_game(
            maps.get(args.map),
            [Bot(Race.Protoss, PhoenixBot(), "PhoenixBot"),
             Bot(race, bot_cls(), args.bot)],
            realtime=False,
            disable_fog=False,
            save_replay_as=replay,
        )
        # run_game returns the result for the FIRST player (PhoenixBot)
        res = r[0] if isinstance(r, list) else r
        results.append(str(res))
        print(f"[{i+1}/{args.games}] PhoenixBot vs {args.bot} on {args.map}: {res}")

    w = sum(1 for r in results if "Victory" in r)
    l = sum(1 for r in results if "Defeat" in r)
    t = sum(1 for r in results if "Tie" in r)
    print(f"=== PhoenixBot {w}W-{l}L-{t}T vs {args.bot} ===")


if __name__ == "__main__":
    main()
