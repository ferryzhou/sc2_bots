# sparring: replay-derived opponents for local testing

Reproduce losses to a specific opponent **without its source code** by mimicking
its behavior with a scripted bot built from the opponent's own replay. Run your
bot against the sparring partner locally to test fixes.

## How it works

An all-in like a 4-gate zealot rush is almost entirely a **scripted build +
timing push**. Everything you need is in the replay:

1. **Extract the build** — `analysis/extract_build_order.py REPLAY <pid>` prints
   the opponent's structures, units, and upgrades with game-time and supply, and
   writes a `*.buildorder.json` spec.
2. **Script a mimic** — a small python-sc2 bot follows that build on a timeline:
   same buildings, same composition, same timing, same attack.

This reproduces the **build, composition, and timing** faithfully. It does *not*
reproduce the original bot's exact reactive micro — for a scripted all-in that's
~90% of the behavior, which is plenty to test your defenses against. For a
reactive macro opponent it's a good approximation, not a clone.

**Why not machine learning / behavior cloning?** It needs many replays, an
action-extraction pipeline, and a trained policy — heavy, fragile, and overkill
for a sparring partner. A scripted mimic is deterministic and reproducible, which
is exactly what you want when testing a fix.

## FourGateZealotBot

`four_gate_zealot_bot.py` mimics the 4-gate zealot all-in that beat `lishimin`
(extracted from `...ZEALOCALYPSE...SC2Replay`):

```
Nexus, Pylon @13, Pylon @15, 4x Gateway (1:35-2:01), NO gas, mass Zealot,
warp-in pylons pushed forward, ~18 probes then all-in. First Zealot ~3:18.
```

Tunables at the top of the class: `TARGET_PROBES`, `NUM_GATEWAYS`,
`ATTACK_AT_ZEALOTS`.

## Run

```bash
# verify the sparring bot opens with a 4-gate (vs a built-in AI)
python sparring/run.py
python sparring/run.py --bot massling     # mass-ling Zerg macro
python sparring/run.py --bot twelvepool   # 12-pool ling rush
```

All three validated headless vs the VeryHard built-in AI (fingerprints from
replay tracker events): fourgate 4 gates / 0 gas / 27 zealots (first 2:38,
won 5:42); twelvepool pool 0:39 on 14 drones, 44 lings (first 2:08);
massling pool 1:19, 5 hatcheries, 4 queens, 73 drones, 288 lings (won).

Cheater-tier sweep (Protoss Macro AI, game-time capped):

| sparring bot | CheatVision | CheatMoney | CheatInsane |
|---|---|---|---|
| fourgate | **Win** 6:09 | **Win** 5:32 | **Win** 6:40 (39 zealots) |
| twelvepool | **Win** 6:32 | Tie at cap | Tie at cap |
| massling | Loss ~12:53 | Loss ~12:57 | Tie at cap |

The scripted 4-gate all-in beats even CheatInsane — which none of the repo's
real macro bots reliably do — while the macro-style massling mimic (first ling
~6:37 behind 70 drones) loses to the cheater tiers' early aggression. This is
the cleanest demonstration yet of `STRATEGY.md` principle 7: built-in-AI
difficulty rewards relentless early aggression and punishes macro play, so the
gauntlet is a catastrophe-guard, not a ladder-strength metric. As sparring
partners: fourgate/twelvepool stress *rush defense*; massling stresses
*out-macroing a flood* — both work regardless of their own win rates here.

