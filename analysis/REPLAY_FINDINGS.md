# Replay Findings: Do the Principles Hold Up?

An empirical check of the strategy model in [`PRINCIPLES.md`](../PRINCIPLES.md) /
[`STRATEGY.md`](../STRATEGY.md) / [`RULES.md`](../RULES.md) against real games —
**65 pro games** and **90 AI Arena bot games** — using
[`principle_analyzer.py`](principle_analyzer.py) and
[`aa_analyze.py`](aa_analyze.py).

For a focused look at the **opening building process** (what top players build,
and when, in the first two minutes — the standardized economic opening and why
it barely differs between winners and losers), see
[`OPENING_PATTERNS.md`](OPENING_PATTERNS.md)
([`opening_analysis.py`](opening_analysis.py)).

## Method

- **Data:** two samples —
  - **65 pro 1v1 games** from spawningtool.com's pro filter (Serral, Reynor,
    Clem, HeroMarine, Harstem, Lambo, Krystianer, ShoWTimE, Elazer, …), and
  - **90 AI Arena bot games** from the top 12 bots of the current standard ladder
    (Deimos, Eris, Phobos, GPT, SharpenedEdge, DominionDog, tito, VeTerran, …),
    pulled via the AI Arena API ([`aa_download.py`](aa_download.py)).
- **Extraction:** `sc2reader` tracker events (`PlayerStatsEvent`,
  `UpgradeCompleteEvent`, unit births) give per-player timelines: worker count,
  supply used vs. made, banked (floating) resources, army/economy/tech spend
  split, cumulative value killed vs. lost, income, upgrades, and base count.
- **Attribution:** for each game the winner and loser are compared on each
  principle; a `MATCH` means the winner followed the principle better, a
  `COUNTER` means the loser led on that metric yet still lost.

These are **correlational** metrics from aggregate stats, not a substitute for
watching the games — they can't see positioning or a single decisive engagement
directly, but they capture the economic and trade-efficiency footprint of one.

## Aggregate results — pro games (65)

| Principle | Verdict | Games | Share |
|-----------|---------|-------|-------|
| **Efficiency** (win trades: value killed / lost) | MATCH | 57 | **88%** |
| **Economy** (workers / income) | MATCH | 54 | **83%** |
| **Upgrades matter** | MATCH | 32 | 49% |
| **Harassment** (loser lost more workers) | MATCH | 29 | 45% |
| **Don't get supply blocked** | MATCH | 26 | 40% |
| **Expand** (more bases) | MATCH | 25 | 38% |
| Harassment — winner lost more workers but won | NOTE | 9 | 14% |
| **Economy** — loser out-econ'd but lost | COUNTER | 6 | 9% |
| **Don't float** (loser banked more) | MATCH | 5 | 8% |

