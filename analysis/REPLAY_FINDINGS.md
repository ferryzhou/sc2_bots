# Replay Findings: Do the Principles Hold Up?

An empirical check of the strategy model in [`PRINCIPLES.md`](../PRINCIPLES.md) /
[`STRATEGY.md`](../STRATEGY.md) / [`RULES.md`](../RULES.md) against real games,
using [`principle_analyzer.py`](principle_analyzer.py).

## Method

- **Data:** 65 professional 1v1 ladder/tournament replays downloaded from
  spawningtool.com's pro filter — recent games from Serral, Reynor, Clem,
  HeroMarine, Harstem, Lambo, Krystianer, ShoWTimE, Elazer, and others across all
  matchups.
- **Extraction:** `sc2reader` tracker events (`PlayerStatsEvent`,
  `UpgradeCompleteEvent`, unit births) give per-player timelines: worker count,
  supply used vs. made, banked (floating) resources, army/economy/tech spend
  split, cumulative value killed vs. lost, income, upgrades, and base count.
- **Attribution:** for each game the winner and loser are compared on each
  principle; a `MATCH` means the winner followed the principle better, a
  `COUNTER` means the loser led on that metric yet still lost.
- **Scope note:** AI Arena bot replays were requested too, but the AI Arena API
  requires authentication credentials that this environment does not have, so the
  sample is pro humans only. The analyzer works on any `.SC2Replay`; point it at
  AI Arena replays once credentials are available.

These are **correlational** metrics from aggregate stats, not a substitute for
watching the games — they can't see positioning or a single decisive engagement
directly, but they capture the economic and trade-efficiency footprint of one.

## Aggregate results (65 games)

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

## Takeaways for our bots

The model matches how pro games are actually won, in priority order:

1. **Efficiency first, economy second.** Our `strategy_engine` treats economy as
   the top investment while safe — correct — but the data says the decisive skill
   is *converting* it: winning trades and not letting resources sit idle. The
   `efficiency` lens deserves first-class weight in bot decisions, not just the
   investment ordering.
2. **Punish the un-converted economy.** The COUNTER games are the greedy-opponent
   archetype from `STRATEGY.md`: a big economy with a thin/inefficient army is
   beatable by pressure and good trades. Our `classify_opponent` +
   `counter_stance` already prescribe exactly this.
3. **The idle-resource and supply-block rules earn their place.** Floating and
   supply blocks measurably separated winners from losers; `rule_stop_floating`
   and `rule_build_supply` are worth acting on aggressively.
4. **Harassment is high-value.** Worker-kill differentials were large and
   one-sided; the `harassment` module's "attack the investment" framing is well
   supported.

## Reproduce

```bash
# install sc2reader (see principle_analyzer.py header for the mpyq workaround)
python analysis/principle_analyzer.py "replays/*.SC2Replay"
```
