"""Map an opponent's play-style to a counter-strategy.

The bot profiles in ``bot_profiles/`` describe *what each opponent does*. This
module turns that into *what we should do about it*, using the economy-army
spectrum and counters from ``STRATEGY.md`` / ``OPPONENTS.md``:

    opponent play-style  --classify_style-->  OPP_STYLE (enum)
    OPP_STYLE            --HYDRA_STRATEGY-->   one of HydraBot's 5 strategies
    OPP_STYLE            --STANCE-->           a race-agnostic stance (any bot)

Pure data + string logic: no game or network imports, so it can run inside a
bot's ``on_start`` with zero overhead.
"""
from __future__ import annotations

# The opponent play-styles we bucket every bot into.
OPP_STYLES = (
    "allin",          # rushes / floods / one-base timings — beat us before ~8 min
    "macro_greedy",   # over-drone / greedy expand — thin army now, huge later
    "macro_standard", # balanced bio/gateway/roach macro — no exploitable extreme
    "turtle",         # static defense (cannon/mech/queen-creep) into a strong late
    "air_tech",       # skytoss / mutalisk / banshee — needs a specific anti-air answer
    "robo_timing",    # immortal / robo timing push
    "broken",         # currently passive / broken / losing everything
    "unknown",        # no profile — fall back to a safe default
)

# Keyword buckets, checked in priority order (first match wins). Matched against
# the lowercased STYLE string from the bot profiles (e.g. "Protoss zealot flood").
_RULES = [
    ("broken",         ("broken", "weak form", "unstable", "dev,", "dev)", "passive", "insufficient")),
    ("allin",          ("flood", "all-in", "all in", "allin", "rush", "one-base",
                        "one base", "cheese", "proxy", "reaper all")),
    ("air_tech",       ("skytoss", "tempest", "carrier", "void", "mutalisk", "muta",
                        "banshee", "stargate", "phoenix", "air")),
    ("turtle",         ("cannon", "turtle", "queen/creep", "queen ", "queen+")),
    ("robo_timing",    ("immortal", "robo")),
    ("macro_greedy",   ("over-drone", "over drone", "greedy", "drone macro")),
    ("macro_standard", ("macro", "bio", "gateway", "mech", "roach", "ling",
                        "stalker", "deathball", "marine")),
]


def classify_style(style: str, race: str = "") -> str:
    """Bucket a profile STYLE string into one OPP_STYLE."""
    s = (style or "").lower()
    if not s:
        return "unknown"
    for opp_style, keys in _RULES:
        if any(k in s for k in keys):
            return opp_style
    return "unknown"


# HydraBot (Zerg) counter — one of the five declarative strategies in
# hydra/zerg_strategies.yml. Rationale in the comment on each line.
HYDRA_STRATEGY = {
    # Enemy rushes us: get fast roaches to HOLD the flood at the choke, then
    # counter — never trade a mutual all-in (OPPONENTS.md: hold, don't trade).
    "allin":          "RoachTiming",
    # Enemy over-drones / greeds: punish the thin-army window with an early ling
    # flood before they remax (STRATEGY.md: aggression beats greed).
    "macro_greedy":   "LingFlood",
    # Balanced opponent: play our own strong standard macro, win on execution.
    "macro_standard": "MacroRoachHydra",
    # Enemy turtles: out-expand and out-tech it — take the map to a lurker/hydra
    # late game (STRATEGY.md: greed beats turtle; don't attack static defense).
    "turtle":         "GreedyHydraLurker",
    # Enemy goes air: hydralisks are the anti-air answer — standard macro with
    # a hydra core and detection.
    "air_tech":       "MacroRoachHydra",
    # Immortal/robo timing: hydra/ling out-value armored immortals; hold with a
    # standard macro rather than feeding roaches into immortals.
    "robo_timing":    "MacroRoachHydra",
    # Broken/passive opponent: be greedy and take the free win.
    "broken":         "GreedyHydraLurker",
    # No prior: safe, flexible default.
    "unknown":        "MacroRoachHydra",
}

# Race-agnostic stance any bot (e.g. GriffinBot/Terran) can read and translate
# into its own openings and behaviour.
STANCE = {
    "allin":          "hold_defensive",   # wall, static defense, no greed, don't move out
    "macro_greedy":   "punish_timing",    # timing attack / worker harass in the thin window
    "macro_standard": "standard",         # even game — win on upgrades/execution
    "turtle":         "out_expand",       # take the map, out-macro, siege from range
    "air_tech":       "anti_air",         # early detection/anti-air BEFORE it lands
    "robo_timing":    "focus_splash",     # splash + focus the immortals; defend the timing
    "broken":         "greedy",           # macro straight up, free win
    "unknown":        "standard_safe",    # default: safe opening until scouted
}

_EXPLAIN = {
    "allin":          "opponent rushes/floods early — hold defensively, don't trade",
    "macro_greedy":   "opponent over-drones/greeds — punish the thin-army window",
    "macro_standard": "balanced macro opponent — win on execution and upgrades",
    "turtle":         "opponent turtles — out-expand and out-tech, avoid static defense",
    "air_tech":       "opponent techs to air — get anti-air/detection early",
    "robo_timing":    "immortal/robo timing — splash + focus fire, defend the push",
    "broken":         "opponent is passive/broken — be greedy, take the free win",
    "unknown":        "no prior on this opponent — safe default, scout to classify",
}


def explain(opp_style: str) -> str:
    return _EXPLAIN.get(opp_style, _EXPLAIN["unknown"])


def hydra_strategy(opp_style: str) -> str:
    return HYDRA_STRATEGY.get(opp_style, HYDRA_STRATEGY["unknown"])


def stance(opp_style: str) -> str:
    return STANCE.get(opp_style, STANCE["unknown"])
