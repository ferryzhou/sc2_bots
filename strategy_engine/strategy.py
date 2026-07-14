"""strategy: classify the opponent and pick a counter stance.

Mirrors ``STRATEGY.md``. The core skill is reading *where on the economy-army
spectrum the opponent has committed*, then moving one notch toward the side that
beats it. ``classify_opponent`` reads scouted signals into an ``Archetype``;
``counter_stance`` returns the recommended response.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .state import GameState


class Archetype(Enum):
    UNKNOWN = "unknown"              # not enough scouting -- go scout
    CHEESE_ALLIN = "cheese_allin"   # all army, no economy
    TIMING_ATTACK = "timing_attack" # army-heavy, delayed economy
    STANDARD = "standard"           # balanced
    GREEDY_ECO = "greedy_eco"       # economy-heavy, light army
    TURTLE = "turtle"               # defense + tech to a strong late game


@dataclass
class Classification:
    archetype: Archetype
    confidence: float          # 0..1
    signals: List[str] = field(default_factory=list)


# Normal base count by game time -- used to judge "earlier/later than standard".
def _expected_bases(minutes: float) -> int:
    if minutes < 1.5:
        return 1
    if minutes < 4.0:
        return 2
    if minutes < 7.0:
        return 3
    return 4


def classify_opponent(state: GameState) -> Classification:
    """Read scouted signals into a strategy archetype.

    Uses the detection cheat-sheet from ``STRATEGY.md``: base count vs. worker
    count vs. army supply, expansion timing, tech/production, proxies, static
    defense, and -- loudest of all -- what is *missing*.
    """
    # A proxy / warp-in near our base, or an early army push, is an alarm on its
    # own -- it does not require having scouted the enemy's base. Fire before the
    # "unknown" gate so home-visible aggression is never missed for lack of a scout.
    home_aggression = state.enemy_proxy or (
        state.enemy_army_moving_out and state.game_minutes < 5.0
    )
    if home_aggression and not state.enemy_known:
        sig: List[str] = []
        if state.enemy_proxy:
            sig.append("proxy / warp-in near our base")
        if state.enemy_army_moving_out:
            sig.append("enemy army moving out early")
        sig.append("aggression seen from home without a base scout -- treat as all-in until disproven")
        return Classification(Archetype.CHEESE_ALLIN, 0.6, sig)

    if not state.enemy_known or state.scouting_stale:
        return Classification(
            Archetype.UNKNOWN,
            confidence=0.0,
            signals=["no fresh scouting -- classify after scouting the enemy"],
        )

    minutes = state.game_minutes
    bases = state.enemy_base_count or 1
    workers = state.enemy_worker_count
    army = state.enemy_army_supply
    prod = state.enemy_production_structures or 0
    tech = state.enemy_tech_structures or 0
    defense = state.enemy_static_defense or 0
    gas = state.enemy_gas_count  # None == not scouted
    expected = _expected_bases(minutes)

    signals: List[str] = []

    # --- Cheese / all-in: one base, aggression markers, economy missing. -----
    cheese_score = 0
    if bases <= 1 and minutes > 1.5:
        cheese_score += 1
        signals.append("still on one base past the opening")
    if state.enemy_proxy:
        cheese_score += 2
        signals.append("proxy buildings near our base")
    if workers is not None and workers < 14 and minutes > 2.0:
        cheese_score += 1
        signals.append(f"low worker count ({workers}) -- economy sacrificed")
    if state.enemy_army_moving_out and minutes < 4.0:
        cheese_score += 1
        signals.append("army moving out very early")
    if cheese_score >= 3:
        return Classification(Archetype.CHEESE_ALLIN, min(1.0, cheese_score / 4), signals)

    # --- Timing attack: delayed expansion, heavy army/production. ------------
    timing_score = 0
    if bases < expected:
        timing_score += 1
        signals.append(f"expansion behind standard ({bases} vs ~{expected})")
    # Production count relative to base is the core tell. Many production
    # buildings on a *single* base is the shape of a gateway/rax all-in and
    # counts double -- this is what a scout of the 4-gate actually sees.
    if bases <= 1 and prod >= 3:
        timing_score += 2
        signals.append(f"{prod} production buildings on one base -- gateway/rax all-in shape")
    elif prod >= 3 and bases <= 2:
        timing_score += 1
        signals.append(f"many production buildings ({prod}) on a small economy")
    # No gas on one base with multiple production = a mass-gateway/zealot (or
    # mass-marine) all-in -- the clearest gas-light aggression tell.
    if bases <= 1 and gas == 0 and prod >= 2 and minutes > 1.5:
        timing_score += 1
        signals.append("no gas + multiple production on one base -- gas-light mass-unit all-in")
    # Stalled economy: workers capped low on one base = resources going to army.
    if bases <= 1 and workers is not None and workers <= 18 and minutes > 2.0:
        timing_score += 1
        signals.append(f"worker count stalled ({workers}) on one base -- committing to army")
    if army is not None and army >= state.army_supply + 4:
        timing_score += 1
        signals.append("army supply spiking ahead of ours")
    if state.enemy_army_moving_out:
        timing_score += 1
        signals.append("army massing / moving out")
    if timing_score >= 3:
        return Classification(Archetype.TIMING_ATTACK, min(1.0, timing_score / 4), signals)

    # --- Turtle: static defense + tech, few units out. ----------------------
    turtle_score = 0
    if defense >= 3:
        turtle_score += 2
        signals.append(f"heavy static defense ({defense})")
    if tech >= 2:
        turtle_score += 1
        signals.append(f"tech-focused ({tech} tech structures)")
    if army is not None and army < state.army_supply and not state.enemy_army_moving_out:
        turtle_score += 1
        signals.append("few units leaving home")
    if turtle_score >= 3:
        return Classification(Archetype.TURTLE, min(1.0, turtle_score / 4), signals)

    # --- Greedy / economic: extra bases, light army. ------------------------
    greedy_score = 0
    if bases > expected:
        greedy_score += 2
        signals.append(f"expanded ahead of standard ({bases} vs ~{expected})")
    # A third-or-later base defended by a minimal army is the clearest greed tell.
    if bases >= 3 and army is not None and army < 4 * bases:
        greedy_score += 2
        signals.append(f"{bases} bases held by a minimal army ({army:.0f} supply)")
    if army is not None and army + 3 < state.army_supply:
        greedy_score += 1
        signals.append("light army relative to ours")
    if workers is not None and workers >= 22 * bases * 0.8 and prod <= 2:
        greedy_score += 1
        signals.append("workers prioritized over production")
    if greedy_score >= 2:
        return Classification(Archetype.GREEDY_ECO, min(1.0, greedy_score / 4), signals)

    # --- Default: standard macro. -------------------------------------------
    signals.append("balanced economy and army -- standard macro")
    return Classification(Archetype.STANDARD, 0.5, signals)


@dataclass
class CounterStance:
    posture: str        # "defensive" | "standard" | "aggressive" | "economic"
    actions: List[str]  # concrete recommendations


def counter_stance(classification: Classification) -> CounterStance:
    """The counter for each archetype -- move one notch toward what beats it."""
    a = classification.archetype
    if a == Archetype.UNKNOWN:
        return CounterStance(
            "standard",
            ["scout to locate the opponent on the spectrum before committing",
             "when unsure, err toward safety -- keep some army and defense"],
        )
    if a == Archetype.CHEESE_ALLIN:
        return CounterStance(
            "defensive",
            ["wall the ramp and add static defense",
             "pull workers to hold if needed -- do not die",
             "survive, then expand and punish their dead economy"],
        )
    if a == Archetype.TIMING_ATTACK:
        return CounterStance(
            "defensive",
            ["hold economy back until safe -- do not over-expand into it",
             "match composition and defend at the choke with defender's advantage",
             "after it breaks, expand and punish their behind economy"],
        )
    if a == Archetype.GREEDY_ECO:
        return CounterStance(
            "aggressive",
            ["apply pressure or a timing attack into the thin-army window",
             "force worker pulls or take a base off them",
             "if you cannot punish, match their economy"],
        )
    if a == Archetype.TURTLE:
        return CounterStance(
            "economic",
            ["take the rest of the map -- out-expand them",
             "do not attack into static defense",
             "hit before their key tech, or tech to your own counter"],
        )
    return CounterStance(
        "standard",
        ["play macro straight and win on execution",
         "look for an edge in upgrades, composition, or a small timing"],
    )
