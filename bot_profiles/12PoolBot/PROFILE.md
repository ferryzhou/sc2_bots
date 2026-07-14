# 12PoolBot

*An objective scouting profile of the AI Arena bot — its own strategy, build,
and record, independent of who it is playing.*

## Identity

| | |
|---|---|
| **Race** | Zerg |
| **Author (AI Arena user)** | 526 |
| **Bot type** | python, built on **ares-sc2** (+ python-sc2, map_analyzer, sc2_helper) |
| **AI Arena id** | 357 |
| **On the ladder since** | 2021-12-11 (a long-established, heavily-iterated bot) |
| **Approx. strength** | Division 1, Elo ~1900 — an upper-tier ladder bot |
| **Source public** | **yes** — zip is publicly downloadable, so this profile is read from its actual code |
| **Archetype** | Zerg mass-zergling (speedling) macro with a 12-pool opening |

## One-line summary

A **12-pool into mass-speedling macro** bot: it opens with an early pool, drones
*only* as much as it needs to keep zerglings flowing, floods the map with
metabolic-boost zerglings off many bases, adds +melee/Hive upgrades in long
games, harasses with overlord drops, and self-tunes its micro per enemy race
across games. Not a one-base all-in — the "12Pool" name is its opening, not its
whole plan.

## Opening build order (`zerg_builds.yml`)

```
12  Overlord (scout to enemy natural high-ground)
12  Spawning Pool          <- pool before natural/gas: early lings, safe vs early aggression
13  Drone x3
14  Extractor              <- gas purely for Zergling speed (metabolic boost)
13  Overlord
```

After this fixed opening the adaptive macro layer (`bot/components/strategy.py`)
takes over. Note **pool-first at 12 supply**: earlier than a standard
hatch-first macro Zerg, so it always has early lings to defend a rush or apply
pressure — but it is *not* an all-in; it keeps droning behind the pool.

## How it plays (from `bot/components/strategy.py` + `main.py`)

- **Army: essentially 100% Zerglings.** The default composition is pure
  Zergling. It builds Queens only when it has spare larva and is below one queen
  per hatch (for injects/defense). No banelings (the code path exists but is
  disabled), no roach/hydra.
- **Economy — "drone just enough."** It morphs a drone *only* when minerals are
  low **and** its mineral income is below ~1.2× what it could spend on lings
  **and** it's below ideal worker saturation. In effect it caps drones at the
  point where ling production stays saturated, then dumps everything into
  zerglings. This is a ling-flood with *just enough* economy behind it, not a
  greedy drone-up.
- **Zergling speed is the first and non-negotiable upgrade** (metabolic boost).
  Gas is taken for speed, then cut to zero once speed is underway (unless it
  needs gas for upgrades, drops, or a muta switch).
- **Aggressive expansion.** Once ling speed is pending it expands toward *every*
  base location on the map — it plays wide, taking many hatcheries to fuel more
  larva → more lings.
- **Upgrades / tech (long games).** With 3+ bases and 32+ workers it starts
  **Zerg melee weapons +1/+2/+3**, teching **Lair → Infestation Pit → Hive**
  alongside to unlock the higher melee upgrades. A maxed, +3-melee speedling army
  off a full map is its late-game.
- **Overlord-drop harassment ("dropperlord").** From 2 bases / 16 workers it
  makes one transport overlord and drops **zerglings into the enemy** (worker
  line / undefended pocket), with pathing that keeps the overlord out of
  anti-air danger and an emergency-unload if it's dying. A genuine second-front
  harass vector on top of the ground flood.
- **Reactive mutalisk switch — but narrow.** It switches to Mutalisks **only if
  the enemy has flying structures and no ground structures** (i.e. a pure-air /
  fully-lifted opponent). This is a niche trigger; against normal ground armies
  it stays on lings.
- **Self-optimizing micro.** It carries a **`leitwerk` optimizer (xNES natural
  evolution strategy)** that tunes its micro parameters *per enemy race*. On
  `on_start` it asks the optimizer for parameters keyed to the opponent's race;
  on `on_end` it reports back `outcome + trade-efficiency`
  (`log(value killed) − log(economy lost)`). Over many games its micro adapts to
  each race — so it tends to get *better against a given opponent pool over time*.

## Performance (last 400 ladder matches)

