# Playing Under Incomplete Information

You never have full information about the opponent. Scouting is partial, it goes
stale the moment you look away, and the fog of war is permanent. The skill is not
eliminating uncertainty — it's making good decisions *despite* it. This document
is the model's answer to "what do we do when we can't see everything?"

Five habits, roughly in order of use: **reduce** uncertainty, **infer** from what
you can see, **insure** against what you can't, **stay flexible**, and **keep
updating**.

## 1. Reduce uncertainty — scout actively and continuously

The cheapest way to handle missing information is to have less of it missing.

- Scout on a schedule, not once. Information decays; a 3-minute-old picture is a
  guess. Re-scout before every decision that depends on the opponent.
- Spend to see when a decision hinges on it. Trading a cheap unit (or a scan, an
  overlord, a probe) for a look is usually worth it — the information is often
  worth more than the unit.
- Take and hold map control (watchtowers, forward positions). Vision is
  information you don't have to keep paying for.

## 2. Infer from partial signals — absence *is* information

You rarely see the whole base, but a glimpse plus reasoning goes a long way. The
loudest signal is often what is **missing** (see `STRATEGY.md`):

- No expansion → aggression. No army → greed. No tech building → no tech yet.
- Read timing and resources: early/heavy gas means tech or a gas unit; a delayed
  natural means an all-in or timing; extra bases mean greed.
- **Dead-reckon from the last sighting.** From what you last saw plus the time
  elapsed and their known production capacity, estimate what they *could* have
  now. Treat that estimate as the floor, not the actual.
- **Assume standard until contradicted.** Start from a prior — the most common
  play for that race/matchup/map — and update only when a signal breaks it. A
  sensible default beats reasoning from nothing.

## 3. Insure against what you can't see — assume the worst where it's cheap

Uncertainty is a risk-management problem, and the payoffs are asymmetric. Some
unknowns are merely inconvenient; a few are lethal (a hidden all-in, cloak with
no detection). The rule:

- **Weigh downside, not just likelihood.** If *not* preparing for something could
  lose you the game outright, buy the insurance even when it's unlikely — a
  bunker, a spore, an extra unit, a scan. Cheap insurance against catastrophe is
  almost always correct.
- **Be only as greedy as your information supports.** Every greedy choice (expand,
  tech, drone up) widens the window where an unseen threat punishes you. Confidence
  should scale your greed: blind → safe; well-scouted-safe → greedy.
- **Default to safe when blind.** With no fresh scouting, hold army and position,
  keep detection available, and don't over-commit into an unscouted base. Dying to
  the unknown loses instantly; playing a little safe loses slowly and is
  recoverable.

## 4. Stay flexible — keep options open until you know

Don't lock into a plan a single scout could invalidate.

- Delay committal decisions (a tech switch, an all-in, pulling workers to attack)
  until you have the information that justifies them.
- Prefer flexible, generally-useful units and reactive builds when blind; commit
  to a hard counter only once you've confirmed the need.
- Keep a fallback. A plan that only wins if a specific assumption holds is a
  gamble; prefer lines that stay okay across the opponent's likely options.

## 5. Keep updating — belief, not certainty

Treat your opponent model as a probability you refine, never a fact you know.

- Every scout, every lost unit, every building glimpsed is an update. Re-plan when
  new information contradicts an assumption instead of clinging to the old read.
- Let confidence decay with time. Re-classify the opponent when the read goes
  stale rather than acting on an old label.
- Force the information when it matters: a poke or probe that makes the opponent
  commit, defend, or reveal units turns your uncertainty into their disclosure.

## How the engine models this

`strategy_engine` is built for incomplete information, not perfect information:

- Scouted `enemy_*` fields on `GameState` are `Optional` and default to `None` —
  unknown is a first-class state, never assumed to be zero.
- `GameState.scouting_stale` decays confidence after ~45s; `rule_scout` fires
  whenever the picture is missing or stale.
- `classify_opponent`, `power_timing`, and `assess_engagement` all return
  `UNKNOWN` when the enemy data isn't there — and the `UNKNOWN` counter stance is
  literally "scout, and when unsure err toward safety."
- `recommend_investment` drops to a **safe** posture (army first, greed delayed)
  the moment pressure is detected, matching "default to safe when blind."
- **Dead-reckoning** (`information.py`): when the last scout is stale,
  `estimate_enemy` / `project_enemy` age the last sighting forward — adding the
  army their production could have made and the workers they could have added, as
  a floor with decaying confidence. The advisor runs classification, timing, and
  engagement on this projection so they **degrade gracefully instead of falling
  straight to `UNKNOWN`**, while own-side rules (including "keep scouting") still
  run on the real state — a projection never hides the need to re-scout.

## Connects to

- [`PRINCIPLES.md`](PRINCIPLES.md) — scout constantly; greed vs. safety.
- [`STRATEGY.md`](STRATEGY.md) — detection cheat-sheet and "what's missing"; the
  err-toward-safety counter procedure.
- [`RULES.md`](RULES.md) — `scout` and react-to-tech rules.
- [`strategy_engine`](strategy_engine/) — `Optional` enemy state, `scouting_stale`,
  and `UNKNOWN` verdicts throughout.
