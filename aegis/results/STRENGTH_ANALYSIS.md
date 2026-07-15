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
`python analysis/analyze_aegis_replays.py 20260715_080232`.
