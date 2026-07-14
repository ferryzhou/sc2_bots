# Deimos

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

The #1 ladder bot: a polished macro Protoss that leans on **adept + phoenix harassment** while teching gateway→robo→stargate behind a strong economy. It grinds most opponents down with superior macro and constant multi-pronged pressure.

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~2295 (top-tier ladder bot) |
| **On ladder since** | 2024-07 |
| **Last source update** | 2026-07-07 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Standard gateway expand into cyber/robo/stargate; adept-heavy early pressure (the replays show 30+ adept phase-shifts — relentless adept shade harass).

- Adept and phoenix harassment on the worker line while it out-macros — it attacks the economy leg while staying safe (harassment lens, PRINCIPLES.md).
- Observers for detection and map vision; robo for immortals vs armored.
- Wins by macro + multi-front pressure, not a single timing — games often go long and it simply has more.

## Performance (recent ladder sample)

**Overall: 104–45 (69%)** over 149 decided games (+1 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 42-18 | 70% |
| vs Protoss | 26-6 | 81% |
| vs Zerg | 15-17 | 46% |
| vs Random | 21-4 | 84% |

**Toughest opponents:** negativeZero 0-5 (P), ANIbot 2-6 (T), Clicadinha 1-4 (Z), 12PoolBot 3-5 (Z), Roro 3-5 (T), zig-spudde 1-3 (T), EvilZoe 0-1 (Z), SharpenedEdge 0-1 (P).

**Best matchups:** theBigBot 10-0 (P), changeling 9-0 (R), Aeolus 8-0 (P), Phobos 8-0 (T), TyrT 7-0 (T), BenBotBC 7-1 (T), Eris 6-3 (Z), GPT 5-2 (T).

## Observed builds (from its own replays)

**vs 12PoolBot (Z), 32.5 min, won:** Probe×23, Stalker×15, Pylon×9, Gateway×5, Nexus×2, Assimilator×2, CyberneticsCore×1, RoboticsFacility×1, Adept×1, Observer×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 44 | 875 | 1250 | 22 | 18 |
| 6 | 50 | 46 | 2450 | 1350 | 22 | 19 |
| 8 | 66 | 65 | 3050 | 1825 | 26 | 23 |
| 12 | 103 | 106 | 4475 | 3425 | 44 | 33 |

**vs Eris (Z), 32.3 min, won:** Probe×48, AdeptPhaseShift×32, Phoenix×9, Pylon×8, Assimilator×4, Adept×4, Stalker×4, Nexus×2, Gateway×2, Stargate×2, ShieldBattery×2, CyberneticsCore×1, RoboticsFacility×1, ChangelingZealot×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 42 | 46 | 625 | 650 | 30 | 33 |
| 6 | 64 | 77 | 1550 | 875 | 44 | 53 |
| 8 | 85 | 96 | 3425 | 1875 | 48 | 58 |
| 12 | 142 | 187 | 5925 | 4650 | 73 | 88 |

**vs changeling (T), 30.1 min, won:** Probe×54, AdeptPhaseShift×14, Stalker×8, Pylon×7, Gateway×4, Assimilator×3, Nexus×2, Adept×2, CyberneticsCore×1, Stargate×1, Phoenix×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 38 | 34 | 675 | 400 | 26 | 25 |
| 6 | 51 | 59 | 950 | 1050 | 35 | 34 |
| 8 | 75 | 84 | 2525 | 2050 | 45 | 45 |
| 12 | 111 | 94 | 4425 | 1925 | 54 | 59 |

## Strengths

- Best-in-class macro and multitasking — dominant vs Protoss (26-6 in sample) and Terran (42-18).
- Adept/phoenix harass forces the opponent to defend two places at once.
- Has answers to most things (observer detection, immortals, phoenix anti-air).

## Weaknesses

- Its softest matchup is Zerg (15-17) — a mass-army/creep Zerg that defends the harass and remaxes can out-scale the gateway army.
- Gateway-based army without heavy splash can be overwhelmed by mass light if the harass doesn't pay off.

## How to beat it

1. Defend the adept/phoenix harass cheaply (static defense + a couple of anti-air) so it gets no free economic damage — that removes its main edge.
2. Match or exceed its macro and force splash-favorable fights; as Zerg, mass army + creep + remax is the proven answer.
3. Don't over-commit into a defended deathball; take favorable trades only.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*