# AI Arena Opponent Profiles

A scouting dossier on the bots GriffinBot (our Terran bio/tank macro bot, AI
Arena id 1187) faces on the ladder. One folder per opponent, each with the bot's
race, build order, economy trajectory, strengths, weaknesses, and the specific
way GriffinBot should play the matchup — all mapped onto our
[`PRINCIPLES.md`](../PRINCIPLES.md) / [`STRATEGY.md`](../STRATEGY.md) /
[`OPPONENTS.md`](../OPPONENTS.md) framework.

## How this was built

- **Source:** GriffinBot's 92-game AI Arena match history (current season),
  pulled from the AI Arena API. Raw data in [`data/`](data/).
- **Build orders:** extracted from each game's replay tracker events with
  s2protocol (same machinery as [`analysis/aa_analyze.py`](../analysis/aa_analyze.py)).
  Each profile shows the opponent's real first-8-minutes production and the
  side-by-side supply/army/worker trajectory.
- **Reproducible:** run `python bot_profiles/_generate.py` to regenerate every
  profile and this index from [`data/profile_data.json`](data/profile_data.json).

## Caveats (read before trusting a profile)

- Most profiles are built from **one sampled game** per opponent. Bots are
  largely deterministic (see [`OPPONENTS.md`](../OPPONENTS.md)), so one game is
  usually representative — but a bot can be updated, or play a different branch.
  **Re-scout to confirm** and update the profile after new games.
- Bots marked **Random (R)** played a specific race in our sampled game; they
  may roll a different race next time.
- `passive/broken` means the bot barely functioned *in our game* — it may play
  far better against other opponents. Treated as a free win, cautiously.
- Army/supply/worker figures are from Blizzard's in-game score values, sampled
  at 2-minute marks.

## The one-paragraph summary

GriffinBot plays **one fixed, slow-but-safe macro opening every game** (~36
supply / 25 workers / 400 army value at 4:00, regardless of opponent). It wins
30 / loses 55 (35%). The losses fall into two clusters: **(1) early all-ins /
timings** (Protoss zealot floods, mass reaper/marauder, Zerg ling floods) that
wipe our army at 7–9 min before tanks are online — a *build-order* loss micro
can't fix; and **(2) greedy macro** Zerg/Terran that simply out-economies and
out-remaxes our slow start. We beat passive/broken bots, turtles we out-expand,
and gateway pressure we hold. The fixes are in [`OPPONENTS.md`](../OPPONENTS.md):
flex opening safety to a per-opponent prior, **hold don't trade** against
aggression, and **punish the greedy window** with harassment.

## Master table

Sorted by number of games played (recurring opponents first), losses before
wins. `src` = bot source is publicly downloadable for deeper study.

