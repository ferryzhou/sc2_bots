# PhoenixBot Ladder Analysis — 2026 Season 1 (through ~game 79)

Data: 164 completed season games (aggregate API) + s2protocol trajectory
profiling of ~50 replays (`harness/analyze_replays.py`).

## Headline record
- **50W – 27L – 2T (65%)**, Elo ~1618, division 3/4, **0 crashes ever**.

## Insight 1 — matchups are nearly BINARY (losses are deterministic counters)
Every repeat opponent is either all-wins or all-losses:

| all-loss | all-win |
|---|---|
| Klakinn 0–3, Crawler 0–2, Princess-Mika 0–2, OneBaseStalkerBot 0–2, kas 0–2, PiG_Bot 0–2 | KoB 2–0, GLM_Bot 2–0, 27turtles 2–0, Terranosaur 2–0, smokinggunbot 2–0, sharpy_protoss_test1 2–0 |

We don't have a "play slightly better" problem. Specific **strategies hard-counter
us the same way every game**. Beating one instance beats all future instances.

## Insight 2 — one loss mechanism dominates: the ARMY WIPE
In ~85% of losses our **supply crashes to 0** mid-game and never recovers:
`Klakinn 37→52→37→6`, `Crawler 33→28→0`, `ZEALOCALYPSE 30→1`, `sharpy 74→22→0`.
In **wins, supply never crashes** — it grows monotonically to 200 (max):
`Hestia 40→68→93→134→198`, `Stockfish 38→66→82→98→192`.

We win by macroing to max with overwhelming force; we lose by committing the
whole army to one fight, losing all of it, and getting overrun before rebuild.

## Insight 3 — the wipe has two sub-causes
- **(A) Out-produced in the opening** (~60% of wipes): enemy army value is
  **2–4× ours by 6–8 min** while we teched/expanded (Klakinn `8m 0v3375`,
  Crawler `8m 0v1925`, ZEALOCALYPSE `6m 50v2100`). One-base / fast-army
  timings arrive before we have enough units.
- **(B) Army thrown away** (~40%): comparable army, then we attack into a
  bigger one and evaporate (sharpy `8m 1750 → 10m 400`).
  - **Suspect: the parameter tuner.** The 47-game local marathon pushed
    `pressure_valve_supply` 60 → 34.7. That knob = "attack even into a
    predicted-loss fight at this army supply." At 34 we force-commit ~17
    stalkers into losing fights. The tuner's curriculum (CheatInsane/
    QueenBot/Clicadinha/Chance) rewards aggression; the ladder meta
    (timing-attack bots) punishes it. **Likely a training-distribution
    mismatch** — the local opponents don't represent the ladder.

## Insight 4 — the Protoss mirror is our worst matchup
Replay sample (loss-biased, so read relative not absolute):
vs **Protoss 20%**, vs Zerg 32%, vs Terran 50%. Protoss zealot/adept timings
(Klakinn, ZEALOCALYPSE, Apidae cannons, PerilousProtoss) are the sharpest
counters. Stalker-only doesn't hold zealot floods into our base.

## Insight 5 — late game: can't close (20min+ bucket is 2W–4L, 33%)
When ahead at 10–12 min we sometimes fail to finish: `DoopyBot 12m 4425v3375
→ 16m 1575v5875` (led big, lost). The colossus close-out just shipped targets
this but these games predate it.

## Recommended next cycles (priority order)
1. **Re-examine tuner aggression** — the pressure valve at 34 is the single
   most testable lever behind the army-wipe losses. Test: raise the floor /
   re-weight the objective to penalize army loss harder; or make the local
   training curriculum ladder-representative (add downloaded timing-attack
   bots, not just cheating AI).
2. **Hold, don't trade, when out-produced** — when the all-in read fires,
   never force-attack; sit on wall+batteries (partly shipped, verify it
   actually suppresses the pressure valve).
3. **Protoss-mirror defense** — earlier units / a second battery vs detected
   gateway aggression; stalker-only loses to zealot timings.
4. **Sim-gate correctness** — audit why (B) wipes pass the combat-sim gate
   (enemy not yet visible? mis-eval? pressure-valve override?).