**Overall: 194–197 (49.6%)** — a coin-flip bot in aggregate, but the aggregate
hides a very strong matchup dependence:

| Opponent race | Record | Win % |
|---|---|---|
| **vs Terran** | 13–45 | **22%** ← its glaring weakness |
| vs Protoss | 101–102 | 50% |
| **vs Zerg** | 69–47 | **59%** |
| vs Random | 11–3 | 79% |

**Toughest opponents:** negativeZero (P) 21–85, BenBotBC (T) 5–22, Zoe (Z) 1–10,
MicroMachine (T) 0–7, Eris (Z) 0–7, XenaT (T) 0–5, MechaShark (T) 0–4.
Note how many are Terran.

**Best matchups:** One-Test (P) 57–11, PhantomTest (Z) 17–4, TyrP (P) 7–0,
Dovahkiin (Z) 8–3, XenaP/XenaZ 5–0.

## Strengths

- **Overwhelming early-to-mid map presence.** Metabolic-boost zerglings off many
  bases arrive fast and everywhere; against a bot that doesn't wall or lacks
  splash, the flood simply runs it over (its 59% vs Zerg and strong vs greedy
  Protoss).
- **Efficient economy-to-army conversion.** The "drone just enough" rule means it
  rarely over-drones or floats — it keeps larva and minerals converting into
  army continuously (the efficiency lens, [`PRINCIPLES.md`](../../PRINCIPLES.md)).
- **Multi-front pressure.** Ground flood + overlord-drop harass forces the
  opponent to defend two places at once — punishing single-tasking bots.
- **It adapts across games.** The per-race micro optimizer means beating it once
  is *not* a permanent solution — its control against your bot can improve over a
  series.
- **Upgrades compound.** +1/+2/+3 melee on a mass-ling army is a large trade-ratio
  swing that many bots neglect to keep pace with.

## Weaknesses

- **Splash damage is its hard counter — hence 22% vs Terran.** Zerglings are
  light, melee, and clump; siege tanks, hellions, widow mines, colossus, high
  templar (storm), and banelings all trade enormously against them. Terran
  mech/bio-with-tanks is the systemic answer and the record shows it.
- **One-dimensional army.** It is ~pure zergling. It has *no* answer to a
  fortified position or a splashy deathball other than "more lings," and its only
  tech switch (muta) triggers on an almost-never condition (pure-air enemy). A
  turtling, splash-heavy opponent shuts the flood down.
- **Melee into a wall does nothing.** A walled ramp/natural neutralizes the flood
  at the choke; lings can't connect and pile up under defensive fire.
- **Thin economy if the flood is held.** Because it drones only enough to feed
  lings, a held or splashed-away flood leaves it without a fallback macro
  economy — a defender who survives the mid-game can out-scale it.
- **Air pressure.** With no static anti-air beyond queens and no real air of its
  own (outside the niche muta trigger), banshees/liberators/void rays/mutas can
  harass it relatively freely.

## How to beat it (analyst notes)

1. **Get splash online before the flood.** Siege tanks + hellions (Terran),
   colossus/storm/guardian-shield (Protoss), or banelings (Zerg) are the
   structural counter. This is why Terran bots dominate it.
2. **Wall and hold — don't trade in the open.** Wall the natural, hold the choke
   with defender's advantage, and let melee lings break on static defense and
   splash. Surviving the mid-game beats it because its economy is thin.
3. **Cover two fronts.** Expect the overlord drop — keep a couple of units and/or
   a turret/spore/cannon over the worker line so the drop doesn't get free
   worker kills while your main army holds the flood.
4. **Keep pace on upgrades.** Don't let its +melee out-compound you; match armor
   upgrades so the flood's trade ratio stays bad.
5. **Then punish the thin economy.** Once the flood is spent, it has fewer
   drones than a macro opponent — take the map and out-produce it into the late
   game.

---
*Sources: 12PoolBot's public source code (ares-sc2 bot, `bot/` package +
`zerg_builds.yml`) read directly, and its last 400 AI Arena ladder matches
(record + per-race + per-opponent) via the AI Arena API. Raw stats in
[`../data/stats/12PoolBot.json`](../data/stats/12PoolBot.json). Its micro
self-tunes across games, so exact behavior drifts over time — re-check the
source (`bot_zip_updated`) and recent record periodically.*
