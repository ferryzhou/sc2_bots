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
2. **Economy** — per-minute workers / bases / minerals(bank/inc) / gas(bank/inc),
   with ⚠️ when our workers drop below 0.85× the enemy's.
3. **Accumulated** — total resources mined and total army value produced over
   time, plus the share of income invested into army. This separates
   *"didn't build enough army"* from *"built it and lost it"*.
4. **Army + fights** — per-minute standing-army value/supply for both sides, the
   ratio, upgrade counts, and the fight that minute inline (`BATTLE` ≥700 value
   lost, else `skirm`, with the trade ratio).
5. **Engagements** — the six costliest 30s fights with the composition going in.
6. **Peak composition + upgrades** for both sides.

## How to read it

- Trades **< 1.0** mean we lost the exchange. A string of 0.1–0.4 BATTLE trades
  with roughly even *standing* armies ⇒ composition mismatch (e.g. melee into
  ranged) — the biggest lever is what units we build and when we choose to fight.
- Army **produced ≈ even but alive-army always behind** ⇒ the army is fine, it's
  dying inefficiently. Do **not** "build more army."
- Economy even/ahead early then a **worker/base collapse right after a lost
  fight** ⇒ the economy crash is a *symptom* of the combat loss, not the cause.
- **Under-invested + short game** ⇒ died to a timing while teching/droning; fix
  is army-timing/defense, not composition.

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
