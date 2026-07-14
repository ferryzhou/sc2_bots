# strategy_engine

The strategy docs at the repo root, turned into runnable **bot behavior**. Each
module mirrors one layer of the docs, so the "why" (docs) and the "how" (code)
stay in lockstep.

| Module          | Mirrors            | Responsibility |
|-----------------|--------------------|----------------|
| `state.py`      | —                  | `GameState`: a framework-agnostic snapshot of the game (+ `from_bot` adapter). |
| `principles.py` | `PRINCIPLES.md`    | The economy / army / tech investment tension, power timing, and the **efficiency** lens (`assess_efficiency`). |
| `strategy.py`   | `STRATEGY.md`      | Opponent classification (detection) and counter stances. |
| `rules.py`      | `RULES.md`         | Concrete, checkable rules as predicate functions. |
| `harassment.py` | harassment sections| Harass and anti-harass decisions. |
| `combat.py`     | `COMBAT.md`        | The should-engage decision (`assess_engagement`): army strength x upgrade edge x terrain/home/reinforcements/composition, with a trading-down veto. |
| `advisor.py`    | all of the above   | `StrategicAdvisor` ties everything into one `Advice` per step. |

## Design

- **Decoupled from any bot.** The logic reads a plain `GameState`, never a live
  bot object. This keeps it pure and unit-testable, and lets python-sc2,
  ares-sc2, or a test harness all feed it.
- **No hard SC2 dependency.** Nothing imports `sc2` at module load;
  `GameState.from_bot` imports it lazily only when called. So you can import and
  test the engine without StarCraft II installed.
- **Uncertainty is explicit.** Scouted `enemy_*` fields are `Optional` and
  default to `None`. The model reasons about "unknown" (e.g. classify as
  `UNKNOWN` and recommend scouting) instead of assuming zero.
- **Tunables in one place.** Thresholds match `RULES.md` and live in `rules.py`
  and the `principles`/`strategy` scorers.
- **Efficiency is first-class.** `Advice.efficiency` leads the digest: replay
  analysis (`analysis/REPLAY_FINDINGS.md`) found trade efficiency — value killed
  vs. lost, plus idle-resource waste — to be the strongest single predictor of
  the winner. Feed `value_killed` / `value_lost` (the `from_bot` adapter reads
  them from python-sc2's score) to get `should_seek_fights` / `should_avoid_fights`.

## Usage from a python-sc2 bot

```python
from strategy_engine import StrategicAdvisor, GameState

class MyBot(BotAI):
    def __init__(self):
        super().__init__()
        self.advisor = StrategicAdvisor()
        self.enemy_memory = {}  # accumulate scouting here (enemy_* keys)

    async def on_step(self, iteration):
        # ... update self.enemy_memory from your scouting ...
        advice = self.advisor.advise_bot(self, self.enemy_memory)

        if iteration % 20 == 0:
            print(advice.summary())

        # Act on the recommendations, e.g.:
        for hit in advice.rule_hits:
            # hit.rule / hit.action / hit.detail
            ...
        if advice.counter.posture == "aggressive":
            ...  # push into the greedy opponent's window
        if advice.harass.should_harass:
            ...  # send a mobile detachment
```

`advise_bot` snapshots the bot via `GameState.from_bot`. A live snapshot only
sees what is currently visible, so pass an `enemy_memory` dict your bot maintains
from scouting (keys mirror the `enemy_*` fields on `GameState`).

## Self-test / demo

Runs without SC2:

```bash
python -m strategy_engine.selftest
```

It exercises every module against representative scenarios, asserts the
recommendations, and prints an example advice digest.
