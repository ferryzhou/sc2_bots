"""selector: choose which of the five strategies to run, and switch mid-game.

This is the adaptive brain. It never hard-codes "if opponent does X play Y";
instead it reads the strategy_engine's opponent classification and its
recommended *counter stance*, and maps that stance onto our own strategy
spectrum (``Stance``). Because our profiles are tagged with the same spectrum the
engine uses to classify opponents, the mapping is a single, principled step:
play the counter to what the opponent has committed to.

Switching is guarded so the bot doesn't flip-flop -- thrashing between strategies
costs more than it gains, because each switch abandons in-progress tech:

* an all-in / opening-only strategy, once chosen, is committed to (you cannot
  "switch out of" a ling flood halfway -- the drones aren't there);
* you cannot switch *into* an opening-only strategy after the opening;
* a new read must **persist** (confirmation window) before it's trusted, and a
  minimum **dwell** must pass since the last switch -- together these reject the
  frame-to-frame flicker in the opponent classifier;
* an immediate all-in defence does NOT force a whole-strategy switch: the planner
  already defends an emergency (freeze economy, static defence, hold) under any
  strategy, so a brief emergency blip can't yank us into turtle and back out.

The result: the bot can start on any of the five strategies and re-choose from
the same five as its read of the opponent *firms up* -- but only on a read that
actually holds, not on noise.
"""

from __future__ import annotations

from typing import Dict, Optional

from loguru import logger

from strategy_engine import Advice

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
_DWELL_SECONDS = 50.0
# a new read must persist *continuously* this long before we act on it -- the
# main defence against flip-flopping on a noisy opponent classification
_CONFIRM_SECONDS = 20.0
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

        # Confirmation: the new read must be desired *continuously* -- any change
        # (including a flip back to where we are) resets the timer, so a flicker
        # never accumulates enough to fire. The planner defends an emergency
        # under any strategy, so we never bypass this for a defensive blip.
        if self._candidate != desired:
            self._candidate = desired
            self._candidate_since = bot.time
        confirmed = bot.time - self._candidate_since >= _CONFIRM_SECONDS

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
        # The stable signal is the engine's counter posture for the scouted
        # opponent archetype. We deliberately do NOT fold in the emergency flag
        # or the per-fight trade verdict here: both toggle frame-to-frame and
        # would reset the confirmation timer forever. Emergency defence and
        # efficiency-based aggression are the planner's job (every step, under
        # whatever strategy is active); the selector only picks the strategy from
        # a *sustained* read of what the opponent has committed to.
        return _POSTURE_TO_STANCE.get(advice.counter.posture, Stance.STANDARD)

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
