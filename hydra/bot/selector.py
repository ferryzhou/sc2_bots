"""selector: choose which of the five strategies to run, and switch mid-game.

This is the adaptive brain. It never hard-codes "if opponent does X play Y";
instead it reads the strategy_engine's opponent classification and its
recommended *counter stance*, and maps that stance onto our own strategy
spectrum (``Stance``). Because our profiles are tagged with the same spectrum the
engine uses to classify opponents, the mapping is a single, principled step:
play the counter to what the opponent has committed to.

Switching is guarded so the bot doesn't flip-flop:

* an all-in / opening-only strategy, once chosen, is committed to (you cannot
  "switch out of" a ling flood halfway -- the drones aren't there);
* you cannot switch *into* an opening-only strategy after the opening;
* a minimum dwell time between switches prevents thrashing on noisy scouting;
* a detected emergency overrides everything toward survival.

The result: the bot can start on any of the five strategies and re-choose from
the same five at any point in the game as its read of the opponent firms up.
"""

from __future__ import annotations

from typing import Dict, Optional

from loguru import logger

from strategy_engine import Advice, TradeVerdict

from .strategies import StrategyProfile, Stance, by_stance


# The engine's counter posture -> where we want to sit on our own spectrum.
# "play one notch toward what beats the opponent" is already baked into
# counter_stance; we just express its posture as a stance of ours.
_POSTURE_TO_STANCE = {
    "defensive": Stance.TURTLE,    # opponent is all-in/timing -> survive & out-tech
    "aggressive": Stance.TIMING,   # opponent is greedy -> punish with pressure
    "economic": Stance.GREEDY,     # opponent is turtling -> out-expand the map
    "standard": Stance.STANDARD,   # even/unknown -> straight macro
}

# minimum seconds a strategy runs before we allow a switch (anti-thrash)
_DWELL_SECONDS = 35.0
# a new read must persist this long before we act on it (kills flip-flopping on
# noisy frame-to-frame opponent classification)
_CONFIRM_SECONDS = 12.0
# after this we never *start* a fresh all-in (the economy is already committed)
_OPENING_SECONDS = 100.0


class StrategySelector:
    def __init__(
        self,
        library: Dict[str, StrategyProfile],
        initial: str,
        locked: bool = False,
    ):
        self.library = library
        self.by_stance = by_stance(library)
        self.locked = locked
        self.current: StrategyProfile = library[initial]
        self._last_switch_time: float = 0.0
        self._committed_all_in: bool = self.current.all_in
        self._candidate: Optional[Stance] = None
        self._candidate_since: float = 0.0

    def select(self, bot, advice: Advice) -> StrategyProfile:
        """Return the profile to run this step, switching if warranted."""
        if self.locked or self._committed_all_in:
            return self.current

        desired = self._desired_stance(bot, advice)
        target = self._resolve(desired)
        if target is None or target.name == self.current.name:
            self._candidate = None
            return self.current

        # A live emergency toward defence is acted on immediately -- survival
        # can't wait out the confirmation window.
        emergency_turtle = advice.defense.emergency and desired == Stance.TURTLE

        # Confirmation: a new read must persist before we trust it, so noisy
        # frame-to-frame opponent classification can't make us flip-flop.
        if self._candidate != desired:
            self._candidate = desired
            self._candidate_since = bot.time
        confirmed = bot.time - self._candidate_since >= _CONFIRM_SECONDS

        if not emergency_turtle:
            if bot.time - self._last_switch_time < _DWELL_SECONDS:
                return self.current
            if not confirmed:
                return self.current
        if target.opening_only and bot.time > _OPENING_SECONDS:
            return self.current

        self._switch_to(bot, target)
        self._candidate = None
        return self.current

    # ------------------------------------------------------------------ #
    def _desired_stance(self, bot, advice: Advice) -> Stance:
        # Survival first: a live emergency pins us defensive no matter the plan.
        if advice.defense.emergency:
            return Stance.TURTLE

        stance = _POSTURE_TO_STANCE.get(advice.counter.posture, Stance.STANDARD)

        # Efficiency overlay: if we are clearly losing trades, step one notch
        # toward safety; if we are clearly winning them, step toward pressure.
        verdict = advice.efficiency.verdict
        if verdict == TradeVerdict.TRADING_DOWN:
            stance = _shift(stance, +1)   # toward turtle
        elif verdict == TradeVerdict.TRADING_UP:
            stance = _shift(stance, -1)   # toward aggression
        return stance

    def _resolve(self, stance: Stance) -> Optional[StrategyProfile]:
        """Nearest available profile to the desired stance."""
        if stance in self.by_stance:
            return self.by_stance[stance]
        # fall back to the closest stance we do have a profile for
        best = None
        best_dist = 99
        for st, prof in self.by_stance.items():
            dist = abs(st.rank - stance.rank)
            if dist < best_dist:
                best, best_dist = prof, dist
        return best

    def _switch_to(self, bot, target: StrategyProfile) -> None:
        logger.info(
            f"{getattr(bot, 'time_formatted', int(bot.time))} strategy switch: "
            f"{self.current.name} -> {target.name} ({target.stance.value})"
        )
        self.current = target
        self._last_switch_time = bot.time
        if target.all_in:
            self._committed_all_in = True


def _shift(stance: Stance, delta: int) -> Stance:
    order = [Stance.CHEESE, Stance.TIMING, Stance.STANDARD, Stance.GREEDY, Stance.TURTLE]
    idx = max(0, min(len(order) - 1, stance.rank + delta))
    return order[idx]
