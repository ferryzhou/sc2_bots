---
name: loss-investigation
description: >-
  Investigate why an SC2 bot lost (or underperformed in) a game from its
  replay. Generates a full markdown report with an auto root-cause verdict
  (macro-broke vs combat-loss vs under-invested/greed), head-to-head economy,
  accumulated resources & army value, and a minute-level army timeline with
  each fight inline. Use when asked to analyze a loss, dig into replays, find
  the root cause of a defeat, or produce an investigation report.
---

# Loss investigation

Turn a replay into a root-cause report. The discipline: **first ask "did
production run and did the economy look good?"** — only if macro was fine do you
attribute the loss to combat. The tooling encodes exactly that order.

## Keep asking "why" until you hit the root cause

The verdict and tables surface **red flags** (a bad trade, a gas pile, a worker
crash, an army deficit). A red flag is a **symptom, not a cause**. Do not stop at
the first one — chain "why?" through the metrics *and the bot's code* until you
reach something you can change in the source. Every "because" must be backed by a
number from the report or a line in the code, not a guess.

Worked example (Aiur vs Zerg):

1. We lost — *why?* Lost the decisive fight at trade 0.09.
2. Why 0.09? Went in at **0.71 army value** with an all-Zealot (melee) army vs a
   ranged Roach/Hydra ball. → but 0.71 is a losing attack regardless, so keep going.
3. Why only 0.71 army value when the economy was even? Because **~1150 gas sat
   unspent** at the fight (bank climbs monotonically to 6241) — army value ≈ the
   unspent resources. Conversion failure, not an economy failure.
4. Why is the gas unspent? The army is all Zealots, which cost **0 gas**.
5. Why all Zealots? `_train`'s gateway logic picks units from race + unit counts
   and **never reads `self.vespene`** — no feedback path from "floating gas" to
   "build gas units". ← **root cause: composition decision is blind to the bank**
   (violates Principle 3, "spend your resources — don't float").

Only step 5 is fixable in code; steps 1–4 are symptoms. Stopping at step 2
("bad composition") would have produced a weaker fix than stopping at step 5
("wire composition to the bank"). **Report the whole chain in the write-up**, not
just the surface symptom — the fix lives at the bottom of it.

Rule of thumb: keep asking why until the answer is *a specific function/line or a
missing rule*. If your "root cause" is still a behavior ("it makes bad units"),
you are not done — ask why the code produces that behavior.

## One command

```
/root/venv312/bin/python analysis/investigate.py <replay> [more replays ...] \
    [--our N] [--out FILE]
```

- `--our N` — our player id (default `1`; vs-Computer replays put the bot at pid 1).
- `--out FILE` — write markdown to a file (e.g. `analysis/reports/<name>.md`);
  omit to print. A batch writes each report concatenated and prints a verdict
  line per replay.
- Run with the **py3.12 venv** (`/root/venv312/bin/python`) — it has sc2reader.
  Suppress the shim's stderr with `2>/dev/null` if noisy.

Example (the Aiur Hard losses):

```
/root/venv312/bin/python analysis/investigate.py \
  results/build_replays/aiur_hard_zerg.SC2Replay \
  results/build_replays/aiur_hard_terran.SC2Replay \
  results/build_replays/aiur_hard_protoss.SC2Replay \
  --out analysis/reports/aiur_hard_losses.md
```

## What the report contains

1. **Verdict** — auto-classified root cause + the four numbers behind it
   (peak workers & floating; army value produced ratio & investment share;
   overall trade; the first decisive fight). Classes:
   - **COMBAT LOSS** — built enough army (produced ≥0.85× enemy) but lost it at a
     bad trade (<0.7). Composition/engagement problem, *not* production.
   - **UNDER-INVESTED / GREED** — produced <0.7× the enemy's army and put a
     smaller share of income into army; caught before teching up (often by an
     early timing in a short game).
   - **MACRO BROKE** — floating cash or, in a long game, a stunted worker count;
     economy/production failed before combat mattered.
