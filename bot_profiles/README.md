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
  events). Many strong bots have their **replays cleaned by the author** (a
  privacy/retention setting — e.g. Eris, BenBotBC, MicroMachine keep 0
  downloadable replays), so their build can't be captured from replays at all;
  those profiles are from race + record (+ reputation for well-known bots) and
  say so. Older replays don't help — they're cleaned first.
- **Open-source bots** (source publicly downloadable) are read from their actual
  code — those profiles are the most authoritative. Currently: **12PoolBot, who,
  QueenBot, Krillin** (Python). Compiled/closed bots (C++, .NET, Java) are from
  replays + record.
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
| 33 | [MechaShark](MechaShark/PROFILE.md) | T | 1849 | Terran macro (mech-leaning) | Z | T |  |
| 34 | [ArgoTest](ArgoTest/PROFILE.md) | P | 1842 | Skytoss cannon+tempest (ArgoBot dev) | Z | R |  |
| 35 | [Sharkling](Sharkling/PROFILE.md) | Z | 1838 | Zerg | R | P |  |
| 36 | [LunaxVRRTest](LunaxVRRTest/PROFILE.md) | P | 1836 | Skytoss void/tempest (LunaxVRR dev) | R | P |  |
| 37 | [JimmyBotZ](JimmyBotZ/PROFILE.md) | Z | 1820 | Roach/drone macro Zerg | P | T |  |
| 38 | [ZeratulsRevengeTest](ZeratulsRevengeTest/PROFILE.md) | P | 1794 | Protoss zealot (dev, unstable) | Z | T |  |
| 39 | [Aeolus](Aeolus/PROFILE.md) | P | 1774 | Stalker/blink macro Protoss | T | R | yes |
| 40 | [zig-spudde](zig-spudde/PROFILE.md) | T | 1757 | Terran bio-tank | R | Z |  |
| 41 | [Cyne](Cyne/PROFILE.md) | P | 1756 | Protoss gateway/robo (weak form) | R | P |  |
| 42 | [LordSuperKing](LordSuperKing/PROFILE.md) | P | 1752 | Protoss stalker+tempest | T | R |  |
| 43 | [AvocaDOS](AvocaDOS/PROFILE.md) | T | 1741 | Terran bio | P | T |  |
| 44 | [Battler](Battler/PROFILE.md) | T | 1718 | Terran reaper bio/mech | Z | P |  |
| 45 | [Apidae](Apidae/PROFILE.md) | P | 1718 | Protoss cannon turtle/rush | R | P |  |
| 46 | [Clicadinha](Clicadinha/PROFILE.md) | Z | 1716 | Roach macro Zerg | P | T | yes |
| 47 | [Arpy](Arpy/PROFILE.md) | P | 1713 | Protoss gateway zealot/adept | R | T |  |
| 48 | [muravevtest](muravevtest/PROFILE.md) | Z | 1710 | Speedling macro Zerg (muravev dev) | T | Z |  |
| 49 | [BigDaddy](BigDaddy/PROFILE.md) | T | 1705 | Terran bio (marine/medivac) | R | T |  |
| 50 | [norman](norman/PROFILE.md) | P | 1705 | Broken/losing (current) | Z | T | yes |
| 51 | [AvocaDEV](AvocaDEV/PROFILE.md) | T | 1700 | Terran bio (dev) | Z | P |  |
| 52 | [Mulebot](Mulebot/PROFILE.md) | T | 1697 | Terran bio-mech | T | R | yes |
| 53 | [Dovahkiin](Dovahkiin/PROFILE.md) | Z | 1697 | Zerg macro | Z | T |  |
| 54 | [72Tortoises](72Tortoises/PROFILE.md) | Z | 1691 | Roach/ling macro Zerg | T | P |  |
| 55 | [FlowerPrincess](FlowerPrincess/PROFILE.md) | Z | 1682 | Ling-flood Zerg | T | R |  |
| 56 | [Dodo](Dodo/PROFILE.md) | Z | 1678 | Drone macro Zerg (Nydus) | T | R |  |
| 57 | [CynEX](CynEX/PROFILE.md) | P | 1677 | Skytoss/stalker macro Protoss | T | R |  |
| 58 | [PerilousProtossBot](PerilousProtossBot/PROFILE.md) | P | 1666 | Protoss zealot/cannon (weak form) | P | R |  |
| 59 | [Voltron](Voltron/PROFILE.md) | T | 1661 | Terran bio-tank | P | R |  |
| 60 | [Forgefiend](Forgefiend/PROFILE.md) | P | 1657 | Protoss cannon turtle/rush | T | P |  |
| 61 | [Creepy_duo_canon](Creepy_duo_canon/PROFILE.md) | P | 1655 | Protoss double cannon rush | P | Z |  |
| 62 | [nida](nida/PROFILE.md) | P | 1653 | Protoss gateway stalker/phoenix | R | T |  |
| 63 | [clone](clone/PROFILE.md) | T | 1648 | Terran reaper/starport | T | R | yes |
| 64 | [PiG_Bot](PiG_Bot/PROFILE.md) | P | 1646 | Protoss gateway/robo macro | T | R |  |
| 65 | [Asteria](Asteria/PROFILE.md) | P | 1642 | Stargate skytoss (carrier/tempest) | T | R |  |
| 66 | [ArtZerg](ArtZerg/PROFILE.md) | Z | 1642 | Ling/roach aggro Zerg | Z | T |  |
| 67 | [Terranosaur](Terranosaur/PROFILE.md) | T | 1641 | Terran mass-marine bio | T | Z |  |
| 68 | [kas](kas/PROFILE.md) | Z | 1638 | Over-drone macro Zerg | T | Z |  |
| 69 | [Persephone](Persephone/PROFILE.md) | Z | 1632 | Ling/roach macro Zerg | P | R |  |
| 70 | [Horizon](Horizon/PROFILE.md) | T | 1625 | Terran bio/air macro | P | Z |  |
| 71 | [muravev](muravev/PROFILE.md) | Z | 1624 | Speedling macro Zerg | T | Z |  |
| 72 | [ZEALOCALYPSE](ZEALOCALYPSE/PROFILE.md) | P | 1623 | Protoss zealot flood | R | T |  |
| 73 | [TheLAW](TheLAW/PROFILE.md) | T | 1619 | Terran bio macro | R | Z |  |
| 74 | [OneBaseStalkerBot](OneBaseStalkerBot/PROFILE.md) | P | 1614 | Protoss one-base stalker | R | T |  |
| 75 | [QueenBot](QueenBot/PROFILE.md) | Z | 1611 | Queen/creep macro Zerg | P | R | yes |
| 76 | [Hellcannon](Hellcannon/PROFILE.md) | P | 1609 | Protoss cannon+zealot | Z | T |  |
| 77 | [smokinggunbot](smokinggunbot/PROFILE.md) | T | 1602 | Terran bio-tank turtle | R | Z |  |
| 78 | [zig-reapers](zig-reapers/PROFILE.md) | T | 1602 | Terran mass-reaper all-in | Z | T | yes |
| 79 | [sharpy_protoss_test1](sharpy_protoss_test1/PROFILE.md) | P | 1601 | Protoss gateway/stargate | T | P |  |
| 80 | [OmegaZ](OmegaZ/PROFILE.md) | Z | 1600 | Zerg ling (weak form) | T | T |  |
| 81 | [PhantomTest](PhantomTest/PROFILE.md) | Z | 1600 | Zerg (dev, weak form) | Z | P |  |
| 82 | [ur_moms_a_ho](ur_moms_a_ho/PROFILE.md) | Z | 1600 | Zerg (small sample) | T | P |  |
| 83 | [Krillin](Krillin/PROFILE.md) | Z | 1600 | Zerg macro/aggro | P | T | yes |

*Best/Worst vs = the race this bot has the highest / lowest win-rate against in the sample. Regenerate with `python bot_profiles/_generate_objective.py`.*

## Ranked but not profiled (insufficient recent activity)

These bots are on the ladder but had fewer than 6 decided games in the sample (many sit at the default ~1600 Elo — new, inactive, or rarely scheduled), so there isn't enough data to characterize them yet:

bilisaur (Z, ~1600), Hello_world (Z, ~1600), SunsetOrpheus (R, ~1600), bottinger (Z, ~1600), Kauyon (P, ~1600), IntrusiveThoughts (Z, ~1600), Thssprtssbt_fan (P, ~1600), Hannibal (Z, ~1600), Chomppet (T, ~1600), BobbyBotV10 (R, ~1600), NextProBot (Z, ~1600), RU (Z, ~1600), DownedStar (P, ~1600).