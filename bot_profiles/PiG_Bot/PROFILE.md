# PiG_Bot

*Objective scouting profile — the bot's own strategy, build, and record, independent of any particular opponent.*

## Summary

A **gateway/robo macro Protoss**: stalker/zealot with observer and robo tech, sometimes high templar, off three bases. Balanced deathball macro (67-71).

## Identity

| | |
|---|---|
| **Race** | Protoss |
| **Bot type** | python |
| **AI Arena Elo** | ~1646 (top-tier ladder bot) |
| **On ladder since** | 2024-06 |
| **Last source update** | 2026-06-30 |
| **Source public** | no (closed source; profiled from replays + record) |

## Strategy

**Opening:** Gateway expand into cyber/robo; stalker/zealot with observer, expanding to three bases.

- Gateway/robo deathball with upgrades and observer detection; macro into a strong mid-game army (adds templar/storm in longer games).
- Plays the game straight — no gimmick, wins on execution.

## Performance (recent ladder sample)

**Overall: 67–71 (48%)** over 138 decided games (+12 draws/no-result).

| Matchup | Record | Win % |
|---|---|---|
| vs Terran | 22-20 | 52% |
| vs Protoss | 23-25 | 47% |
| vs Zerg | 21-22 | 48% |
| vs Random | 1-4 | 20% |

**Toughest opponents:** nida 1-5 (P), Princess-Mika 1-4 (Z), DougrizoBot 0-3 (T), Positive_Null 1-3 (Z), norman 1-3 (P), WaterLeak 0-2 (Z), Creepy_duo_canon 0-2 (P), 27turtles 0-2 (T).

**Best matchups:** miniTestikZ 5-0 (Z), 49Terrapins 5-0 (P), BotTato 4-0 (T), Alexa 4-0 (T), Dominion 4-0 (T), Hybrid 3-0 (P), SilverBio 3-1 (T), miniTestikP 3-1 (P).

## Observed builds (from its own replays)

**vs QueenBot (Z), 46.6 min, won:** Probe×57, Pylon×10, Stalker×5, Gateway×4, Assimilator×4, Zealot×4, Nexus×3, RoboticsFacility×2, CyberneticsCore×1, Observer×1, Immortal×1, RoboticsBay×1, TwilightCouncil×1, Forge×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 45 | 275 | 700 | 34 | 30 |
| 6 | 64 | 69 | 1425 | 1575 | 45 | 43 |
| 8 | 90 | 92 | 1625 | 725 | 64 | 69 |
| 12 | 199 | 66 | 8375 | 1600 | 92 | 36 |

**vs SiriusBot (Z), 39.3 min, won:** Probe×55, Pylon×8, Zealot×5, Stalker×5, Gateway×4, Assimilator×4, Nexus×3, RoboticsFacility×2, CyberneticsCore×1, Observer×1, Immortal×1, RoboticsBay×1, Forge×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 43 | 41 | 275 | 525 | 34 | 34 |
| 6 | 64 | 76 | 1425 | 350 | 45 | 64 |
| 8 | 89 | 72 | 1525 | 325 | 63 | 60 |
| 12 | 167 | 102 | 5425 | 800 | 90 | 73 |

**vs Bubu (P), 37.1 min, won:** Probe×48, Pylon×5, Gateway×4, Assimilator×4, Stalker×4, Nexus×3, Zealot×2, CyberneticsCore×1, ShieldBattery×1, Forge×1, TwilightCouncil×1

| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |
|--:|--:|--:|--:|--:|--:|--:|
| 4 | 36 | 30 | 550 | 350 | 27 | 22 |
| 6 | 52 | 44 | 900 | 1925 | 38 | 22 |
| 8 | 68 | 54 | 900 | 2625 | 53 | 24 |
| 12 | 125 | 57 | 1400 | 1225 | 89 | 42 |

## Strengths

- Balanced army + economy; observer detection; even across matchups.

## Weaknesses

- No exploitable extreme; gateway/robo core can be out-splashed if it clumps, and out-macroed.

## How to beat it

1. Match upgrades and force splash-favorable fights; keep tanks sieged so its deathball eats splash.
2. Out-macro via cleaner production; take only favorable engagements.

---
*Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.*