To reproduce *your* bot's loss, import your bot in `run.py` and put it in the
players list (there's a commented example). Requires `python-sc2` and a local
StarCraft II install.

## Declarative recreations on strategy_engine (`archetype_bot.py`)

The three mimics above are 50–175 lines of bespoke logic each (352 total).
`archetype_bot.py` recreates all three behaviors in **130 lines total**: one
generic executor driven by `strategy_engine` (`OpeningExecutor` walks the build
from the mined opening families; `recommend_investment` gates supply/economy
each frame) plus a 3-line `Spec` per archetype holding only the deliberate
principle-violations that define it — worker cutoff, attack timing, base count,
queens. Run them via `--bot fourgate2|twelvepool2|massling2`.

Fingerprints vs the hand-scripted originals (VeryHard, same caps):

| metric | fourgate | fourgate2 | twelvepool | twelvepool2 | massling | massling2 |
|---|---|---|---|---|---|---|
| key build | 4 gates, 0 gas | 4 gates, 0 gas | pool 0:39 | pool 1:07 | pool 1:19, 5 hatch | pool 1:14, 4 hatch |
| army | 27 zealots @2:38 | 34 @2:36 | 44 lings @2:08 | 40 @2:37 | 288 lings, 4 queens | 410 lings, 4 queens |
| workers | 18 | 18 | 14 | 15 | 73 | 76 |
| outcome | Win 5:42 | Win 6:19 | Tie at cap | Tie at cap | Win | Tie at cap |

Known deltas: the recreations skip ling-speed/upgrades (no gas in the mined
zerg families), and massling2 attacks off a 60-ling count (~5:22 first wave)
rather than droning to full saturation first.

The same executor also recreates a real ladder opponent from its
`bot_profiles/` dossier: `--bot onebasestalker2` mimics **OneBaseStalkerBot**
(aiarena ~1614 Elo, one-base 4-gate mass stalker). Validated headless vs
VeryHard Terran: 4 gateways / 2 assimilators / 1 cybernetics core / 1 nexus,
**23 stalkers (first 3:18) on exactly 22 probes, Victory in 6:16** — matching
(and slightly beating) the profile's observed 4/2/1/1, ~22 stalkers on 22
probes. Gas placement, army tech-gating, `distribute_workers`, and chrono were
the executor additions — a profiled ladder bot is now a 3-line Spec.

An earlier draft produced only 17 stalkers on 19 probes and lost; the replay
diagnosis (gas income 134/min with 3.3k minerals floating) traced it to three
throughput leaks, all since fixed in the executor: no `distribute_workers()`
(only the builder probe mined each geyser), the library's 85%-saturation rule
cutting probes at 19 before the spec's 22 (the spec cap now governs workers —
the archetype's economy plan is the deliberate deviation), and no chrono
boost. After the fixes gas income hit ~300/min and the float dropped to ~100.

## Greedy archetypes (`--bot greedyp|greedyt|greedyz`)

One per race: race to 200 supply, army only from excess, attack only near max
— the opposite pole from the rushes, for testing *punishing greed* (`STRATEGY.md`:
counter GREEDY_ECO with aggression) and macro-race endurance. Openings are the
mined pro expand-first families (`gate_expand` / `rax_expand` / `hatch_first`,
~100% expand-in-window across the 66-replay pro study); expansion cadence (two
in flight), production scaling (`recommend_macro`: bases/saturation/float), and
the supply gate come from the library. Zerg greed uses macro hatcheries as
larva engines; protoss chronos its own probe queue until gateways are busy.

Unpressured benchmark (vs Easy AI, supply/min from replay tracker):

| bot | 200 supply at | 8 min | 10 min | workers peak |
|---|---|---|---|---|
| greedyz | **10:00** | 121 | 200 | 79 |
| greedyp | **11:10** | 103 | 155 | 69 |
| greedyt | **12:20** | 91 | 136 | 69 |

Two optimization rounds took greedyz 11:10 → **10:00 exactly**: the inject
pass (one fresh inject per un-injected hatch, queens scaled to hatch count,
draining the whole larva burst per step; 11:10 → 10:40), then a gasless
3-hatch opening — greedyz spends zero gas, so the mined family's Extractor
was dead money at the most timing-critical moment; dropping it and baking the
3rd hatchery into the opening pulls the larva engine forward (10:40 → 10:00,
~40 supply/min sustained from 7:00).

Protoss and terran then got their signature mechanics, gated to greedy specs
so the rushes stay untouched: **warpgate** (research → morph gates → warp-in;
warpgates count as gateways everywhere production is counted) took greedyp
11:30 → 11:10 with 12 warpgates warping the zealot flood, and
**orbitals + MULEs** took greedyt 13:40 → 12:40 (8 orbitals, 25 MULEs), then
**reactors** on every second rax took it to 12:20 — built with a
lift-and-re-land fallback when the rax lacks add-on room (the silent add-on
failure behind the aegis 0-tank games), and trained via two production slots
while a reactor is attached (7 reactors, 156 marines off 17 rax, the whole
mid-curve lifted: 196 vs 179 supply at 12:00). These times are near
race-realistic pro pace — zerg is *the* fast-max race (~9-10 min pro), while
pro protoss/terran maxouts run ~11-12 min. Terran's residual gap is
income-curve shape (mule timing, CC-first openings) — diminishing returns
from here. Under VeryHard pressure the same specs survive and macro (168-189
peak) but get punished — the archetype's designed weakness.

### Built-in-AI calibration: punishment is the *build*, not the difficulty

Sweeping the greedy trio against the built-in AI settled how to read its
difficulty tiers. On the **Macro** build, no tier punishes greed — not Hard,
not CheatInsane: in every game the first real resource loss came *after* the
10-12 min maxout (greedyz maxed at 10:00 against CheatInsane untouched).
Varying CheatInsane's `ai_build` instead:

| CheatInsane build | greedyz | greedyp | greedyt |
|---|---|---|---|
| Rush | dead 8:46 (peak 69) | dead 7:33 (peak 54) | dead 6:11 (peak 38) |
| Timing | dead 9:12 | maxed 11:00, then wiped | Tie (held 97v99) |
| Macro / Air | maxed untouched, Tie/loss after | peak ~197, Tie/loss after | maxed, Tie |

**Rush** is the only true greed-punisher (first damage 5:20-5:50, all three
dead); **Timing** discriminates the races' defensive profiles; **Macro/Air**
are free macro races. So: use `CheatInsane + Rush` as the harshest
survive-while-greedy test the built-in AI offers, and read all Macro-build
gauntlet results as macro races, not punishment tests. The greedy bots' own
losses after maxing are the designed ceiling (one unupgraded mineral unit) --
they are maxout racers, not closers.

Pitting the package's own poles against each other (greedy trio vs rush trio,
9 bot-vs-bot games) caps the ranking: **our sparring rushes punish greed
1.5-3 minutes faster than anything the built-in AI offers**. Punisher ranking
by first structural damage: twelvepool2 3:40 (kills by ~4:00) > fourgate2
5:10 > CheatInsane+Rush 5:20 > onebasestalker2 6:20 > everything else never.
Greedy went 0W-3T-6L with peaks collapsed to 23-75 supply; every "tie" was a
rush that had functionally won (end states 0v140, 25v144) but could not
close -- lifted terran buildings and last-structure hunting are the rushes'
own documented ceiling, mirroring the greedy bots' no-upgrade one.

