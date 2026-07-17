# AegisBot strength & strategy-alignment analysis

Gauntlet run `20260715_080232` @ `2e75722` — 12 headless games, AegisBot vs the
built-in AI, across all three races and two difficulty tiers (`VeryHard`, the
strongest **non-cheating** AI, and `CheatVision`). Replays analyzed with
`analysis/analyze_aegis_replays.py` (tracker-event metrics + unit/structure
counts, principle attribution shared with `principle_analyzer.py`).

## Strength: 3–9 (25%)

| Opponent | VeryHard | CheatVision | total |
|---|---|---|---|
| Zerg | 1–1 | 1–1 | **2–2** |
| Protoss | 0–2 | 1–1 | **1–3** |
| Terran | 0–2 | 0–2 | **0–4** |
| **total** | **1–5** | **2–4** | **3–9** |

The bot loses to the **non-cheating** `VeryHard` AI 1–5, so the losses are *not*
explained by CheatVision's resource cheat. This corroborates the standing verdict
in `aegis/STRATEGY.md` ("weak vs built-in AI") and localizes the weakness to
TvT/TvP. Games are long (13–20 min) and decisive — the bot reaches the mid/late
game, then loses the deciding engagement.

## The core finding: AegisBot does not execute its own strategy contract

`aegis/STRATEGY.md` names the load-bearing pillars: **siege tanks** ("Tanks are
load-bearing … pure bio went 0-6"), a Terran **static-defense line**
("siege tanks + bunkers + turrets + PF-able expansions"), a **home guard** that
stops harassment, and a **fully-upgraded** maxed army before the timing push.
The replays show the bot builds **almost none of this** in the games it loses.

### 1. Composition collapses to a marine flood — the exact 0-6 antipattern

Siege tanks actually built (whole game):

| result | games | siege tanks built |
|---|---|---|
| **losses** | 9 | 0, 0, 0, 0, 1, 1, 1, 1, and one with 0 | mostly **0–1** |
| **wins** | 3 | **7, 10, 11** |

Losing comps are 80–160 marines with ~0 tanks (e.g. vs Zerg VeryHard: 157
Marine / 25 Marauder / **0 tank**; vs Terran VeryHard: 125 Marine / **1 tank**).
The three wins are precisely the games where 7–11 tanks made it out. The strategy
says pure bio loses; the bot plays pure bio whenever it loses.

### 2. Root cause — production mix can't build the comp (principle 2)

Structures built in the 9 losses (representative):

```
Barracks 9–13   Factory 2   Starport 2–3
FactoryTechLab 0–2 (often 0)   EngineeringBay 1   Bunker 0   MissileTurret 0
```

- **9–13 barracks vs only 2 factories.** With a 20 %-tank comp target
  (`ARMY_COMP` in `bot/main.py`) but two factories, the bot physically cannot
  hit the tank ratio, so `SpawnController` falls back to marines from 10+
  barracks. In several losses **FactoryTechLab = 0**, meaning siege tanks were
  *impossible* — the comp silently degraded to pure bio.
- This is `STRATEGY.md` principle 2 verbatim ("Production capacity is the real
  macro bottleneck … match production buildings to income"), now visible on the
  build side: barracks scale with income, factories/tech-labs do not.
- Corroborating float: banks average 1.4–3.2k and peak to **15.5k** — mineral
  income the barracks can't convert into the (gas-heavy) tanks/tech the plan
  wants.

### 3. The defensive line and home guard are absent (principle 4)

- **0 bunkers and 0 missile turrets in essentially every game.** The Terran
  static defense the whole turtle thesis rests on is never constructed.
- Consequence: workers lost to harassment in the 9 losses = **46, 53, 57, 63,
  70, 73, 81, 82, 97**. The "standing home guard stops harassment" principle is
  failing outright — the economy leg is being sawn off every game
  (`harassment MATCH 12/12`).

### 4. Under-teched and the army dies in one fight (principles 1 & 6)

- Upgrades: AegisBot **5–8** vs the AI's **9–17** (`upgrades MATCH 10/12`). One
  Engineering Bay can't deliver the "fully-upgraded" army the push assumes.
- Biggest single-window army-value drop in losses: **1100–2400** — the bio ball
  evaporating in one engagement, i.e. the bucket-B/C failure the turtle was
  meant to prevent. Without a sieged tank line there is nothing to fight from,
  so principle 1 ("never lose the army in one fight") can't hold.

## What *is* aligned

- **Worker macro** is fine: AegisBot peaks 57–83 workers and often out-workers
  the AI (83 v 70, 82 v 75). The economy engine works; the spend does not.
- **Reactive ghosts vs Protoss** fire correctly (16/24/13 ghosts in TvP), and
  vikings appeared vs a Zerg air game (19). The scout-and-answer layer
  (principle 5) is the one advanced behavior that executes.
- **Expansions** trail (4 bases vs the AI's 6–8, `expand MATCH 12/12`) — a
  symptom of the same infrastructure-lag, not a separate problem.

## Why the losses happen — root cause through the principles

The symptoms above are downstream of one mechanism. Reading the per-loss
timelines (`analyze_aegis_replays.py <run_id> --timeline`) against the loss
buckets in `aegis/STRATEGY.md` and the fundamentals in `PRINCIPLES.md` /
`COMBAT.md`:

**1. The turtle succeeds at what it was built for, and fails at the next step.**
None of the 9 losses is a **bucket-A early all-in death** — every game lasts
13–20+ minutes. The bot survives to the mid/late game, which is exactly what
turtling is supposed to buy. The losses are all **bucket B/C** (mid-game remax /
late grind): the bot is *even or ahead on army-supply at 10–12 min* (e.g. TvT
`10'=51 v 38`; TvP `12'=73 v 58`, `14'=101 v 81`), then loses one engagement
(army value −1100 to −2400 in a single window) and — in 8 of 9 — **never
rebuilds** (end army value ≈ 0). This is the precise failure `STRATEGY.md`
names: "even/ahead at 8min, army evaporates by 12min, can't rebuild before the
enemy re-attacks."

**2. It wins the economy sub-game but loses the *conversion*.** By
`PRINCIPLES.md` the economy exists to be *spent into a board advantage*; by
`COMBAT.md` the #1 predictor of a won game is winning trades. AegisBot out-works
the AI and reaches midgame ahead on raw supply, but its trade ratio in losses is
**0.2–0.68** (it kills a fifth to two-thirds of the value it loses). A supply
lead in the wrong currency is not a lead — it is un-converted economy.

**3. All three combat levers that turn supply into trade value are missing.**
`COMBAT.md` "How to win battles" lists them in order of impact, and the bot
fails each:
   - **Composition (the fight is decided before it starts).** Near-pure bio,
     ~0 tanks — no splash, no siege anchor. Supply-for-supply the countered army
     loses, and bio *is* the countered side vs the AI's tank/colossus/roach
     comps. (`STRATEGY.md`: "pure bio went 0-6".)
   - **Upgrades = "efficiency bought in advance."** Bot **5–8** vs the AI's
     **9–17**, and it *stops upgrading around 12–15 min* while the opponent keeps
     going. Per `PRINCIPLES.md` §tech, a +N-behind army is structurally
     out-traded before a single command — which is why the bot loses fights it
     is *ahead on supply* for (101 v 81 supply, still wiped).
   - **Position.** The whole turtle thesis is to fight from a sieged tank line at
     a choke (`COMBAT.md` "defend": walls/chokes/static defense). With no tanks
     and **zero bunkers/turrets**, there is no line — the bio ball fights in the
     open and is caught, violating "only fight favorable engagements."

**4. The deeper cause is the three-way investment split (`PRINCIPLES.md`
central tension).** Every resource is a claim on **economy**, **army**, or
**tech/upgrades**. AegisBot pours minerals into the two *cheap* claims — workers
and marines from 10–13 barracks (a mineral-only army) — and starves the
*gas/tech* claim: **2 factories, often 0 factory tech-labs, 1 engineering bay**.
So gas piles up unspent (late mineral/gas float 500–1100+, peaks to 15k), the
army is quantity without quality, and upgrades stall. The turtle's stated win
condition is "out-macro, then push with an overwhelming, **fully-upgraded** maxed
army" — that is precisely the leg (tanks + upgrades) the build never funds.

**5. Why "ahead now" still loses (`PRINCIPLES.md` §timing).** Strength is
relative and swings over time. The bot's 10–12 min supply lead is a power
window, but it sits in TURTLE and never pushes it; meanwhile the AI converts its
gas into upgrades and a better comp and swings the relative strength. The bot's
own doctrine ("Don't tie; close — push once maxed & upgraded") never fires
because it is never actually upgraded/maxed on the right comp — so the paper lead
expires and the eventual fight is unfavorable.

**6. A parallel bleed on the economy leg.** `COMBAT.md` "defend" and the
harassment principle both call for static defense covering worker lines; with no
bunkers/turrets the bot loses **46–97 workers per loss** to harass, continuously
sawing the one leg it does win.

**In one sentence:** AegisBot loses because it never converts its economic lead
into combat value — it funds workers and mineral bio but not the tanks, tech
labs, and upgrades its own turtle win-condition depends on, so its supply lead is
out-traded and wiped in a single open-field fight it cannot rebuild from
(textbook bucket-B/C), while harassment saws the economy leg in parallel.

## Bottom line

AegisBot's macro *economy* aligns with the strategy, but its **production
composition and static defense do not**. It builds a marine flood from 10+
barracks on 2 factories with no tech labs, no bunkers, no turrets, and one
engineering bay — so it never fields the load-bearing tanks, never builds the
defensive line, under-upgrades, bleeds 50–97 workers to harass, and loses its
bio ball in one fight. The three wins are the games where tanks happened to come
out. The highest-leverage fix is production-side, in priority order:

1. **Scale factories (with tech labs) to income** so the 20 %-tank comp is
   actually buildable — the current 10-barracks/2-factory split guarantees pure
   bio. (Match `ProductionController` factory count to the comp, not just to a
   fixed opening.)
2. **Build the static-defense line** the DEFEND stance assumes — bunkers at the
   natural choke and turrets in mineral lines — to stop the 50–97-worker
   harassment bleed.
3. **Add a second engineering bay / push upgrades** so the maxed army is the
   "fully-upgraded" one the timing push is predicated on.

Method note: `VeryHard` is non-cheating and is the cleaner signal for macro
attribution; `CheatVision` inflates the opponent's economy/float numbers and is
best read only as the catastrophe-guard `STRATEGY.md` intends. Reproduce with
`python analysis/analyze_aegis_replays.py 20260715_080232` (add `--timeline`
for the per-loss army-supply trajectories and decisive-drop timing).

## Attempted fix #1 — factory-at-float (REVERTED)

Ported griffin's `_build_factories_vs_float` (add a factory when floating
≥500 gas, up to base count) to convert the gas bank into the missing tanks.
Re-ran the **same seed 7** gauntlet (run `20260716_122726`) as a controlled A/B:

| | vs Zerg | vs Protoss | vs Terran | total |
|---|---|---|---|---|
| baseline `2e75722` | 2–2 | 1–3 | 0–4 | **3–9 (25%)** |
| +factory-at-float | 1–3 | 0–4 | 0–4 | **1–11 (8%)** |

**It regressed, and the composition data shows why it never did what it
intended.** Factories did rise (2 → 4–5), but **`FactoryTechLab` stayed 0–1 in
almost every game** — and siege tanks require a factory tech-lab, so the extra
factories sat idle (or made nothing) and **tanks did not rise** (still 0–3;
only the one game that happened to get 3 factory tech-labs built 12 tanks). Net
effect: ~600–750 minerals diverted into bare factories, a thinner marine army
(the thing actually carrying the bot), gas *still* floating, and longer games
lost anyway.

Two lessons for the next attempt:
1. **Adding factories ≠ adding tanks.** A real fix must guarantee the *factory
   tech-lab* (and enough gas income), not just the factory shell — otherwise
   `ProductionController` keeps spending the minerals on marines.
2. **The gauntlet is the wrong judge for this** (`STRATEGY.md` principle 7): it
   rewards aggression and punishes tank/turtle transitions, so a tank-oriented
   change should be validated on the **ladder**. But the naked-factory waste
   above is a genuine defect independent of that caveat, so the port was
   reverted rather than shipped for ladder judging.

Reverted in the commit following `20260716_122726`; baseline behavior restored.

## Fix #2 — tank-build fix (KEPT)

Applying lesson 1 above, `_ensure_tank_production` fixes the two compounding
causes directly:
- **Guarantee the factory tech-lab** — attach a `FACTORYTECHLAB` explicitly,
  lifting/re-landing where there is add-on room (HanBot's pattern). ares' own
  `TechUp` silently failed when the factory had no add-on room, which is why
  5/9 losses never built one.
- **Make tanks actually train** — `SIEGETANK` becomes the *sole* priority-0 unit
  (marine → priority 1), and tanks are trained *directly* from idle tech-lab
  factories (gas-funded), gated on the tank supply share. The SpawnController on
  its own never had 150 spare minerals for a tank behind the 10-barracks marine
  flood.

Single-game check on a baseline 0-tank loss (terran CheatVision, IncorporealAIE_v4):
13:12 loss / 0 tanks → **26:46 Victory / 9 tanks**. Same-seed-7 gauntlet A/B
(run `20260716_235924`):

| | vs VeryHard (non-cheating) | vs CheatVision (resource-cheat) | total |
|---|---|---|---|
| baseline `2e75722` | **1–5** | 2–4 | 3–9 (25%) |
| +tank-build fix `c41f9a3` | **3–3** | 0–6 | 3–9 (25%) |

**Tanks now build** — and every win had a real tank count (6 / 8 / 14) vs the
baseline's 0–1. The headline winrate is flat, but the split moved exactly as
`STRATEGY.md` principle 7 predicts: the tank-macro turtle is **better vs the
non-cheating VeryHard AI (1–5 → 3–3)** — the closest proxy to a fair ladder
opponent — and **worse vs CheatVision (2–4 → 0–6)**, which rewards the faster
marine aggression the baseline accidentally supplied and lets its economy cheat
snowball against a slower macro game. Since the strategy is explicitly
ladder-judged (principle 7: the gauntlet is a catastrophe-guard, not the metric)
and this is not a wipeout, the fix is **kept**; final validation belongs on the
ladder.

Known remaining gaps (future work): tank production is still inconsistent under
early pressure (some CheatVision losses stay marine-floods because the emergency
gate suppresses tanks), the first tank is late (~10 min), and the static-defense
line (bunkers/turrets) and upgrade cadence from the root-cause section are not
yet addressed.