| Opponent | Race | Archetype | Our record | Result | src |
|---|:--:|---|:--:|:--:|:--:|
| [GLM_Bot](GLM_Bot/PROFILE.md) | Z | Z drone macro | 1-2 | **LOSS** |  |
| [Princess-Mika](Princess-Mika/PROFILE.md) | Z | Z ling flood | 0-3 | **LOSS** |  |
| [WorkingAsIntended](WorkingAsIntended/PROFILE.md) | R | T bio macro | 0-3 | **LOSS** |  |
| [AxeFighter](AxeFighter/PROFILE.md) | T | T bio macro | 0-2 | **LOSS** | yes |
| [DasyBot](DasyBot/PROFILE.md) | P | P robo/immortal | 0-2 | **LOSS** |  |
| [Hestia](Hestia/PROFILE.md) | T | T mech | 0-2 | **LOSS** |  |
| [KoB](KoB/PROFILE.md) | Z | Z drone macro | 0-2 | **LOSS** |  |
| [muravevTerran](muravevTerran/PROFILE.md) | T | T mech | 0-2 | **LOSS** |  |
| [oberon](oberon/PROFILE.md) | T | T one-base all-in | 0-2 | **LOSS** | yes |
| [onlyfans](onlyfans/PROFILE.md) | T | T starport air | 0-1 | **LOSS** | yes |
| [SiriusBot](SiriusBot/PROFILE.md) | R | Z drone macro | 0-2 | **LOSS** |  |
| [StarK234_0000](StarK234_0000/PROFILE.md) | T | T bio macro | 0-2 | **LOSS** |  |
| [Stark234_PR02](Stark234_PR02/PROFILE.md) | T | T bio macro | 0-2 | **LOSS** |  |
| [Thssprtssbt](Thssprtssbt/PROFILE.md) | P | P air/skytoss | 0-2 | **LOSS** | yes |
| [27turtles](27turtles/PROFILE.md) | T | T mech | 2-0 | **WIN** |  |
| [Crawler](Crawler/PROFILE.md) | Z | Z ling flood | 1-1 | even |  |
| [GenesisLotus](GenesisLotus/PROFILE.md) | P | P gateway pressure | 2-0 | **WIN** | yes |
| [JackBot2.0](JackBot2.0/PROFILE.md) | T | passive/broken | 2-0 | **WIN** |  |
| [Visenya](Visenya/PROFILE.md) | Z | passive/broken | 2-0 | **WIN** |  |
| [Apidae](Apidae/PROFILE.md) | P | P cannon turtle | 0-1 | **LOSS** |  |
| [Asteria](Asteria/PROFILE.md) | P | P air/skytoss | 0-1 | **LOSS** |  |
| [BioBot](BioBot/PROFILE.md) | T | T bio macro | 0-1 | **LOSS** |  |
| [BobbyBotV13](BobbyBotV13/PROFILE.md) | R | Z drone macro | 0-1 | **LOSS** |  |
| [Creepy_macro](Creepy_macro/PROFILE.md) | Z | Z drone macro | 0-1 | **LOSS** |  |
| [DoopyBot](DoopyBot/PROFILE.md) | Z | Z drone macro | 0-1 | **LOSS** |  |
| [Horizon](Horizon/PROFILE.md) | T | T starport air | 0-1 | **LOSS** |  |
| [kas](kas/PROFILE.md) | Z | Z mutalisk | 0-1 | **LOSS** |  |
| [Klakinn](Klakinn/PROFILE.md) | P | P gateway all-in | 0-1 | **LOSS** |  |
| [Lissy](Lissy/PROFILE.md) | Z | Z ling flood | 0-1 | **LOSS** |  |
| [LoremIpsum](LoremIpsum/PROFILE.md) | Z | Z drone macro | 0-1 | **LOSS** |  |
| [muravev](muravev/PROFILE.md) | Z | Z drone macro | 0-1 | **LOSS** |  |
| [MY_SCRIPTING_SON](MY_SCRIPTING_SON/PROFILE.md) | Z | Z ling flood | 0-1 | **LOSS** | yes |
| [OneBaseStalkerBot](OneBaseStalkerBot/PROFILE.md) | P | P gateway all-in | 0-1 | **LOSS** |  |
| [PerilousProtossBot](PerilousProtossBot/PROFILE.md) | P | P gateway all-in | 0-1 | **LOSS** |  |
| [Persephone](Persephone/PROFILE.md) | Z | Z drone macro | 0-1 | **LOSS** |  |
| [PiG_Bot](PiG_Bot/PROFILE.md) | P | P macro deathball | 0-1 | **LOSS** |  |
| [Princess-Mika-Test](Princess-Mika-Test/PROFILE.md) | Z | Z ling flood | 0-1 | **LOSS** |  |
| [protossinger](protossinger/PROFILE.md) | P | P gateway all-in | 0-1 | **LOSS** |  |
| [QueenBot](QueenBot/PROFILE.md) | Z | Z drone macro | 0-1 | **LOSS** | yes |
| [sharpy_protoss_test1](sharpy_protoss_test1/PROFILE.md) | P | P air/skytoss | 0-1 | **LOSS** |  |
| [Slowpoke](Slowpoke/PROFILE.md) | T | T bio macro | 0-1 | **LOSS** |  |
| [smokinggunbot](smokinggunbot/PROFILE.md) | T | T bio macro | 0-1 | **LOSS** |  |
| [ZEALOCALYPSE](ZEALOCALYPSE/PROFILE.md) | P | P gateway all-in | 0-1 | **LOSS** |  |
| [zig-reapers](zig-reapers/PROFILE.md) | T | T one-base all-in | 0-1 | **LOSS** | yes |
| [Alexa](Alexa/PROFILE.md) | T | T bio macro | 1-0 | **WIN** |  |
| [BioBotGod](BioBotGod/PROFILE.md) | T | passive/broken | 1-0 | **WIN** |  |
| [Chance](Chance/PROFILE.md) | R | passive/broken | 1-0 | **WIN** | yes |
| [CodeX001](CodeX001/PROFILE.md) | P | passive/broken | 0-0+1T | even |  |
| [Creepy_duo_canon](Creepy_duo_canon/PROFILE.md) | P | P cannon turtle | 0-0+1T | even |  |
| [Creepy_sentry](Creepy_sentry/PROFILE.md) | P | P gateway pressure | 1-0 | **WIN** |  |
| [CryptBotRevival](CryptBotRevival/PROFILE.md) | P | P gateway pressure | 1-0 | **WIN** | yes |
| [CyraxxDKAkron](CyraxxDKAkron/PROFILE.md) | T | passive/broken | 1-0 | **WIN** |  |
| [DoopyBot-Test](DoopyBot-Test/PROFILE.md) | Z | Z drone macro | 1-0 | **WIN** |  |
| [DownedStar1](DownedStar1/PROFILE.md) | T | T mech | 1-0 | **WIN** |  |
| [Forge](Forge/PROFILE.md) | P | P air/skytoss | 0-0+1T | even |  |
| [iGottaCRush](iGottaCRush/PROFILE.md) | P | P gateway all-in | 1-0 | **WIN** |  |
| [Laser-Circus](Laser-Circus/PROFILE.md) | P | P cannon turtle | 1-0 | **WIN** |  |
| [Leviabyss](Leviabyss/PROFILE.md) | Z | passive/broken | 0-0 | even |  |
| [lishimin](lishimin/PROFILE.md) | P | passive/broken | 1-0 | **WIN** |  |
| [MangoShark](MangoShark/PROFILE.md) | P | passive/broken | 0-0 | even |  |
| [Montka](Montka/PROFILE.md) | R | T bio macro | 1-0 | **WIN** |  |
| [Myztery](Myztery/PROFILE.md) | Z | Z drone macro | 1-0 | **WIN** |  |
| [PrimordialOrigin](PrimordialOrigin/PROFILE.md) | P | P gateway pressure | 1-0 | **WIN** | yes |
| [Siriusly](Siriusly/PROFILE.md) | R | Z drone macro | 1-0 | **WIN** |  |
| [Starcraft-Agent-v01](Starcraft-Agent-v01/PROFILE.md) | T | passive/broken | 0-0+1T | even |  |
| [Starlight](Starlight/PROFILE.md) | P | P cannon turtle | 1-0 | **WIN** |  |
| [Terranosaur](Terranosaur/PROFILE.md) | T | T bio macro | 1-0 | **WIN** |  |
| [TheCatSC2Bot](TheCatSC2Bot/PROFILE.md) | P | P robo/immortal | 1-0 | **WIN** |  |
| [WildLupo](WildLupo/PROFILE.md) | P | P gateway pressure | 1-0 | **WIN** |  |
| [Zummok](Zummok/PROFILE.md) | T | passive/broken | 1-0 | **WIN** |  |

*Regenerate with `python bot_profiles/_generate.py`.*