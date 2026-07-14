# OneBaseStalkerBot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **one-base stalker all-in Protoss**: pumps ~20+ stalkers off a single base and pushes before the opponent has an army. All-in timing. Weak vs Terran (6-19).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1614 (top-tier ladder bot) |
| **On ladder since** | 2026-06 |
| **Last source update** | 2026-06-29 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** One base, 3-4 gateways, mass Stalker — no expansion, all army by ~8 min.

- Mass stalkers on one base and attack — a ranged all-in that ends the game early or loses.
- Blink (if teched) to reinforce and kite.

## Performance (recent ladder sample)

**Overall: 63–68 (48%)** over 131 decided games (+19 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 6-19 | 24% |
| vs Protoss | 22-24 | 47% |
| vs Zerg | 28-22 | 56% |
| vs Random | 7-3 | 70% |

**Toughest opponents:** nida 0-5 (P), Forgefiend 0-5 (P), smokinggunbot 0-5 (T), Horizon 0-5 (T), Princess-Mika 0-4 (Z), 27turtles 0-4 (T), PerilousProtossBot 0-4 (P), ZEALOCALYPSE 0-3 (P).

**Best matchups:** Klakinn 4-1 (P), Crawler 4-1 (Z), PiG_Bot 4-1 (P), ArtZerg 3-0 (Z), sharpy_protoss_test1 3-1 (P), Asteria 2-0 (P), zig-reapers 2-0 (T), muravev 2-0 (Z).

## Observed builds (from its own replays)

**vs Hestia (T), 23.9 min, won:** Probe×22, Stalker×22, Pylon×6, Gateway×4, Assimilator×2, Nexus×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 32 | 32 | 525 | 300 | 22 | 25 |
| 6 | 54 | 46 | 2800 | 950 | 22 | 24 |
| 8 | 52 | 21 | 2450 | 600 | 22 | 8 |
| 12 | 30 | 24 | 700 | 300 | 22 | 13 |

**vs GLM_Bot (Z), 23.9 min, won:** Probe×22, Stalker×21, Pylon×6, Gateway×4, Assimilator×2, Nexus×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 30 | 44 | 350 | 775 | 22 | 26 |
| 6 | 44 | 71 | 1925 | 350 | 22 | 51 |
| 8 | 60 | 76 | 3325 | 175 | 22 | 67 |
| 12 | 88 | 85 | 5600 | 700 | 22 | 70 |

**vs Creepy_duo_canon (P), 20.1 min, won:** Probe×38, Stalker×7, Gateway×4, Assimilator×4, Pylon×2, Nexus×1, CyberneticsCore×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 16 | 23 | 350 | 200 | 10 | 17 |
| 6 | 18 | 25 | 525 | 200 | 11 | 17 |
| 8 | 22 | 21 | 875 | 0 | 12 | 17 |
| 12 | 27 | 22 | 1225 | 100 | 12 | 15 |

## Strengths

- Ranged all-in overwhelms greedy/undefended openings (even vs Protoss 22-24, good vs Zerg 28-22).
- Stalkers out-range a bare wall — needs real defense to hold.

## Weaknesses

- One base, no economy — a held all-in loses; weak vs Terran (6-19) where tanks + a wall crush it.
- No splash/tech beyond the timing.

## How to beat it

1. Treat as an all-in: wall, tanks/bunker + units, hold the timing (don't trade in the open).
2. Survive → its one base loses to your expand.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*