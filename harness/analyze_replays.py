"""Profile loss replays: what killed us, when, and how the economies compared.

Uses Blizzard's s2protocol (sc2reader cannot parse bot-vs-bot replays).

Usage:
    python harness/analyze_replays.py results/ladder_replays/loss_*.SC2Replay
"""

import sys
from collections import Counter

import mpyq
from s2protocol import versions

OUR_NAMES = {b"lishimin", b"PhoenixBot", b"GriffinBot"}
SAMPLE_MINUTES = (4, 6, 8, 10, 12, 16)
LOOPS_PER_MIN = 16 * 60  # tracker gameloops: 16/game-second


def load(path: str):
    archive = mpyq.MPQArchive(path)
    header = versions.latest().decode_replay_header(
        archive.header["user_data_header"]["content"]
    )
    protocol = versions.build(header["m_version"]["m_baseBuild"])
    details = protocol.decode_replay_details(archive.read_file("replay.details"))
    tracker = list(protocol.decode_replay_tracker_events(
        archive.read_file("replay.tracker.events")
    ))
    return details, tracker


def profile(path: str) -> None:
    try:
        details, tracker = load(path)
    except Exception as exc:  # noqa: BLE001
        print(f"{path}: unparseable ({type(exc).__name__}: {exc})")
        return

    players = details["m_playerList"]
    us_id = them_id = None
    them_name, them_race = "?", "?"
    for i, p in enumerate(players, start=1):
        name = p["m_name"].split(b"&gt;")[-1].replace(b"&lt;sp/", b"").strip()
        if any(n in p["m_name"] for n in OUR_NAMES):
            us_id = i
        else:
            them_id = i
            them_name = name.decode(errors="replace")
            them_race = p["m_race"].decode(errors="replace")

    if us_id is None or them_id is None:
        print(f"{path}: players not identified")
        return

    # stats trajectory + enemy early production
    stats: dict[int, dict[int, tuple]] = {us_id: {}, them_id: {}}
    enemy_prod: Counter = Counter()
    last_loop = 0
    for e in tracker:
        loop = e.get("_gameloop", 0)
        last_loop = max(last_loop, loop)
        if e["_event"] == "NNet.Replay.Tracker.SPlayerStatsEvent":
            pid = e["m_playerId"]
            if pid in stats:
                s = e["m_stats"]
                stats[pid][loop // LOOPS_PER_MIN] = (
                    s["m_scoreValueFoodUsed"] / 4096,
                    s["m_scoreValueMineralsUsedCurrentArmy"]
                    + s["m_scoreValueVespeneUsedCurrentArmy"],
                    s["m_scoreValueMineralsLostArmy"]
                    + s["m_scoreValueVespeneLostArmy"],
                )
        elif e["_event"] in ("NNet.Replay.Tracker.SUnitBornEvent",
                             "NNet.Replay.Tracker.SUnitInitEvent"):
            if (e.get("m_controlPlayerId") == them_id
                    and loop <= 8 * LOOPS_PER_MIN):
                name = e["m_unitTypeName"].decode(errors="replace")
                if name not in ("Larva", "Egg", "Broodling", "BroodlingEscort",
                                "MULE", "Interceptor"):
                    enemy_prod[name] += 1

    mins = last_loop / LOOPS_PER_MIN
    print(f"\n=== vs {them_name} ({them_race}) | ~{mins:.1f} min")
    print("  enemy first-8min production: "
          + ", ".join(f"{n}x{c}" for n, c in enemy_prod.most_common(9)))
    parts = []
    for m in SAMPLE_MINUTES:
        if m > mins:
            break
        o = stats[us_id].get(m)
        t = stats[them_id].get(m)
        if o and t:
            parts.append(f"{m}m supply {o[0]:.0f}v{t[0]:.0f} "
                         f"army {o[1]}v{t[1]}")
    print("  " + " | ".join(parts))
    o_end = stats[us_id].get(int(mins), stats[us_id].get(int(mins) - 1))
    t_end = stats[them_id].get(int(mins), stats[them_id].get(int(mins) - 1))
    if o_end and t_end:
        print(f"  final: our army {o_end[1]} lost-total {o_end[2]} | "
              f"their army {t_end[1]} lost-total {t_end[2]}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        profile(p)