2. **Deficits & why** — a scan that flags *every* sustained deficit (workers,
   bases, resources mined, gas, army produced, army on the field) and
   cross-references the metrics to name the likely cause of each (e.g. "even
   workers but out-mined → less gas / worse saturation", "under-invested 21% vs
   31%", "FEEDING: lost 93% of everything built"). Start here after the verdict.
3. **Economy** — per-minute workers / bases / minerals(bank/inc) / gas(bank/inc)
   plus three us/enemy ratios: **workers**, **mining speed** (income rate), and
   **total mined**. Every ratio flags ⚠️ below 0.85, and bases flag when behind —
   so an income deficit shows up before the worker count does.
4. **Accumulated** — total resources mined and total army value produced over
   time, with a **made ratio** (army produced, us/enemy) and the share of income
   invested into army. Separates *"didn't build enough army"* from *"built it and
   lost it"*.
5. **Army + fights** — per-minute standing-army value/supply for both sides, the
   **val ratio** and **sup ratio** (both flag ⚠️ below 0.85), upgrade counts, and
   the fight that minute inline (`BATTLE` ≥700 value lost, else `skirm`, trade).
6. **Engagements** — the six costliest 30s fights with the composition going in.
7. **Peak composition + upgrades** for both sides.

## How to read it

- Trades **< 1.0** mean we lost the exchange. A string of 0.1–0.4 BATTLE trades
  with roughly even *standing* armies ⇒ composition mismatch (e.g. melee into
  ranged) — the biggest lever is what units we build and when we choose to fight.
- Economy even/ahead early then a **worker/base collapse right after a lost
  fight** ⇒ the economy crash is a *symptom* of the combat loss, not the cause.
- **Under-invested + short game** ⇒ died to a timing while teching/droning; fix
  is army-timing/defense, not composition.

### Debugging a lost battle: check army value FIRST

When a fight was lost, the first question is always **"what army value did each side
bring into it?"** — not micro, not composition. The report's verdict line and the
`## Army value + the fight each minute` table give it: the val/sup ratio *going in*.

- **Went in below ~0.85 value** ⇒ it was lost before it started — a *quantity*
  problem (too little army, or the wrong timing to fight). Do not chase micro;
  ask why the army was small there (under-invested? fed the last fight? behind on
  economy?). A fight at 0.5 value is unwinnable regardless of how it's executed.
- **Went in at ~parity (≥0.9) and still traded badly (<0.7)** ⇒ *now* it's a
  quality problem: composition mismatch (melee into ranged, no splash vs a flood,
  no anti-air vs air), an upgrade deficit, or bad positioning/engagement.

Only after value is ruled even do composition and micro become the answer. Skipping
this step is how you "fix" micro on a fight that was a 2:1 value loss.

### The feeding signature (the trap this skill exists to catch)

Always compare **army value *produced* (cumulative)** against **army value *alive*
(the per-minute standing-army ratio)**. They tell different stories:

- **Produced ≈ even but alive-army always behind** ⇒ the army is fine, it's dying
  inefficiently. Do **not** "build more army."
- **Produced FAR ahead (e.g. 1.5–1.8×) but the alive ratio sits below 1.0 almost
  the whole game** ⇒ **feeding.** The bot out-builds the enemy and still never has
  a field-army lead because it throws every batch into a losing fight before the
  next is built. Quantify it: `lost / produced`. Losing **>85%** of everything you
  produced (while the enemy loses ~65–70%) is the smoking gun. The fix is *not*
  more production or better units — it's **engagement discipline** (only commit at
  a real advantage; hold and let production accumulate into a standing lead).
- A verdict of "built enough army (ratio 1.7) but traded at 0.4" is this exact
  case. When the user says "the army ratio is below 1.0 the whole time," they mean
  *alive* ratio — reconcile it against *produced*, and if produced ≫ alive, it's
  feeding, full stop.

## From diagnosis to fix

Investigation only pays off if the fix lands in the right place and is verified.

- **Fix the strategy library first, keep bot code thin.** The *decision* (when to
  expand, what to build, whether to commit) belongs in `strategy_engine`; the bot
  should be a thin translator of the advice. Before editing bot logic, ask "should
  this rule live in the library so every bot gets it?" A hard-coded threshold in
  the bot that overrides a library verdict is a common root cause in itself (e.g.
  an attack gate that ignores `assess_engagement` and attacks at raw supply).
- **One fix reveals the next.** Root causes are layered — gas/composition →
  expansion → tech transition → engagement. After a fix, re-run and re-investigate;
  expect the verdict to change and a new bottleneck to surface. That's progress,
  not failure.
- **Verify across several games, not one.** Variance is high: the same bot dies to
  an 8-min timing in one game and macros to 30 min in the next. Run 3+ and read the
  *pattern*. To test a late-game change (tech transition, engagement) you need a
  game that *reaches* the late game — short timing deaths won't exercise it.
- **Confirm the mechanism actually triggered.** Intent ≠ effect. After a fix, check
  the replay's unit/structure births to prove the change happened — e.g. count
  Stargates built and Void Rays trained, not just "I added the code." A building
  that gets built but sits idle (unit unaffordable) is a real and common failure.
  Quick check:
  ```python
  import sys; sys.path.insert(0, "analysis"); sys.argv = ["x"]
  import loss_analysis as la
  from collections import Counter
  r, units, stats, upg = la.load("results/build_replays/<name>.SC2Replay")
  print(Counter(n for owner, n, born, died in units.values() if owner == 1))
  ```

## Underlying pieces (if you need finer detail)

- `analysis/investigate.py` — the driver above (imports `loss_analysis`).
- `analysis/loss_analysis.py` — same metrics as a text dump for one replay:
  `python analysis/loss_analysis.py <replay> [our_pid]`.
- `analysis/game_report.py` — production/economy triage for a single player
  (structures placed, supply blocks, floating): `python analysis/game_report.py
  <replay> [player_or_race]`.

## Notes / gotchas

- sc2reader **load_level=3** (tracker events) — level 4 crashes on vs-AI replays.
- vs-Computer replays carry no player result; result is inferred from final army
  supply (the loser's collapses to ~0).
- Costs/army-value use a static unit cost table in `loss_analysis.py`; add units
  there if a matchup shows `0`-value unknowns.
- After diagnosing, write the narrative report as `analysis/<BOT>_LOSS_ANALYSIS.md`
  (see `analysis/AIUR_LOSS_ANALYSIS.md` for the template: TL;DR, evidence table,
  root causes, prioritized solutions).