(Multiple principles fire per game, so shares don't sum to 100%.)

## What the data confirms

1. **Winning trades is the single strongest predictor (88%).** In nearly every
   game the winner killed more value than they lost (killed/lost ratios like
   2.5, 4.9, 5.0 for winners vs. 0.2–0.6 for losers). This is exactly the
   **efficiency lens** — the game is won by *trading up*, not just by amassing
   units. It out-predicts raw economy.

2. **Economy is the foundation (83%).** Winners almost always had more workers
   and higher income. Economy and efficiency together account for the large
   majority of outcomes — precisely the two lenses the docs lead with.

3. **Upgrades, expansions, and supply discipline are real edges (38–49%).**
   Winners were more often better-upgraded, on more bases, and less
   supply-blocked. These are secondary but consistent — they show up as
   tiebreakers on top of economy + trades, just as the principles frame them.

4. **Harassment hits the economy leg (45%).** Losers repeatedly bled more workers
   to harass (e.g. 25, 32, 147 workers lost vs. 0 for the winner), confirming the
   harassment thesis: attacking the *investment* (workers) rather than the army
   is disproportionately effective.

## The most instructive cases: economy without conversion (the 6 COUNTERs)

In 6 games the loser had the **bigger economy** and still lost. These are not
counter-examples to the model — they are its subtlety made visible. In *every*
one of them the same pattern held:

- the winner had a far better trade ratio (1.6–2.5 vs. 0.4–0.8), **and**
- the loser floated more resources and spent more time supply-blocked.

Example — Clem vs. Elazer: Elazer led 94 workers to 73 and 8 bases to 5, but
banked ~988 avg unspent, sat supply-blocked ~108s, and traded at 0.62 while Clem
traded at 1.64. The bigger economy never made it onto the battlefield.

This is a direct empirical validation of the **economy-vs-army tension** and the
"ahead now vs. ahead later" idea: a larger economy is only "ahead later" — it
loses anyway if you **can't spend it** (floating), **stall your own production**
(supply-blocked), or **lose the decisive trade** (efficiency). Clem in particular
wins repeatedly with fewer workers by converting a smaller economy more
efficiently.

## AI Arena bots (90 games): same principles, sharper

Running the identical analysis on 90 games from the top AI Arena bots
([`aa_analyze.py`](aa_analyze.py)) gives the same ordering — only more extreme.

| Principle | Pro (65) | AI Arena bots (90) |
|-----------|:--------:|:------------------:|
| Efficiency (win trades) | 88% | **99%** |
| Economy | 83% | **98%** |
| Harassment (loser bled workers) | 45% | **94%** |
| Expand (more bases) | 38% | **78%** |
| Upgrades | 49% | 72% |
| Don't get supply-blocked | 40% | 40% |
| Economy COUNTER (out-econ'd but lost) | 9% (6) | **1% (1)** |

Four things stand out about bot play:

1. **Economy + efficiency are near-deterministic (98–99%).** Among bots, whoever
   leads on workers *and* trades essentially always wins. The pro sample has more
   noise (upsets, all-ins, comebacks); bot games are cleaner tests of the two
   core lenses — and they pass overwhelmingly.

2. **Comebacks from an economy deficit barely exist (1 COUNTER vs. 6 for pros).**
   The pro COUNTERs were Clem-style wins with a *smaller* economy converted more
   efficiently. Bots almost never pull this off — they lack the micro/efficiency
   finesse to beat a bigger economy, so an economy lead converts to a win far more
   reliably against bots than against humans. The lone bot COUNTER proves the
   rule: VeTerran beat BenBotBC despite fewer workers because BenBotBC **never
   expanded** (1 base the whole 50-minute game) and floated ~4800 unspent while
   VeTerran spread to 13 bases and traded 2.68 vs. 0.31.

3. **Harassment is far more decisive vs. bots (94% vs. 45%).** Losing bots leaked
   enormous worker counts to harass — up to **118 workers** in a single game — vs.
   near-zero for the winner. Bot worker-defense and static-defense placement are
   weak, so "attack the investment" pays off much harder against bots than against
   pros who defend harass cleanly.

4. **Bots waste resources heavily.** Losing bots sat supply-blocked far longer
   (one Zerg bot: **250s** blocked) and floated huge banks. The `don't float` /
   `don't get supply blocked` rules, minor tiebreakers among pros, are frequent
   and severe among bots.

## Takeaways for our bots

The model matches how games are actually won — and the bot sample sharpens the
priorities for a bot competing on AI Arena specifically:

1. **Efficiency first, economy second.** Our `strategy_engine` treats economy as
   the top investment while safe — correct — but the data says the decisive skill
   is *converting* it: winning trades and not letting resources sit idle. The
   `efficiency` lens (now first-class in the engine) is validated at 88% among
   pros and 99% among bots.
2. **Vs. bots, out-economy + out-expand is nearly sufficient.** Economy leads
   convert to wins 98% of the time against bots and comebacks are almost absent,
   so the `economy`/`expand` rules (`rule_build_worker`, `rule_expand`) are
   especially high-value on the AI Arena ladder.
3. **Harassment is the biggest under-exploited edge vs. bots (94%).** The
   `harassment` module's "attack the investment" framing is enormously effective
   against bot worker-defense — and conversely, defending our own workers well is
   a cheap way to avoid the most common way losing bots die.
4. **Enforce the anti-waste rules hard.** `rule_stop_floating` and
   `rule_build_supply` separate winners from losers among bots far more than among
   pros — bots routinely violate them.

## How Protoss beats a rush (12PoolBot / ZEALOCALYPSE)

Separate study: 12 games where a Protoss bot **beat** 12PoolBot (Zerg 12-pool
zergling rush) or ZEALOCALYPSE (Protoss 4-gate zealot all-in). The winning recipe
was strikingly uniform — and it is *static defense*, not army:

| | Winner's opening | Static defense up by |
|---|---|---|
| **vs 12PoolBot** | **Forge ~0:45–1:00** → 2–4+ **Photon Cannons** | **~1:31–2:00** |
| **vs ZEALOCALYPSE** | **Forge ~0:57–1:16** → 2–6 Photon Cannons + **Shield Batteries** | **~1:41–2:20** |

Key points:

1. **Forge-first cannons, not gateway army.** Several winners made *zero* combat
   units early (just probes + cannons) and still held. Cannons are static,
   cost-efficient vs. lings/zealots, and need no micro.
2. **Cannons beat batteries to the punch.** A Forge finishes ~0:50 → cannons
   ~1:20; a Shield Battery needs a Cybernetics Core (~2:15). Against a 1:30 ling
   flood, only cannons are up in time. Batteries then *supplement* (great vs.
   zealots — they heal shields).
3. **Proactive, not reactive.** The winners committed to the Forge before
   scouting could confirm the rush — textbook `INFORMATION.md` "insure against the
   unseen": buy the cheap cannon when you can't yet rule out the rush.
4. **Survive, then punish.** After holding, they transitioned to a huge economy
   (88–122 probes) and won off the rusher's dead economy.

This directly informs AthenaBot: the library (`DefensePlan`) now recommends
proactive static defense and the bot builds Forge-first cannons. It measurably
improves rush survival, though not yet to a *reliable* hold — the winners had
tighter timing (Forge ~0:57, 4–6 cannons, precise placement) than the bot
currently achieves.

## Reproduce

```bash
# install sc2reader (see principle_analyzer.py header for the mpyq workaround)

# pro replays (any .SC2Replay from spawningtool, etc.)
python analysis/principle_analyzer.py "replays/*.SC2Replay"

# AI Arena bot replays (needs an API token: https://aiarena.net/profile/token/)
AA_API_TOKEN=... python analysis/aa_download.py replays_aa
python analysis/aa_analyze.py replays_aa
```
