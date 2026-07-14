# Playing a Field of Deterministic Opponents

[`PRINCIPLES.md`](PRINCIPLES.md), [`STRATEGY.md`](STRATEGY.md), and
[`RULES.md`](RULES.md) describe how to play *StarCraft* against a general,
adapting opponent. On the AI Arena ladder that model is missing one structural
fact that dominates results: **our opponents are computer programs, and most of
them play very close to the same build every single game.** This document adds
the principles that follow from that fact. It is grounded in GriffinBot's 92
ladder games ([`results/LADDER_ANALYSIS.md`](results/LADDER_ANALYSIS.md) and
[`bot_profiles/data/griffin_matches.json`](bot_profiles/data/griffin_matches.json))
and the opponent build orders behind them. For objective, standalone profiles of
the ladder's top bots, see [`bot_profiles/`](bot_profiles/).

## The core observation: matchups are (nearly) binary

Across 92 games, repeat opponents were almost never split — we either beat a bot
every time or lost to it every time:

| We beat every time | We lose every time |
|---|---|
| 27turtles 2–0, GenesisLotus 2–0, Visenya 2–0, JackBot2.0 2–0 | Princess‑Mika 0–3, WorkingAsIntended 0–3, KoB 0–2, Hestia 0–2, DasyBot 0–2, StarK234 0–2, oberon 0–2, AxeFighter 0–2, SiriusBot 0–2, Thssprtssbt 0–2 |

This is exactly the pattern the earlier
[`results/LADDER_ANALYSIS.md`](results/LADDER_ANALYSIS.md) found for PhoenixBot,
now reconfirmed for GriffinBot on a fresh 92‑game sample. The reason is simple:
a deterministic bot runs the same build into the same fixed opening, so the same
thing happens every time. **We do not have a "play slightly better" problem —
we have a set of specific builds that hard‑counter our fixed opening.**

The strategic consequences are large:

1. **Beating one instance beats all future instances.** Every game is a
   *known, repeatable puzzle*. Effort spent solving one loss is not spent on a
   coin‑flip — it converts a whole column of future losses into wins.
2. **A pre‑game opponent model can substitute for in‑game scouting.** Against a
   human, you must scout because they adapt. Against a bot that opens the same
   way every game, the *strongest scouting information you have is last game's
   replay.* Store a per‑opponent build prior and load it before the game starts.
3. **The distribution of opponents is fixed and knowable.** We are not playing
   "Protoss" — we are playing *Klakinn's zealot flood* and *KoB's hydra macro*.
   Prepare for the actual ladder field, not the abstract matchup.

## Principle A — Opponent priors beat blind scouting

