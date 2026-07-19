# Pro-game analysis: greedy Protoss macro (PvZ) vs AiurBot

Analysis of real professional Protoss macro play into the late game, compared
head-to-head against Aiur. Data pulled from spawningtool build orders (exact
in-game timings), cross-checked across two pro sources:

- **"PvZ Benchmark"** (spawningtool build 199301) — a 114-step full-game macro
  reference. Primary source below.
- **ShoWTimE vs YoungYakov** (build 202053) — a pro's opening, to corroborate.

Fetch/refresh with `python analysis/spawningtool_build.py <id>`.

## The headline: pros are MAXED by ~10–12:00; Aiur is at ~half

| Time | Pro supply | Aiur supply (best case) | Gap |
|------|:----------:|:-----------------------:|:---:|
| 5:00 | **57** | 39 | −18 |
| 7:00 | **98** | 57 | −41 |
| 8:00 | **131** | 41 (crashed) | −90 |
| 10:00 | **194** | ~98 | −96 |
| 12:00 | **~198** | ~113 | −85 |
| Max (200) | **~10–12:00** | never | — |

The pro roughly **doubles** Aiur's supply by the mid-game and maxes 4–6 minutes
earlier. This is the whole game right here: Aiur is playing a fundamentally
slower economy.

## Why — the opening (Nexus-FIRST, not tech-first)

Pro opening (both sources agree):

```
0:00 Pylon
0:24 Gateway
0:40 Assimilator (gas)
0:51 NEXUS (natural)      <- before the Cyber Core; ~1:00
1:33 Cybernetics Core
1:40 2nd gas
2:04 Stargate             <- Oracle for map control + harass
2:26 Warp Gate research   <- chrono'd
3:37 NEXUS (3rd base)
```

Aiur's opening (measured, after the eco fixes):

```
0:36 Pylon
1:10 Gateway
1:13 Assimilator
1:45 2nd Assimilator      <- 2 gas before the Nexus
2:21 Cybernetics Core     <- Cyber before the Nexus
3:09 NEXUS (natural)      <- ~2 min later than the pro
(no Stargate, no Warp Gate ever)
8:00 NEXUS (3rd base)     <- ~4.5 min later than the pro
```

Three structural gaps:

1. **Natural ~2 min late.** The pro takes the Nexus *before* the Cyber Core and
   *before* the 2nd gas — Gateway → gas → **Nexus** → Cyber. Aiur builds 2 gas +
   Cyber first, delaying the Nexus to 3:09.
2. **No Warp Gate, ever.** The pro researches it at ~2:26 (chrono'd). Warp Gate is
   what lets a Protoss produce/reinforce army fast enough to *afford* being this
   greedy. Without it Aiur's army trickles and can't cover expansions.
3. **Expansion cadence far too slow.** Pro: **3rd ~3:37, 4th ~7:52, 5th ~11:39**
   (and keeps going). Aiur: 3rd ~8:00, and it's gated behind "have 14 army supply"
   which slow production can't hit until ~8:00. The pro is on 4–5 bases while Aiur
   is on 2–3.

## The key realization: greedier economy FUNDS more army (not less)

The tension we kept hitting — "greedy economy leaves no army" — is a false
choice. The pro does **both** hyper-greedy expansion AND heavy army/tech
*simultaneously*, because more bases pay for more army:

- **Army/tech runs the whole time, off the huge economy:** Stargate/Oracle by
  2:00, Twilight + Forge 4:02, Blink 4:47, Templar Archives 6:30, **Charge 6:39,
  Storm 6:56**, Robo 7:28, 2nd Robo + Robo Bay ~8:50, continuous **High Templar**
  from 7:00 on ("hella templars for hella archons").
- **Upgrades never stall:** +1 weapons 4:51, **+2 6:58, +3 by 10:07** ("+3 by 10
  min is a benchmark"). Aiur stalls at +1/+2.

Contrast Aiur at 7:00: **57 total supply / 13 army / 44 workers on 2 bases** — it
poured everything into over-saturating two bases with probes and left the army at
13. The pro at 7:00 has ~98 supply spread across 3–4 bases *with* Stargate, Storm
tech, and continuous Templar. **Aiur is greedy on workers; the pro is greedy on
bases and army.**

## What Aiur must change (in priority order)

1. **Warp Gate research + warp-in** (`_tech`/`_train`). The keystone — nothing
   else works without army tempo. Research at ~2:30, chrono it, warp units onto
   power fields.
2. **Nexus before Cyber/2nd-gas** in the opening — natural at ~1:00, not 3:09.
   Gateway → 1 gas → Nexus → Cyber.
3. **Faster, army-independent expansion** — 3rd by ~4:00, 4th by ~8:00. The
   army-covered gate should not hold the 3rd base to 8:00 in a macro game; take it
   behind a wall/battery instead.
4. **Cap workers per base (~22) and lift army investment** — stop over-saturating
   2 bases; spread workers across more bases and convert the surplus into army +
   tech (target ~25–30% of income into army, like the pro).
5. **Don't stall upgrades** — +2 by ~7:00, +3 by ~10:00; second Forge.

## Sources

- [spawningtool — PvZ Benchmark (build 199301)](https://lotv.spawningtool.com/build/199301/)
- [spawningtool — ShoWTimE vs YoungYakov (build 202053)](https://lotv.spawningtool.com/build/202053/)
- [spawningtool — Protoss PvZ build list](https://lotv.spawningtool.com/build/pvz/)
