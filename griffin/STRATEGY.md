# GriffinBot Strategy & Architecture

A principled re-architecture of GriffinBot around a **turtle → timing-push**
core, distilled from ~10 rounds of ladder-driven loss analysis (aiarena bot
#1187). This document is the design contract; `bot/main.py` implements it.

## Why turtle

The ladder loss study (29 losses, classified by *when griffin's army fell
behind*) found three buckets:

- **A. Early all-in death** (~14, mostly Protoss): a 6-10min one/two-base
  timing attack while griffin teched and expanded.
- **B. Mid-game remax** (~9, mostly Zerg): even/ahead at 8min, army
  evaporates by 12min.
- **C. Late remax/grind** (~10): even past 12min, lost the long game —
  sometimes while far ahead (DoopyBot up 3.6x, still lost).

The unifying failure across all three: **griffin loses its whole army in one
engagement, then can't rebuild before the enemy re-attacks.** Aggression
into that dynamic is a trap — you feed the army piecemeal into a stronger or
faster-rebuilding force.

A turtle strategy attacks all three at the root:
- You are *already defensive* when the all-in lands (bucket A).
- You fight from **sieged tank lines**, never A-moving the ball into a bad
  fight, so the army isn't lost in one trade (buckets B/C).
- You **macro and out-produce** while defending, then push once with an
  overwhelming, fully-upgraded, maxed army — ending the game before a remax
  can matter.

Terran is built for this: siege tanks + bunkers + turrets + PF-able
expansions make a defensive line that costs the attacker far more than it
costs us.

## Core principles (earned, with evidence)

1. **Never lose the army in one fight.** Fight defensively from siege lines;
   retreat individual low units, never feed the ball. (Buckets B/C.)
2. **Production capacity is the real macro bottleneck.** Long-game losses
   floated 3-7k unspent resources because army production capped (2
   factories → 10 tanks in 24min; Ares *win* floated 6475 minerals). Match
   production buildings to income, not just to the comp ratio.
3. **Tanks are load-bearing.** Pure bio went 0-6 vs Terran+Protoss. Tanks
   give splash (vs remax) and a defensive anchor. But *mobile* tank
   transitions get punished — keep tanks sieged on defense.
4. **Defend the economy.** A standing home guard stops harassment that
   otherwise bleeds 600-1400s of idle-worker time. Engage siege units that
   set up a contain *outside* the base immediately — a siege line only grows.
5. **Answer what you scout, don't pre-commit.** Reactive vikings on real air
   (3+ or a capital ship), turrets on any air, ghost+EMP vs Protoss
   deathballs, SCV pulls vs cannon rushes. Blind pre-commitment regressed
   (permanent vikings 1-5).
6. **Don't tie; close.** Past ~22min with a maxed army, commit unconditionally
   — a 3-3 push resolving the game beats a guaranteed half-point tie.
7. **The gauntlet (CheatVision) is a catastrophe-guard, not the metric.** It
   rewards relentless aggression the ladder doesn't; validate turtle/macro
   changes on the ladder, only use the gauntlet to catch wipeouts.

## Architecture: a phase state machine

`on_step` resolves the bot's **stance** each frame, then dispatches macro +
army control for that stance. Stances (highest priority first):

| Stance | Trigger | Behavior |
|---|---|---|
| **DEFEND** | enemy army near our bases, or all-in read, or a forming contain | Whole army + guard hold the defensive line (sieged tanks, ramp/natural choke); SCV pull if outnumbered; abort greed. |
| **TURTLE** | default | Macro hard (workers→80, expand behind defense, production-at-bank, upgrades), tech, bank into army. Army stages sieged at the natural. No attack. |
| **PUSH** | maxed & upgraded (supply ≥ PUSH_SUPPLY) or stalemate timer | Roll out behind a siege-tank leapfrog to end the game; regroup only on a real sim loss. |

Cross-cutting managers run every frame regardless of stance: orbitals/MULEs,
depot raise/lower, turrets/vikings vs air, gas throttle, comp selection.

### Composition

- Base: marine / marauder / **siege tank** / medivac (tanks load-bearing).
- vs Protoss: + **ghost/EMP** (TvP 1-5 → 5-1 when added).
- Late/floating: gas-draining tank-heavy shift **plus** enough factories to
  actually build the tanks (the missing piece — principle 2).
- Reactive: vikings on heavy air.

## What this replaces

The current `main.py` is an aggressive-by-default machine (attack at 40
supply, commit at 70) with turtle behaviors bolted on reactively. The
re-architecture **inverts the default to TURTLE** and organizes the
hard-won reactive behaviors into the DEFEND stance and the cross-cutting
managers — same proven pieces, coherent control flow.
