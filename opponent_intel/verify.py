"""Verify opponent-id resolution and strategy selection.

This is the proof that a bot can turn the in-game --OpponentId into a strategy.

    # look up one opponent by name OR by game_display_id UUID
    python opponent_intel/verify.py 12PoolBot
    python opponent_intel/verify.py 4a491758-76ff-40de-996c-018d49b6237f

    # self-test: resolve every known bot and show the strategy distribution
    python opponent_intel/verify.py --all
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opponent_intel import recommend_for, known_count
from opponent_intel.intel import _BOTS


def show_one(opponent_id: str) -> None:
    rec = recommend_for(opponent_id)
    print(f"\n  input --OpponentId : {opponent_id}")
    print(f"  resolved           : {'YES' if rec.known else 'NO (unknown -> safe default)'}")
    if rec.known:
        print(f"  opponent           : {rec.name} [{rec.race}] — {rec.style}")
    print(f"  play-style         : {rec.opp_style}  ({rec.reason})")
    print(f"  -> HydraBot picks  : {rec.hydra_strategy}")
    print(f"  -> generic stance  : {rec.stance}")


def selftest() -> None:
    print(f"opponent_map: {known_count()} known bots\n")
    hydra = Counter()
    stance = Counter()
    # resolve each bot BOTH by its UUID and by its name; assert they agree
    mismatches = 0
    for uuid, e in _BOTS.items():
        by_uuid = recommend_for(uuid)
        by_name = recommend_for(e["name"])
        if by_uuid.hydra_strategy != by_name.hydra_strategy:
            mismatches += 1
            print(f"  MISMATCH {e['name']}: uuid->{by_uuid.hydra_strategy} name->{by_name.hydra_strategy}")
        hydra[by_uuid.hydra_strategy] += 1
        stance[by_uuid.opp_style] += 1
    print("HydraBot initial-strategy distribution across known opponents:")
    for k, n in hydra.most_common():
        print(f"  {k:<18} {n}")
    print("\nopponent play-style distribution:")
    for k, n in stance.most_common():
        print(f"  {k:<16} {n}")
    # unknown opponent -> safe default
    unk = recommend_for("00000000-dead-beef-0000-000000000000")
    print(f"\nunknown UUID -> known={unk.known}, hydra={unk.hydra_strategy}, stance={unk.stance}")
    assert not unk.known and unk.hydra_strategy == "MacroRoachHydra"
    assert mismatches == 0, f"{mismatches} uuid/name mismatches"
    print("\nOK: UUID and name resolve identically; unknown falls back safely.")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("--all", "-a", "--selftest"):
        selftest()
    else:
        for a in args:
            show_one(a)


if __name__ == "__main__":
    main()
