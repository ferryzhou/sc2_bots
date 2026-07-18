# opponent_intel — pick a strategy from who you're playing

Turns the ladder's opponent id into a **known profile** and a **counter-strategy**,
so a bot can load a pre-game prior instead of playing blind (see
[`../OPPONENTS.md`](../OPPONENTS.md), *"load the prior first"*). It joins the
scouting work in [`../bot_profiles/`](../bot_profiles/) to the adaptive bots.

## What the game actually gives you (the important part)

**In-game you only get the opponent's `game_display_id` — a UUID — never the
name.** AI Arena launches your bot with `--OpponentId <uuid>`, e.g.

```
MyBot --OpponentId 4a491758-76ff-40de-996c-018d49b6237f   # this is 12PoolBot
```

Our ladder wrapper stores it on `self.opponent_id` (see `griffin/ladder.py`).
So to act on *who* the opponent is, you need a **UUID → name/strategy mapping**.

**Is the UUID→name mapping constant?** Yes, for a bot's lifetime. `game_display_id`
is a stable identifier assigned once when the bot is created and stored by AI
Arena — it does not change between matches or seasons. That stability is the
whole reason the platform lets bots "save this ID in your data folder" to learn
per-opponent (per the [AI Arena wiki](https://aiarena.net/wiki/bot-development/)).
The one caveat: if an author **deletes a bot and re-uploads it as a new bot**,
the new entry gets a new UUID (and shows as a new name), so the mapping should be
**refreshed periodically** to pick up new/renamed bots — but existing entries
never silently change meaning.

Note: our **local** harness (`harness/versus.py`) passes the opponent's *name*
as `--OpponentId` instead of the UUID. The resolver accepts **either** form, so
the same code path works on the ladder and in local testing.

## Files

| File | Purpose |
|---|---|
| `opponent_map.json` | Generated map: `game_display_id` (UUID) **and** lowercased name → `{name, race, style, opp_style}` for every profiled bot. |
| `classify.py` | `STYLE string → opp_style` (8 buckets) and `opp_style →` counter (HydraBot strategy + race-agnostic stance), grounded in `STRATEGY.md`. |
| `intel.py` | Runtime, no-network: `resolve(id)` and `recommend_for(id) → Recommendation`. Loads `opponent_map.json`. |
| `build_map.py` | Regenerate the map from the AI Arena API + `bot_profiles/`. |
| `verify.py` | Prove resolution + strategy selection (by UUID or name); `--all` self-test. |

## Using it in a bot

```python
from opponent_intel import recommend_for

rec = recommend_for(self.opponent_id)      # UUID (ladder) or name (local); never raises
logger.info(rec.summary())
initial_strategy = rec.hydra_strategy      # HydraBot: one of its 5 strategies
stance           = rec.stance              # any bot: hold_defensive / out_expand / anti_air / ...
```

An unknown or `None` id yields a safe default (`opp_style="unknown"` →
`MacroRoachHydra` / `standard_safe`), so a new opponent never breaks anything.

### HydraBot integration (live)

`HydraBot.on_start` calls `_apply_opponent_intel`: it resolves `self.opponent_id`
and sets the **starting** strategy (unless a human forced one with `--strategy`).
The mid-game `StrategySelector` still refines it by live scouting — the prior
just gives a better opening than a blind default. Example decisions:

| Opponent | Their style | HydraBot opens |
|---|---|---|
| ZEALOCALYPSE (zealot flood) | `allin` | **RoachTiming** — fast roaches to hold, then counter |
| kas (over-drone macro) | `macro_greedy` | **LingFlood** — punish the thin-army window |
| ArgoBot (skytoss/tempest) | `air_tech` | **MacroRoachHydra** — hydralisk anti-air |
| norman (broken) | `broken` | **GreedyHydraLurker** — be greedy, free win |
| Eris (roach/ling macro) | `macro_standard` | **MacroRoachHydra** — win on execution |
| unknown / new bot | `unknown` | **MacroRoachHydra** — safe default |

## Verify

```bash
python opponent_intel/verify.py 12PoolBot                                 # by name
python opponent_intel/verify.py 4a491758-76ff-40de-996c-018d49b6237f      # by UUID (== 12PoolBot)
python opponent_intel/verify.py --all                                     # self-test all known bots
```

The self-test asserts that a bot's **UUID and name resolve to the same
strategy** and that unknown ids fall back safely.

## Refresh (after new/updated bots or new profiles)

```bash
AA_API_TOKEN=... python opponent_intel/build_map.py
```

Re-fetches each profiled bot's `game_display_id` and re-classifies. Coverage is
the set of bots in `bot_profiles/` (currently the top ~96 by Elo); opponents
outside that set resolve to the safe `unknown` default until profiled.