## Mimic a different opponent

1. `python analysis/extract_build_order.py THEIR_REPLAY <pid>` (use the numeric
   player id — AI Arena replays carry no player names).
2. Copy `four_gate_zealot_bot.py` and adjust the buildings / units / timings to
   the extracted spec (e.g. a mass-ling Zerg or a stalker timing).

The extractor handles AI Arena arena-client replays (via the sc2reader shim in
`analysis/principle_analyzer.py`).

## Gym report: the ladder bots vs the archetype poles

Six in-process games (the `vs_phoenix.py` pattern generalized): each repo
ladder bot vs twelvepool2 (survive the 3:40 rush?) and greedyz (punish the
10:00 maxout?).

| bot | vs twelvepool2 | vs greedyz |
|---|---|---|
| phoenix | **Win 6:08** (rush held to 20 supply) | **Win 10:28** (greed capped at 136, never maxed) |
| griffin | Win 8:59 | **Tie** -- greedyz maxed to 200, griffin turtled at 112, stalemate at cap |
| hydra | Win 8:49 | **Defeat 8:54** -- out-macroed 200 v 90 by the sparring bot |

Rush defense is solid repo-wide; punishing greed is phoenix-only. Griffin
reproduces its documented long-grind/no-close ladder weakness on demand, and
hydra loses the zerg macro mirror outright to the Spec-driven inject engine
-- the two concrete work items this gym exists to surface.