Scouting (PRINCIPLES #5) still matters — bots do get updated, and some are
non‑deterministic — but against this field the ordering flips:

- **Load the prior first.** Before (or in the first seconds of) a game, key on
  the opponent's name and recall their known build. AI Arena passes the opponent
  name to the bot; a stored `{opponent → build, timing, counter}` table is the
  single highest‑value piece of information available.
- **Scout to *confirm or refute* the prior, not to discover from scratch.** If
  the prior says "Klakinn = 6‑gate zealot all‑in at 8:00," the early scout's job
  is only to check the build hasn't changed — and to trigger the prepared
  counter earlier if confirmed.
- **Update the prior after every game.** A lost replay is a bug report. The
  objective bot profiles in [`bot_profiles/`](bot_profiles/) are that kind of
  table in human‑readable form; the same per‑opponent data can drive an in‑bot
  lookup.
- **When there is no prior (new opponent), fall back to STRATEGY.md** — classify
  from live scouting and err toward safety.

## Principle B — Opening safety is a first‑class decision

The clearest lesson from the data: **GriffinBot plays one fixed opening
regardless of the opponent** — ~36 supply, ~25 workers, ~400 army value at the
4‑minute mark in essentially every game. That opening is *safe against nothing
in particular and greedy against nothing in particular*, and it decides most of
our losses before any micro happens:

- Against every **all‑in / early‑timing** opponent it is too greedy — the flood
  arrives (zealots, mass reaper, mass marauder, ling flood) and wipes our army
  at 7–9 min before tanks are out. This is a **build‑order loss**: no amount of
  micro saves an opening that can't be safe in time.
- Against every **greedy macro** opponent it is not greedy enough — they reach
  150+ supply and 75+ workers while we sit at ~100/50, then out‑remax us.

So opening choice is not a fixed constant to tune once; it is a **decision that
should flex to the prior**:

- **Default to an all‑in‑safe opening** (wall the natural, early bunker, first
  tank/­siege fast) whenever the opponent is unknown or known to be aggressive.
  Dying to an unscouted all‑in loses *instantly*; being slightly slower on
  economy loses *slowly and recoverably* (STRATEGY.md #4).
- **Flex greedier only when the prior (or live scouting) clears it** — against a
  known turtle, greedy‑macro, or passive/broken opponent, take the fast third
  and out‑economy them.
- **The opening must be able to reach "safe" by the earliest ladder timing** —
  which the data puts at **~7–8 minutes** (Klakinn 8:00, oberon/zig‑reapers 8:00,
  ZEALOCALYPSE 9:30, Crawler's ling flood even earlier). Wall + bunker + one
  sieged tank by ~7:00 is the survival bar.

## Principle C — Hold, don't trade, against aggression

Every one of our all‑in losses shares one mechanism, already named in
[`results/LADDER_ANALYSIS.md`](results/LADDER_ANALYSIS.md) as **the army wipe**:
our supply crashes to ~0 mid‑game and never recovers, because we commit the
whole army into a bigger one instead of holding. The fix is a direct application
of *defender's advantage* (RULES 7 / 9a) plus the efficiency lens:

- Against a scouted all‑in, **do not move out and do not take the open‑field
  fight.** Sit on the wall with tanks sieged and let the aggressor break itself
  on static defense. Our 1–1 vs **Crawler** (120‑zergling flood) is the proof:
  the game we *held* the wall, its army collapsed to almost nothing by 12 min
  and we won; the game we traded, we died.
- **Winning the trade, not amassing units, is what wins** (REPLAY_FINDINGS:
  efficiency predicts 88% of pro and 99% of bot games). A held all‑in is the
  most efficient trade in the game — the attacker's whole economy is already
  spent.

## Principle D — Harassment is our biggest un‑taken edge vs. the macro field

The other loss cluster is greedy‑macro Zerg/Terran simply out‑economying us.
[`analysis/REPLAY_FINDINGS.md`](analysis/REPLAY_FINDINGS.md) found harassment
decides **94% of bot games** — losing bots bleed enormous worker counts (up to
118 in one game) because bot worker‑defense is weak. We mostly don't exploit
this. Against the over‑drone / over‑expand window (Siriusly droned to 99 workers
with no army; Thssprtssbt took 4 bases):

- **Punish the greedy window** with a bio+tank timing or hellion/medivac worker
  harass *before* they remax. Every dead drone compounds as lost mining.
- If we can't punish it and let the game go even into the late game, the Zerg
  remax beats us — so against macro we must be *ahead by ~10 min*, not floating
  and passive.

## The ladder field at a glance

Our 92‑game opponent pool clusters into a handful of recurring builds. Prepare
for these, in priority order (most losses first):

| Cluster | Example opponents | What beats us | Our counter |
|---|---|---|---|
| **Protoss gateway all‑in** | Klakinn, ZEALOCALYPSE, OneBaseStalkerBot, protossinger, PerilousProtoss | Zealot/stalker flood at 8 min, army wipe | Wall + bunker + sieged tank, **hold, don't trade** |
| **Zerg drone macro** | KoB, GLM_Bot, SiriusBot, Persephone, muravev, QueenBot | Out‑econ + faster remax | Punish the drone window; be ahead by 10 min |
| **Terran macro (bio/mech)** | Hestia, StarK234, WorkingAsIntended, muravevTerran, AxeFighter | Out‑macro the near‑mirror | Win upgrades + tank count; no floating |
| **Zerg ling flood** | Crawler, Princess‑Mika, Lissy, MY_SCRIPTING_SON | 40–120 lings before our splash | Wall + splash (tank/hellion), hold |
| **Terran one‑base all‑in** | oberon (marauder), zig‑reapers (reaper) | 20+ units at 8 min, army wipe | Cheese defense: wall/bunker/tank, hold |
| **Protoss air / cannon / robo** | Asteria (tempest), sharpy (void), DasyBot (immortal), Apidae (cannon) | Un‑scouted tech we can't answer | Scout the tech building, react early (turrets/vikings/focus) |
| **Passive / broken** | JackBot2.0, BioBotGod, Visenya, CyraxxDKAkron | — (they stall) | Macro straight up, free win |

The specific opponents above come from GriffinBot's own match history
([`bot_profiles/data/griffin_matches.json`](bot_profiles/data/griffin_matches.json)).
For objective build orders, records, strengths/weaknesses, and counters on the
ladder's top bots, see the profiles in [`bot_profiles/`](bot_profiles/).

## How this connects back to the core model

None of this replaces the economy‑vs‑army tension in
[`PRINCIPLES.md`](PRINCIPLES.md) — it *specializes* it for a known, repeating
field:

- **Opening safety** is the greed‑vs‑safety trade‑off (STRATEGY.md), resolved
  *per opponent* from a prior instead of blindly.
- **Hold, don't trade** is *defender's advantage* + the *efficiency lens*
  applied to the one loss mechanism that actually kills us.
- **Punish the window** is the *timing* section — every fixed build opens a
  fixed window, and a deterministic opponent opens the *same* window every game,
  so we can pre‑build the punish.

The meta‑principle: **against deterministic opponents, preparation compounds like
upgrades.** Each solved matchup is a permanent win, not a one‑off.
