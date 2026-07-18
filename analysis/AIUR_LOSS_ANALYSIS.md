# AiurBot loss analysis: why it caps out at Hard

**TL;DR — AiurBot's macro is fine; it loses the *battles*.** It mass-produces
**Zealots (melee)** and feeds them into every opponent's **ranged** army, trading
at ~**0.35** (kills 35% of the value it loses) in all three Hard losses. It is
behind on army value from ~1–3:00 and never recovers, has **no splash** and a
**gas-starved** economy that can't afford the ranged/tech army it actually wants,
and lets opponents out-upgrade it to 3/3 while it stalls at 2/2.

## Strength placement

| Difficulty | vZ | vT | vP | Verdict |
|-----------|----|----|----|---------|
| Medium    | ✅ | ✅ | ✅ | wins |
| Hard      | ❌ | ❌ | ❌ | **ceiling** |
| VeryHard  | ❌ | ❌ | ❌ | loses |

Macro triage (`game_report.py`): economy is healthy — ~48 workers, **0 mineral
floating** (no float bug), full-length games (19.5 min vs Hard Zerg). The
problem is downstream of macro.

## Method

- `analysis/game_report.py` — production/economy timeline + red-flag scan.
- `analysis/loss_analysis.py` — reconstructs army value/supply, composition, and
  upgrades over time for both players from unit births/deaths; finds the decisive
  engagements and the state going into each; reports trade ratios.

## The evidence (Hard losses)

| Loss | Aiur army (peak) | Enemy army | Overall trade | Behind since |
|------|------------------|-----------|---------------|--------------|
| vs Zerg   | 18–21 **Zealot**, 2 Stalker, 1 Immortal | Roach/Hydra/Ravager + Infestor | **0.37** (lost 10225, killed 3750) | 1:00 |
| vs Terran | 11 **Zealot**, 1 Stalker | Marine/Marauder (stim) | **0.36** (lost 3850, killed 1375) | 3:00 |
| vs Protoss| 6 **Zealot**, 1 Stalker | Adept/Stalker/Sentry (blink) | **0.33** (lost 1350, killed 450) | 3:00 |

Representative fights (Hard Zerg): `11:00` we lost 8 Zealots for 3 Zerglings
(**trade 0.09**); `17:30` we lost 10 Zealots for 2 Zerglings + 1 Roach
(**0.15**). Melee walking into a ranged, defended army.

Army-value curve (Hard Zerg) — Aiur is *below* the enemy the entire game:

```
 6:00   575 vs 1375   (0.4)
12:00  2900 vs 3950   (0.7)   <- our best
19:00  2150 vs 5425   (0.4)
```

## Root causes

1. **Zealot-heavy composition into ranged armies.** `aiur/main.py:_train` builds
   zealot-heavy vs Zerg *by design* (`zealots < 2*stalkers`), and vs Terran/
   Protoss it *wants* stalkers but can't afford them (see #2) so it falls through
   to Zealots. Melee units get kited and die before dealing damage — the direct
   cause of the 0.33–0.37 trades.

2. **Gas-starved economy → can't afford the army it wants.** Only **2
   assimilators until ~7:30**; gas income ~300–490/min while Robo + Twilight drain
   it. Stalker (50 gas), Immortal (100), Colossus (200) are all gas — starved of
   it, the gateways default to Zealots. Gas is the hidden constraint behind the
   melee army.

3. **No splash, thin robotics.** One Robotics Facility; Colossus only via a bay
   that is built **vs Zerg only**. In the fights Aiur had 0–1 Immortal and **no
   Colossus / no Storm**. Against mass Roach/Hydra or Marine/Marauder, splash is
   the hard counter and Aiur simply doesn't have it.

4. **Upgrade deficit.** Aiur *leads* early (1 vs 0 at 6:00) then **stalls at
   +2/+2** while the Zerg reaches **3/3 + all tech upgrades** (10 vs our 5 by
   19:00). Upgrades compound every fight; a 3/3-vs-2/2 gap alone swings trades.

5. **Commits while behind.** The engagement logic attacks at supply ~35 / at max
   even when army value is ~0.5 of the enemy's *and* the composition is
   unfavorable (melee vs ranged), feeding army into un-winnable fights instead of
   defending and teching to parity.

## Detailed solutions (priority order)

### S1 — Fix the composition: ranged + splash core, Zealots as tanks only
`aiur/main.py:_train`. Stop making Zealots the bulk.
- vs **Zerg**: Zealots (charge) are a *front line*, not the army. Core = Immortal
  (anti-Roach) + Colossus / High-Templar Storm (splash vs Hydra/Ling). Cap
  Zealots at ~1:1 with Stalkers and gate them behind having splash online.
- vs **Terran/Protoss**: Stalker/Adept + Immortal core; Zealots minimal.
- Make Colossus available for **all races** once floating gas (not Zerg-only).
- Expected impact: turns 0.1–0.5 trades into ≥1.0 — the single biggest lever.

### S2 — More gas, earlier
`aiur/main.py` economy/tech. Take the **2nd gas per base sooner** and a 3rd/4th
base's gas promptly; target 2 gas per base by the time Cyber finishes. Without
gas the composition fix in S1 can't execute (you can't build what you can't
afford). Expected impact: unlocks the ranged/splash army.

### S3 — Add a splash/tech path for every matchup
Robotics Bay → 2–3 Colossus, and/or Templar Archive → High Templar (Psionic
Storm) / Archons, regardless of enemy race. Scale a **2nd–3rd Robotics Facility**
with gas (this doubles as the gas sink). Expected impact: a hard answer to
mass-ranged and mass-light.

### S4 — Don't stall upgrades
Keep both forge lines running to **3/3**, build a **2nd Forge** to parallelize
weapons+armor, and continue past level 2 (currently it stops). Add Blink/Storm
where relevant. Expected impact: closes the compounding upgrade gap.

### S5 — Engage only at parity + right composition
`strategy_engine.combat.assess_engagement` / the `_army` attack gate: veto the
attack when our army *value* < ~1.0× the enemy's, or when we're melee-heavy vs a
ranged army with no splash. Defend on the ramp and tech to splash first, then
commit. Expected impact: stops feeding; converts a lead into a won fight.

**Order to implement:** S2 (gas) and S1 (composition) together — they're
coupled — then S3 (splash), S4 (upgrades), S5 (engagement discipline). S1+S2
alone should move the trade ratio from ~0.35 toward parity and likely lift the
ceiling past Hard.

## Reproduce

```
python analysis/game_report.py   results/build_replays/aiur_hard_zerg.SC2Replay Protoss
python analysis/loss_analysis.py results/build_replays/aiur_hard_zerg.SC2Replay 1
```
