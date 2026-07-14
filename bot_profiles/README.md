# AI Arena Bot Profiles

Objective scouting profiles of the **top AI Arena ladder bots** — each bot's own
strategy, build, and record, studied on its own terms (not from any one
opponent's point of view).

## What's here

One folder per bot with a `PROFILE.md`: identity (race, type, Elo, longevity,
whether its source is public), strategy and opening, a per-race win/loss record,
the builds observed in its own replays, and an analysis of its strengths,
weaknesses, and how to beat it.

## Method & caveats

- **Records** are a recent-match sample per bot from the AI Arena API — they
  show *current form and matchup tendencies*, not lifetime totals. The Elo column
  is the real ranking signal; treat the per-race **win %** as the matchup read.
- **Builds** are extracted from each bot's own replays (s2protocol tracker
  events). Where recent replays were cleaned/unavailable, the build wasn't
  directly observed and the strategy is inferred from race + record (+ reputation
  for well-known bots) — each profile says which.
- **Open-source bots** (source publicly downloadable) are read from their actual
  code — those profiles are the most authoritative. Currently: 12PoolBot, who
  (and the C++/closed ones are from replays + record).
- Bots iterate constantly (some self-tune per game), so re-check periodically.
- Raw data: [`data/topbot_data.json`](data/topbot_data.json),
  [`data/stats/`](data/stats/). Regenerate with
  `python bot_profiles/_generate_objective.py`.

## Top ladder bots (by Elo)

| # | Bot | Race | Elo | Style | Best vs | Worst vs | Source |
|--:|---|:--:|--:|---|:--:|:--:|:--:|
| 1 | [Deimos](Deimos/PROFILE.md) | P | 2295 | Macro Protoss, adept/phoenix harass | R | Z |  |
| 2 | [Eris](Eris/PROFILE.md) | Z | 2283 | Macro Zerg (roach/ling) | P | R |  |
| 3 | [Phobos](Phobos/PROFILE.md) | T | 2150 | Terran bio (MMM) | P | R |  |
| 4 | [BenBotBC](BenBotBC/PROFILE.md) | T | 2143 | Terran bio, marine micro | R | Z |  |
| 5 | [Zozo](Zozo/PROFILE.md) | P | 2109 | Macro Protoss | R | P |  |
| 6 | [Xena](Xena/PROFILE.md) | R | 2103 | Random, adaptive macro | R | P |  |
| 7 | [MicroMachine](MicroMachine/PROFILE.md) | T | 2094 | Terran marine-micro specialist | T | P | yes |
| 8 | [ArgoBot](ArgoBot/PROFILE.md) | P | 2065 | Skytoss (cannon+tempest) | T | P |  |
| 9 | [GPT](GPT/PROFILE.md) | T | 2056 | Terran bio-tank | Z | T |  |
| 10 | [SharpenedEdge](SharpenedEdge/PROFILE.md) | P | 2042 | Macro Protoss | R | T |  |
| 11 | [tito](tito/PROFILE.md) | Z | 2036 | Macro Zerg | R | Z |  |
| 12 | [who](who/PROFILE.md) | R | 2033 | Random cheese/proxy specialist | P | R | yes |
| 13 | [Caninana](Caninana/PROFILE.md) | Z | 2025 | Micro macro Zerg | P | T |  |
| 14 | [smallBly](smallBly/PROFILE.md) | Z | 1996 | Zerg | Z | P |  |
| 15 | [DominionDog](DominionDog/PROFILE.md) | T | 1987 | Terran bio | Z | P |  |
| 16 | [chito](chito/PROFILE.md) | Z | 1977 | Speedling macro Zerg | P | T |  |
| 17 | [VeTerran-revived](VeTerran-revived/PROFILE.md) | T | 1972 | Terran bio/mech macro | Z | P | yes |
| 18 | [WickedBot](WickedBot/PROFILE.md) | T | 1940 | Terran bio | Z | T |  |
| 19 | [TyrP](TyrP/PROFILE.md) | P | 1933 | Protoss macro | R | T |  |
| 20 | [WoundMaker](WoundMaker/PROFILE.md) | Z | 1932 | Mutalisk Zerg | P | Z |  |
| 21 | [Roro](Roro/PROFILE.md) | T | 1922 | Terran | P | T |  |
| 22 | [PhantomBot](PhantomBot/PROFILE.md) | Z | 1921 | Zerg | Z | T |  |
| 23 | [BotTato](BotTato/PROFILE.md) | T | 1909 | Terran mech/reaper | R | Z |  |
| 24 | [sharkbot](sharkbot/PROFILE.md) | P | 1903 | Protoss macro | P | T |  |
| 25 | [whalemean](whalemean/PROFILE.md) | R | 1896 | Random | Z | T |  |
| 26 | [JimmyBotP](JimmyBotP/PROFILE.md) | P | 1887 | Protoss (stalker/immortal/oracle) | P | R |  |
| 27 | [TyrT](TyrT/PROFILE.md) | T | 1884 | Terran macro | R | T |  |
| 28 | [LunaxVRR](LunaxVRR/PROFILE.md) | P | 1883 | Skytoss (cannon+tempest) | Z | R |  |
| 29 | [WaterLeak](WaterLeak/PROFILE.md) | Z | 1876 | Roach/ling Zerg | Z | T |  |
| 30 | [JimmyBot](JimmyBot/PROFILE.md) | R | 1860 | Random (Zerg-leaning) | R | T |  |
| 31 | [JimmyBotT](JimmyBotT/PROFILE.md) | T | 1860 | Terran bio-tank | Z | T |  |
| 32 | [12PoolBot](12PoolBot/PROFILE.md) | Z | 1858 | 12-pool speedling macro Zerg | Z | P | yes |

*Best/Worst vs = the race this bot has the highest / lowest win-rate against in the sample. Regenerate with `python bot_profiles/_generate_objective.py`.*