#!/usr/bin/env python3
"""Generate objective per-bot profiles for the top ladder bots from
data/topbot_data.json (record-by-race, toughest/best opponents, and build
orders extracted from each bot's own replays via s2protocol).

Factual sections are auto-generated from data. Analysis sections (strategy,
strengths, weaknesses, how-to-beat) come from the ANALYSIS dict below, which is
hand-written per bot and grounded in that bot's collected build + record +
(for open-source bots) its actual code.

    python bot_profiles/_generate_objective.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = {}
for _f in ("topbot_data.json", "topbot_data2.json"):
    _p = os.path.join(HERE, "data", _f)
    if os.path.exists(_p):
        DATA.update(json.load(open(_p)))
RACE = {"P": "Protoss", "T": "Terran", "Z": "Zerg", "R": "Random"}

# Hand-written analysis per bot, grounded in the collected build orders, the
# per-race record, and (for open-source bots) their actual code. Where a build
# was not directly observed (replays cleaned), the strategy is inferred from the
# per-race record + race + reputation and is marked as such.
ANALYSIS = {
 "Deimos": dict(
   summary="The #1 ladder bot: a polished macro Protoss that leans on **adept + "
     "phoenix harassment** while teching gateway→robo→stargate behind a strong "
     "economy. It grinds most opponents down with superior macro and constant "
     "multi-pronged pressure.",
   opening="Standard gateway expand into cyber/robo/stargate; adept-heavy early "
     "pressure (the replays show 30+ adept phase-shifts — relentless adept "
     "shade harass).",
   strategy=[
     "Adept and phoenix harassment on the worker line while it out-macros — it "
     "attacks the economy leg while staying safe (harassment lens, PRINCIPLES.md).",
     "Observers for detection and map vision; robo for immortals vs armored.",
     "Wins by macro + multi-front pressure, not a single timing — games often go "
     "long and it simply has more.",
   ],
   strengths=[
     "Best-in-class macro and multitasking — dominant vs Protoss (26-6 in sample) "
     "and Terran (42-18).",
     "Adept/phoenix harass forces the opponent to defend two places at once.",
     "Has answers to most things (observer detection, immortals, phoenix anti-air).",
   ],
   weaknesses=[
     "Its softest matchup is Zerg (15-17) — a mass-army/creep Zerg that defends "
     "the harass and remaxes can out-scale the gateway army.",
     "Gateway-based army without heavy splash can be overwhelmed by mass light "
     "if the harass doesn't pay off.",
   ],
   beat=[
     "Defend the adept/phoenix harass cheaply (static defense + a couple of "
     "anti-air) so it gets no free economic damage — that removes its main edge.",
     "Match or exceed its macro and force splash-favorable fights; as Zerg, mass "
     "army + creep + remax is the proven answer.",
     "Don't over-commit into a defended deathball; take favorable trades only.",
   ]),
 "Eris": dict(
   summary="A top-tier **macro Zerg** and one of the ladder's most established "
     "bots. Drones hard, spreads creep, and converts a big economy into "
     "roach/ling/hydra waves with fast remax. (Closed source — build not "
     "directly captured in this sample; characterization from record + reputation.)",
   opening="Hatch-first economic Zerg opening into a roach/ling macro game.",
   strategy=[
     "Economy-first: heavy drone count, many hatcheries, creep spread for vision "
     "and speed.",
     "Converts economy into roach/hydra/ling and remaxes quickly after fights.",
     "Plays the macro game and wins on economy + trade efficiency.",
   ],
   strengths=[
     "Crushes Protoss in the sample (19-2) and is strong in the Zerg mirror (40-9).",
     "Fast remax — a lost fight rarely loses it the game.",
     "Deep, well-tuned macro from years of iteration.",
   ],
   weaknesses=[
     "Its weakest matchup is Terran (35-25) — siege tanks / mech / splash punish "
     "roach-ling and out-position it.",
     "Like most macro Zerg, vulnerable in the window before its economy pays off "
     "to a sharp timing.",
   ],
   beat=[
     "Terran: mech / bio-with-tanks and splash are the systemic answer — hold a "
     "position and let roach-ling break on siege lines.",
     "Hit an economic timing before its remax comes online rather than trading "
     "endlessly into a bigger economy.",
     "Deny creep spread to cut its vision and army speed.",
   ]),
 "Phobos": dict(
   summary="A strong **Terran bio** macro bot (marine/marauder/medivac with "
     "reaper opening and a starport). Standard, well-executed MMM into upgrades.",
   opening="Reaper-expand into 2-base bio; barracks-heavy with reactor/tech-lab, "
     "starport for medivacs.",
   strategy=[
     "Bio ball with stim/shield + combat upgrades; medivacs for mobility and drops.",
     "Reaper opening scouts and harasses; expands on a standard timing.",
     "Macro-oriented — trades bio efficiently and reinforces from home.",
   ],
   strengths=[
     "Balanced, no exploitable extreme; strong vs Zerg (33-20) and Protoss (28-15).",
     "Bio mobility + medivac drops apply constant pressure.",
   ],
   weaknesses=[
     "Bio without many tanks melts to splash — colossus, storm, banelings, "
     "lurkers.",
     "Slightly negative vs Terran mirrors in-sample; tank-count and positioning "
     "decide those.",
   ],
   beat=[
     "Force splash-favorable fights: colossus/storm (P), banelings/lurkers (Z), "
     "more tanks (T).",
     "Defend drops (turrets/keep-back units) so its medivac harass gets nothing.",
     "Don't fight stimmed bio in the open — use position and defender's advantage.",
   ]),
 "BenBotBC": dict(
   summary="A veteran **Terran** bot (Java, on the ladder since 2019) known for "
     "aggressive marine-based bio and micro. (Closed source — characterization "
     "from record + long-standing reputation.)",
   opening="Bio-oriented Terran; marine/marauder pressure with strong unit control.",
   strategy=[
     "Marine-centric bio with tight micro (splits, focus fire).",
     "Applies bio pressure and macros behind it.",
   ],
   strengths=[
     "Strong marine micro; punishes poor defensive positioning.",
     "Very strong vs Random (22-3) in-sample.",
   ],
   weaknesses=[
     "In the recent sample it struggles badly vs Protoss (12-53) and Zerg (2-24) "
     "— splash/colossus/storm and mass army out-trade its bio.",
     "Bio-heavy with limited splash of its own.",
   ],
   beat=[
     "Bring splash: colossus/storm (P), banelings/lurkers (Z) — the sample shows "
     "these dominate it right now.",
     "Hold defensive positions; don't get caught out of position by marine micro.",
   ]),
 "Zozo": dict(
   summary="A strong **Protoss** macro bot. (Closed source and no build captured "
     "this sample — characterization from race + record.)",
   strategy=[
     "Gateway-based Protoss macro; expands and builds a mixed gateway/robo army "
     "with upgrades (typical of a bot at this rating).",
   ],
   strengths=[
     "Well-rounded record; strong vs Zerg (35-17) and Terran (40-19) in-sample.",
   ],
   weaknesses=[
     "Roughly even vs Protoss (12-13) — the mirror comes down to execution.",
     "Build not observed here; scout it directly before committing.",
   ],
   beat=[
     "Standard anti-Protoss: match upgrades, force splash-favorable fights, don't "
     "attack into a defended position.",
     "Scout its tech (robo vs stargate vs templar) and prepare the specific answer.",
   ]),
 "Xena": dict(
   summary="A strong **Random** bot (C++). Plays all three races (its XenaP / "
     "XenaT / XenaZ variants each specialize), so the race is unknown until you "
     "scout. (Closed source — characterization from record + variant family.)",
   strategy=[
     "Race is random each game — must be scouted. Each race plays a solid macro "
     "game tuned by its dedicated variant.",
   ],
   strengths=[
     "Unpredictable race choice denies pre-game preparation.",
     "Strong all-around, especially vs Zerg (49-26).",
   ],
   weaknesses=[
     "As a generalist, each race line is a notch less specialized than a "
     "dedicated single-race bot.",
   ],
   beat=[
     "Scout the race immediately and apply the standard counter for that matchup.",
     "Play safe early until the race and build are known.",
   ]),
 "MicroMachine": dict(
   summary="A famous **marine-micro specialist** (Terran, C++). Its whole "
     "identity is *unit control*: it splits, kites, and focus-fires marines to "
     "win fights it should lose on paper. Dominant vs Terran in-sample (135-1).",
   opening="Marine-heavy bio; prioritizes army control over economy/tech.",
   strategy=[
     "Elite marine micro — stutter-step kiting and splits that beat larger or "
     "splashier armies through control alone (the micro-multiplies-army principle).",
     "Leans on winning engagements rather than out-macroing.",
   ],
   strengths=[
     "Best marine control on the ladder — wins fights massively outnumbered.",
     "Crushes other bio/Terran bots that can't match its control.",
   ],
   weaknesses=[
     "Economy/macro is secondary — a greedy macro opponent can out-produce it.",
     "Struggles vs Protoss (2-5) — colossus/storm/immortal splash and gateway "
     "mass blunt marine micro.",
     "Heavy splash (banelings, tanks, storm, colossus) is the hard counter.",
   ],
   beat=[
     "Never fight marines head-on in the open. Bring splash — banelings (Z), "
     "storm/colossus (P), tanks/mines (T).",
     "Out-macro it: it under-invests in economy, so a bigger army eventually "
     "overwhelms even perfect micro.",
     "Use air / cliff harass it can't micro against efficiently.",
   ]),
 "ArgoBot": dict(
   summary="A **cannon-turtle skytoss** Protoss: forge/cannons + shield batteries "
     "for a fortress economy, teching to **tempests** (and stargate air) to win "
     "from range. Patient, defensive, economy-heavy.",
   opening="Forge/cannon defensive opening; fast Nexus economy behind static "
     "defense, into Stargate + Tempest.",
   strategy=[
     "Turtle behind photon cannons + batteries, take a greedy economy, and tech "
     "to tempests that out-range everything.",
     "Wins the late game on economy + tempest range; avoids early fights.",
   ],
   strengths=[
     "Very hard to attack head-on (cannon/battery fortress) — strong, safe "
     "economy; good all-around record (90-32 sample).",
     "Tempests out-range most compositions and pick apart slow armies.",
   ],
   weaknesses=[
     "Immobile and slow — cedes map control; weak to early aggression before "
     "tempests are online (the tech window).",
     "Anti-air (vikings, corruptors, mass air) and mobility beat a static skytoss.",
   ],
   beat=[
     "Punish the tech window with a timing before tempests arrive — don't give it "
     "a free late game.",
     "Don't attack into the cannons; out-expand and take the map, then bring "
     "anti-air (vikings/corruptors) for the tempests.",
     "Multi-prong its immobile defense.",
   ]),
 "GPT": dict(
   summary="A **Terran bio-tank** macro bot (marine/marauder + siege tanks). "
     "Solid mech-flavored bio that grinds positional games.",
   opening="Bio into tanks off 2-3 bases; reactor/tech-lab barracks, factory for "
     "tanks, engineering-bay upgrades.",
   strategy=[
     "Marine/marauder backed by siege tanks — a positional, splash-heavy Terran.",
     "Macro-oriented, trades with tank support and upgrades.",
   ],
   strengths=[
     "Tank support makes it splash-resistant vs mass light; strong vs Zerg (24-10).",
   ],
   weaknesses=[
     "Weak vs Terran in-sample (18-34) — loses the mech/tank mirror on positioning.",
     "Tanks are immobile; multi-pronged pressure and drops stretch it.",
   ],
   beat=[
     "Don't run mass light into sieged tanks — flank, drop, or out-position.",
     "In the Terran mirror, win the tank count and high ground.",
     "Air (that it can't easily answer) and multi-prong exploit tank immobility.",
   ]),
 "SharpenedEdge": dict(
   summary="An established **Protoss** macro bot that dominates Random (27-1) and "
     "Protoss (29-7) but has a clear Terran problem. (Closed source — build not "
     "captured; from record + reputation.)",
   strategy=[
     "Gateway/robo/templar Protoss macro with upgrades and a deathball mid-game.",
   ],
   strengths=[
     "Excellent vs Protoss and Random; strong, disciplined macro.",
   ],
   weaknesses=[
     "Its glaring weakness is Terran (35-43) — bio-tank / mech splash and drops "
     "give it trouble.",
   ],
   beat=[
     "As Terran, bring tanks + drops and out-position the deathball; the record "
     "says Terran is the counter.",
     "Force splash-favorable, multi-front fights rather than one big engagement.",
   ]),
 "tito": dict(
   summary="A **macro Zerg** (C++): heavy drone economy, creep spread, into "
     "roach/ling with queens. Economy-first Zerg.",
   opening="Hatch-first economic Zerg; fast drones + creep, roach warren, "
     "queens for injects/defense.",
   strategy=[
     "Drone hard, spread creep, remax roach/ling; play the long macro game.",
   ],
   strengths=[
     "Strong economy; good vs Protoss (32-15) and Terran (19-3) in-sample.",
   ],
   weaknesses=[
     "Surprisingly weak in the Zerg mirror (15-26) — loses to more aggressive "
     "speedling/roach timings.",
     "Standard macro-Zerg vulnerability to splash and to sharp timings pre-remax.",
   ],
   beat=[
     "As Zerg, out-aggress it — speedling/roach pressure before its economy "
     "snowballs (the mirror record shows aggression works).",
     "As T/P, bring splash and hit a timing before it remaxes.",
   ]),
 "who": dict(
   summary="A **Random cheese/all-in specialist** (open source). It carries a big "
     "library of aggressive openings across all three races — worker rushes, "
     "proxy marine/marauder/reaper, thor drops — plus race-specific macro builds. "
     "Unpredictable and punishing.",
   opening="Varies wildly: worker rush, proxy 2-rax marauder/marine, proxy reaper "
     "with planetary, thor drop, or a standard race build — chosen per game.",
   strategy=[
     "Race is random AND the opening is often an all-in/proxy — double "
     "unpredictability (its `openings/` folder includes worker_rush, "
     "proxy_marauder, proxy_marine, proxy_reaper_with_pf, thor_drop).",
     "Dedicated combat modules for reaper harass, mine drops, cyclone, and "
     "battlecruisers if it reaches a macro game.",
     "Bets on ending the game early before the opponent stabilizes.",
   ],
   strengths=[
     "Extremely hard to prepare for — random race + proxy/all-in library.",
     "Punishes greedy or slow openings hard (strong 81-38 sample).",
   ],
   weaknesses=[
     "Most of its openings are all-ins — if the cheese is scouted and held, it "
     "has little economy to fall back on.",
     "A prepared, safe defender beats it consistently.",
   ],
   beat=[
     "Scout early and everywhere (worker-rush/proxy tells: missing workers, "
     "buildings near your base).",
     "Wall, pull workers, add static defense, and simply survive the all-in — its "
     "economy is spent once it's held.",
     "Then punish: a held cheese leaves it far behind.",
   ]),
 "Caninana": dict(
   summary="A **micro-heavy macro Zerg** (C++, the MicroCaninana/Caninana "
     "family). Strong economy with well-controlled roach/ling/hydra. Especially "
     "strong vs Protoss (47-21). (Closed source — from record + family reputation.)",
   strategy=[
     "Macro Zerg with good unit control; roach/ling/hydra with creep and remax.",
   ],
   strengths=[
     "Dominant vs Protoss (47-21); solid economy + micro.",
   ],
   weaknesses=[
     "Weaker vs Terran (20-17, near-even) — tank/mech splash is the usual answer.",
     "Standard macro-Zerg timing vulnerability.",
   ],
   beat=[
     "Terran splash (tanks/mech) and defensive positioning.",
     "Hit a timing before its economy + remax take over; deny creep.",
   ]),
 "smallBly": dict(
   summary="A **Zerg** bot, mid-pack recent form (63-77 sample). (Closed source, "
     "no build captured — characterization from race + record.)",
   strategy=[
     "Zerg macro/aggression (exact build not observed this sample — scout it).",
   ],
   strengths=[
     "Competitive vs Zerg (27-19) in-sample.",
   ],
   weaknesses=[
     "Struggles vs Protoss (13-25) in the recent sample.",
   ],
   beat=[
     "As Protoss, the sample says you're favored — standard anti-Zerg splash + "
     "macro.",
     "Scout the build directly; treat as a standard macro/aggro Zerg until seen.",
   ]),
 "DominionDog": dict(
   summary="A long-standing **Terran bio** bot (Java). Marine/marauder/medivac "
     "macro with drops. (Closed source — from record + reputation.)",
   strategy=[
     "Standard MMM bio with medivac drops and upgrades; macro-oriented.",
   ],
   strengths=[
     "Solid all-around Terran; even-to-favorable across matchups (74-51 sample).",
   ],
   weaknesses=[
     "Bio-centric — splash (colossus/storm/banelings/lurkers) is the answer.",
   ],
   beat=[
     "Force splash-favorable fights and defend drops.",
     "Don't fight stimmed bio in the open; use position.",
   ]),
 "chito": dict(
   summary="A strong **speedling macro Zerg** (C++): mass zerglings backed by a "
     "big drone economy and creep, with melee upgrades. Excellent record (113-34), "
     "crushing Protoss (36-7) and the Zerg mirror (40-11).",
   opening="Fast pool + speed into a drone/ling macro; expands wide, +melee "
     "upgrades and evolution chambers.",
   strategy=[
     "Mass speedling flood off a strong economy — like a stronger, better-macro'd "
     "12PoolBot: it drones more and adds +melee/creep.",
     "Overwhelms with ling numbers + upgrades and remaxes fast.",
   ],
   strengths=[
     "Dominant vs Protoss (gateway armies get swarmed) and Zerg; very strong "
     "overall.",
     "Efficient economy-to-ling conversion + upgrades that compound.",
   ],
   weaknesses=[
     "Zerglings are light/melee — splash (tanks, hellions, colossus, storm, "
     "banelings) is the structural counter; weaker vs Terran (21-13).",
     "A wall + defensive position neutralizes the flood at the choke.",
   ],
   beat=[
     "Get splash online before the flood: tanks + hellions (T), colossus/storm "
     "(P), banelings (Z).",
     "Wall and hold — don't fight speedlings in the open; let them break on "
     "static defense.",
     "Keep pace on armor upgrades so the ling trade stays bad, then punish its "
     "economy once the flood is spent.",
   ]),
 "VeTerran-revived": dict(
   summary="A revived version of the well-known **VeTerran** — a solid macro "
     "**Terran** (C++) that mixes bio and mech and out-macros opponents. Strong "
     "vs Zerg (43-18). (Closed source — from record + reputation.)",
   strategy=[
     "Balanced Terran macro: bio + tanks/mech with upgrades; expands and trades "
     "efficiently with tank support.",
   ],
   strengths=[
     "Very strong vs Zerg (43-18) — tanks + splash punish roach/ling.",
     "Disciplined macro and positional play.",
   ],
   weaknesses=[
     "Even-ish vs Protoss (19-14) and Terran (28-18) — immobile mech elements can "
     "be out-maneuvered.",
   ],
   beat=[
     "Exploit mech immobility with drops, air, and multi-pronged pressure.",
     "As Protoss, splash + tempest/colossus range; don't run into sieged tanks.",
   ]),
 "WickedBot": dict(
   summary="A **Terran bio** bot (marine/medivac + engineering-bay upgrades, "
     "bunker defense). Standard MMM macro.",
   opening="Bio expand with early bunker; marine/medivac into upgrades, factory "
     "for support.",
   strategy=[
     "Marine + medivac bio with upgrades; bunker-safe expansion into a macro game.",
   ],
   strengths=[
     "Competitive vs Zerg (28-21) and Protoss (17-13); safe bunkered openings.",
   ],
   weaknesses=[
     "Weak vs Terran (10-25) — loses the mirror on tanks/positioning.",
     "Bio-heavy — light on splash; melts to colossus/storm/banelings.",
   ],
   beat=[
     "As Terran, get more tanks and better position — the mirror favors you.",
     "Bring splash (P/Z); defend drops; hold defensive ground.",
   ]),
 "TyrP": dict(
   summary="A **Protoss** bot (the Tyr family, .NET). Gateway-based macro. Weak "
     "vs Terran in-sample (32-48). (Closed source — from record + family.)",
   strategy=[
     "Gateway/robo Protoss macro (typical for the family); expands into a mixed "
     "army with upgrades.",
   ],
   strengths=[
     "Undefeated vs Random (18-0) and favorable vs Protoss (14-7) in-sample.",
   ],
   weaknesses=[
     "Clear Terran weakness (32-48) — bio-tank + drops out-trade it.",
   ],
   beat=[
     "As Terran, the record says you're favored — tanks, drops, splash, position.",
     "Scout its tech and prepare the specific answer (immortal vs your armored, "
     "etc.).",
   ]),
 "WoundMaker": dict(
   summary="A **mutalisk/spire Zerg**: drone economy into fast Spire and "
     "mutalisks (with roach support). Strong record (112-36), demolishing Protoss "
     "(42-5) with muta harass.",
   opening="Economic Zerg into fast Lair + Spire; mutalisks for harass, roach for "
     "ground support.",
   strategy=[
     "Muta harass on worker lines and anything without anti-air, dodging the main "
     "army; roaches hold the ground.",
     "Uses mutalisk mobility to attack the economy leg and pick off stragglers.",
   ],
   strengths=[
     "Mutalisk harass is devastating vs bots with weak anti-air — crushes Protoss "
     "(42-5).",
     "Mobility + economy; hard to pin down.",
   ],
   weaknesses=[
     "Anti-air hard-counters it: thors, turrets/spores, vikings, mass queens, "
     "phoenix.",
     "If the muta harass is neutralized, its ground army is relatively thin.",
   ],
   beat=[
     "Anti-air BEFORE the mutas pop (read the Spire): turrets/spores over worker "
     "lines, thors/vikings/phoenix, keep marines/queens home.",
     "Then push the muta-thinned ground while the mutas are off harassing.",
     "Don't chase mutas around the map with your main army.",
   ]),
 "Roro": dict(
   summary="A **Terran** bot, mid-pack recent form (69-74). (Closed source, no "
     "build captured — from race + record.)",
   strategy=[
     "Terran macro (bio or mech — not observed this sample; scout it).",
   ],
   strengths=[
     "Competitive vs Protoss (40-31) in-sample.",
   ],
   weaknesses=[
     "Weak vs Terran (11-22) and Zerg (17-19) recently.",
   ],
   beat=[
     "Scout its bio-vs-mech choice and apply the standard Terran counter.",
     "Splash + position; exploit whichever immobility its composition has.",
   ]),
 "PhantomBot": dict(
   summary="A **Zerg** bot in a rough recent stretch (56-84). (Closed source, no "
     "build captured — from race + record.)",
   strategy=[
     "Macro/aggressive Zerg (exact build not observed — scout it).",
   ],
   strengths=[
     "Most competitive in the Zerg mirror (38-33).",
   ],
   weaknesses=[
     "Struggling across the board recently — vs Terran (5-17), Protoss (8-20), "
     "Random (5-14).",
   ],
   beat=[
     "Standard anti-Zerg: splash + macro; the sample says most matchups favor you.",
     "Scout and punish — it appears to be losing its openings currently.",
   ]),
 "BotTato": dict(
   summary="A **Terran mech/reaper** bot: reaper + KD8-charge harass into siege "
     "tanks and factory tech. Positional mech.",
   opening="Reaper opening with KD8 charges (worker harass), into command centers "
     "+ factory/siege tanks — a mech-leaning macro.",
   strategy=[
     "Reaper harass early (KD8 charges snipe workers), then siege tanks + mech for "
     "a positional mid-game.",
   ],
   strengths=[
     "Reaper harass pressures economies; tanks give splash and hold ground.",
   ],
   weaknesses=[
     "Rough recent form (38-75) — weak vs Zerg (4-23): mass ling/roach + flanks "
     "beat slow mech.",
     "Mech immobility — drops and multi-prong stretch it.",
   ],
   beat=[
     "As Zerg, swarm and flank the immobile mech (sample: 23-4 for Zerg).",
     "Defend the reaper harass (keep-back units), then exploit tank immobility.",
   ]),
 "sharkbot": dict(
   summary="A **Protoss** bot (.NET) that is strong vs Protoss (22-5) and Zerg. "
     "(Closed source — from record + reputation.)",
   strategy=[
     "Gateway/robo Protoss macro with upgrades and a solid deathball.",
   ],
   strengths=[
     "Dominant in the Protoss mirror (22-5); strong vs Zerg (11-4).",
   ],
   weaknesses=[
     "Even vs Terran (41-39) — the tank/drop matchup is its closest.",
   ],
   beat=[
     "As Terran, bio-tank + drops; don't attack the deathball head-on.",
     "Match upgrades and force splash-favorable, multi-front fights.",
   ]),
 "whalemean": dict(
   summary="A **Random** bot (.NET), mid-pack recent form (61-82). Race varies "
     "per game. (Closed source — from record.)",
   strategy=[
     "Random race each game — scout to learn it. Plays a macro game per race.",
   ],
   strengths=[
     "Race unpredictability denies pre-game prep.",
   ],
   weaknesses=[
     "Generalist — each race line is less specialized; losing record recently.",
   ],
   beat=[
     "Scout the race immediately and apply the standard matchup counter.",
     "Play safe until race + build are known.",
   ]),
 "JimmyBotP": dict(
   summary="The Protoss variant of the **Jimmy** family: gateway/robo with "
     "stalker/immortal and oracle harass.",
   opening="Gateway expand into cyber/robo; stalker/immortal army with oracle "
     "harass off 2-3 bases.",
   strategy=[
     "Stalker/immortal core (immortals vs armored) with oracle worker harass.",
   ],
   strengths=[
     "Immortals hard-counter armored units; oracle pressures economies.",
   ],
   weaknesses=[
     "Losing recent form (60-78); vulnerable vs Zerg (27-37) — mass army swarms "
     "gateway/robo.",
     "Oracle/stalker army is light on splash.",
   ],
   beat=[
     "Anti-air for the oracle (don't feed it workers); then out-macro the "
     "gateway/robo army.",
     "As Zerg, mass army + splash; as Terran, tanks + position.",
   ]),
 "TyrT": dict(
   summary="The Terran variant of the **Tyr** family (.NET). Standard Terran "
     "macro. (Closed source — from record + family.)",
   strategy=[
     "Terran bio or mech macro (family standard); expands with upgrades.",
   ],
   strengths=[
     "Competitive across matchups; best vs Protoss (20-15) in-sample.",
   ],
   weaknesses=[
     "Weak vs Terran (16-30) — loses the mirror.",
   ],
   beat=[
     "In the Terran mirror the sample favors you — tank count + position.",
     "Bring splash (P/Z) and exploit any mech immobility.",
   ]),
 "LunaxVRR": dict(
   summary="A **skytoss / tempest** Protoss: photon cannons + stargate into "
     "tempests (very similar to ArgoBot). Turtle-to-air.",
   opening="Cannon/forge defensive opening + fast Nexus, into Stargate + Tempests.",
   strategy=[
     "Turtle behind cannons + batteries and tech to tempests that out-range the "
     "opponent; win late on economy + air.",
   ],
   strengths=[
     "Hard to attack head-on; tempests out-range most armies; strong vs Zerg "
     "(32-10).",
   ],
   weaknesses=[
     "Immobile; weak to early timings before tempests and to mass anti-air; "
     "negative vs Terran (12-20) and Protoss (14-22) in-sample.",
   ],
   beat=[
     "Punish the tech window before tempests; don't attack into cannons.",
     "Bring anti-air (vikings/corruptors) and out-maneuver the static defense.",
   ]),
 "WaterLeak": dict(
   summary="A **roach/ling (and baneling) macro Zerg**. Mixes roach-heavy and "
     "mass-ling/baneling styles off a drone economy.",
   opening="Economic Zerg; roach warren + spawning pool, baneling nest available "
     "— roach-ling-baneling macro.",
   strategy=[
     "Roach/ling core with banelings vs bio; drone economy + remax.",
   ],
   strengths=[
     "Strong vs Zerg (32-12); banelings give it splash vs light armies.",
   ],
   weaknesses=[
     "Weak vs Protoss (16-21) and Terran (12-20) in-sample — colossus/tanks "
     "out-range roaches.",
   ],
   beat=[
     "Out-range roaches (colossus, tanks, tempest) and keep splash for the "
     "ling/bane.",
     "Hit a timing before its remax; deny creep.",
   ]),
 "JimmyBot": dict(
   summary="The **Random** member of the Jimmy family. In-sample it played Zerg "
     "(both a 100-zergling flood and a roach/creep macro), so expect a Zerg-heavy, "
     "variable game — but the race is random.",
   opening="Random race; observed Zerg lines ranged from a mass-ling all-in "
     "(100 lings) to a roach macro with creep.",
   strategy=[
     "Race and build vary — from aggressive ling floods to standard macro.",
   ],
   strengths=[
     "Unpredictable; the ling-flood branch can overwhelm the unprepared.",
   ],
   weaknesses=[
     "Losing recent form (71-74); weak vs Terran (12-28) — splash beats the ling "
     "branch.",
   ],
   beat=[
     "Scout the race and build; if it's the ling flood, wall + splash + hold.",
     "As Terran, tanks/hellions dominate its aggressive Zerg branch.",
   ]),
 "JimmyBotT": dict(
   summary="The Terran variant of the **Jimmy** family: bio + siege tanks + "
     "starport. Bio-tank-air macro.",
   opening="Bio into siege tanks and starport (tech-lab) — a mech-flavored bio "
     "macro.",
   strategy=[
     "Marine + siege tank + starport tech; positional Terran.",
   ],
   strengths=[
     "Tank support gives splash; competitive vs Zerg (38-20).",
   ],
   weaknesses=[
     "Losing recent form (68-71); weak vs Terran (10-26) and Protoss (14-21).",
   ],
   beat=[
     "Exploit tank immobility with drops/air/multi-prong.",
     "As Protoss, immortal/colossus + storm; as Terran, win the tank count.",
   ]),
}

# --- Batch 2 (Elo ranks ~33-64). Many are dev/"Test" variants of bots above,
# or currently in a losing/broken state — noted honestly per bot. ---
ANALYSIS.update({
 "MechaShark": dict(
   summary="A **Terran** bot (the mech-flavored member of the shark* family). "
     "Strong vs Zerg (21-10) but struggles vs Protoss (39-60). (Closed source, "
     "build not captured — from race + record.)",
   strategy=["Terran macro (bio and/or mech — not observed this sample; scout it)."],
   strengths=["Good vs Zerg (21-10) — tanks/mech splash punish roach/ling."],
   weaknesses=["Weak vs Protoss (39-60) and in the Terran mirror (5-11) in-sample."],
   beat=["As Protoss, the sample strongly favors you — immortals/colossus + storm; "
         "don't run into sieged mech.",
         "Exploit any mech immobility with drops/multi-prong."]),
 "ArgoTest": dict(
   summary="A development/test build of **ArgoBot** — same **cannon-turtle "
     "skytoss** (forge/cannons into stargate + tempests). Strong record (100-42), "
     "crushing Zerg (43-9). See the ArgoBot profile; play it the same way.",
   opening="Forge/cannon defensive opening + fast Nexus, into Stargate + Tempests.",
   strategy=["Turtle behind cannons/batteries, greedy economy, tech to tempests "
     "that out-range everything — identical plan to ArgoBot."],
   strengths=["Fortress defense + tempest range; dominant vs Zerg (43-9)."],
   weaknesses=["Immobile; weak to timings before tempests and to mass anti-air."],
   beat=["Punish the tech window before tempests; don't attack into cannons.",
         "Out-expand, then bring anti-air (vikings/corruptors) for the tempests."]),
 "Sharkling": dict(
   summary="A **Zerg** bot (shark* family), currently in a rough stretch (54-95). "
     "(Closed source, build not captured — from race + record.)",
   strategy=["Zerg macro/aggression (build not observed — scout it)."],
   strengths=["Most competitive in the Zerg mirror (23-38, still its best)."],
   weaknesses=["Losing across the board — especially vs Protoss (10-30)."],
   beat=["Standard anti-Zerg splash + macro; the sample says most matchups "
         "favor you. Scout and punish."]),
 "LunaxVRRTest": dict(
   summary="A test build of **LunaxVRR** — the same **skytoss** line (stargate "
     "into void rays / tempests, fleet beacon) behind cannons. See the LunaxVRR "
     "profile.",
   opening="Cannon/stargate into void ray + tempest air.",
   strategy=["Turtle-to-air: cannons + batteries, tech to void ray/tempest and "
     "win late on air + economy."],
   strengths=["Hard to attack head-on; strong vs Terran (28-12) in this sample."],
   weaknesses=["Immobile; weak to early pressure and mass anti-air."],
   beat=["Anti-air (vikings/corruptors) + hit the tech window; don't attack the "
     "cannons head-on."]),
 "JimmyBotZ": dict(
   summary="The **Zerg** member of the Jimmy family: drone economy into "
     "roach/ling with creep and spine defense — a standard macro Zerg.",
   opening="Hatch/pool economic opening into roach warren; drones + creep + queens.",
   strategy=["Roach/ling macro off a drone economy with creep spread and remax."],
   strengths=["Competitive vs Protoss (22-16); solid macro base."],
   weaknesses=["Losing form (73-75); weak vs Terran (14-26) — tanks/mech out-range "
     "roach-ling."],
   beat=["As Terran, tank/mech + splash; hit a timing before its remax.",
         "Deny creep to cut vision and speed."]),
 "ZeratulsRevengeTest": dict(
   summary="A **Protoss** zealot-based test/dev bot currently performing very "
     "poorly (15-105) — it loses almost every game in this sample, so treat it as "
     "an unstable work-in-progress rather than a ladder threat.",
   opening="Gateway zealot mass (25 zealots seen) — a zealot all-in/pressure that "
     "isn't currently working.",
   strategy=["Zealot-heavy gateway aggression; in its current state it fails to "
     "convert or defend."],
   strengths=["None reliable in the current sample — it is losing across all "
     "matchups."],
   weaknesses=["Broken/underperforming: 15-105, worst vs Protoss (7-44)."],
   beat=["Play straight up and macro — it is not defending or converting its "
     "zealot aggression right now."]),
 "Aeolus": dict(
   summary="A **stalker-based macro Protoss** that teches through Twilight "
     "Council (blink) into a gateway deathball. Even-ish across matchups.",
   opening="Gateway expand into cyber; stalker-heavy army (16+ stalkers) with "
     "Twilight Council (blink), forge upgrades.",
   strategy=["Stalker/blink core with upgrades; kite and out-position with blink.",
     "Macro-oriented — expands and grinds with a mobile stalker army."],
   strengths=["Blink stalkers are mobile and kite well; even vs Terran (28-28)."],
   weaknesses=["Stalker-heavy armies lack splash — mass light and heavy air/"
     "splash trouble it; weak vs Random (5-16).",
     "Losing overall form (63-78)."],
   beat=["Bring splash and mass (banelings/lings, storm/colossus, tanks) — "
     "stalker-only folds to it.",
     "Match blink micro or force fights where blink doesn't help (into a wall)."]),
 "zig-spudde": dict(
   summary="A **Terran bio-tank** bot (zig* family): marine + siege tank + "
     "liberator. Positional Terran.",
   opening="Bio into siege tanks + liberators; standard rax/factory macro.",
   strategy=["Marine/tank/liberator — a splash-heavy, positional Terran that "
     "trades with tank support."],
   strengths=["Tanks + liberators make frontal attacks costly; splash-resistant."],
   weaknesses=["Losing form (56-81); weak vs Terran (21-37) and Zerg (9-19) — "
     "immobility exploited by flanks/drops."],
   beat=["Don't run into sieged tanks/libs — flank, drop, out-position.",
     "Multi-prong to exploit mech immobility; win the tank count in the mirror."]),
 "Cyne": dict(
   summary="A **gateway/robo macro Protoss** currently underperforming (37-89). "
     "(A CynEX variant/relative — CynEX is the stronger current build.)",
   opening="Gateway expand into robo; stalker/zealot with robo support.",
   strategy=["Gateway/robo Protoss macro; in current form it is losing most "
     "matchups."],
   strengths=["Occasionally competitive but no reliable strength in this sample."],
   weaknesses=["Broadly losing (37-89), worst vs Protoss (8-27) and Zerg (7-23)."],
   beat=["Macro straight up; it is not converting its gateway/robo army well "
     "right now. Force splash-favorable fights."]),
 "LordSuperKing": dict(
   summary="A **Protoss** bot mixing stalkers with a Stargate/Fleet-Beacon tempest "
     "tech. Underperforming recently (47-71).",
   opening="Gateway/stalker into Stargate + tempest.",
   strategy=["Stalker army teching to tempests for range; a lighter skytoss."],
   strengths=["Tempest range if it survives to tech."],
   weaknesses=["Losing form; thin during the tempest tech window; stalker army "
     "lacks splash."],
   beat=["Pressure the tech window; bring anti-air for the tempests and splash "
     "for the stalkers."]),
 "AvocaDOS": dict(
   summary="A **Terran bio** bot (Avocado family): marine/marauder off many "
     "barracks. Even-ish form.",
   opening="Bio expand; marine/marauder with reactor/tech-lab barracks.",
   strategy=["Standard MMM bio macro with upgrades."],
   strengths=["Strong vs Protoss (23-11) in-sample."],
   weaknesses=["Weak vs Terran (7-30) — loses the mirror on tanks/position.",
     "Bio-heavy, light on splash."],
   beat=["In the Terran mirror, out-tank and out-position it (sample favors you).",
     "Bring splash (P/Z); defend drops."]),
 "Battler": dict(
   summary="A solid **Terran** bot with a reaper opening into bio/mech. Good "
     "record (83-54), strong vs Zerg (32-16) and Terran (14-8).",
   opening="Reaper opening (scout/harass) into a bio or mech macro with tanks.",
   strategy=["Reaper harass early, then a positional bio/tank macro.",
     "Trades efficiently with tank support and upgrades."],
   strengths=["Well-rounded; strong vs Zerg and in the Terran mirror.",
     "Reaper opening pressures economies."],
   weaknesses=["Closest matchup is Protoss (30-25) — colossus/storm out-splash "
     "its bio if it goes light."],
   beat=["As Protoss, splash (colossus/storm) + immortals; defend the reaper.",
     "Exploit any mech immobility with drops/multi-prong."]),
 "Apidae": dict(
   summary="A **cannon-turtle / cannon-rush Protoss** (Java). Forge + photon "
     "cannons for defense/aggression, teching behind. Even form (77-68).",
   opening="Forge-first into photon cannons (defensive rings or a cannon rush).",
   strategy=["Static cannon defense + tech; can turn a cannon rush into an "
     "opponent's base.",
     "Wins by shutting down aggression and out-teching behind cannons."],
   strengths=["Cannons punish frontal attacks and can end games early vs a bot "
     "that doesn't scout the rush."],
   weaknesses=["Immobile — cedes map and expansions; beaten by out-expanding.",
     "A scouted cannon rush that's denied leaves it behind."],
   beat=["Scout early for a cannon rush (probe/pylon near your base) and deny it.",
     "Don't attack into cannons — out-expand and out-macro the turtle; siege it "
     "from range (tanks/tempest)."]),
 "Clicadinha": dict(
   summary="A **macro Zerg** (the well-known Clicadinha): heavy drone economy "
     "into roach/queen with creep and spore defense. Roach-centric macro.",
   opening="Economic Zerg; drone-heavy into roach warren, queens, spore/spine "
     "defense, creep spread.",
   strategy=["Drone hard, defend with queens/spores, remax roach — a patient "
     "macro Zerg."],
   strengths=["Strong economy; grinds long games with roach remax."],
   weaknesses=["Losing form (58-79); weak vs Terran (15-34) — tanks/mech out-range "
     "roach.",
     "Roach without much splash struggles vs colossus/tanks."],
   beat=["Terran: tanks/mech + splash and out-range the roaches.",
     "Hit a timing before its economy + remax take over; deny creep."]),
 "Arpy": dict(
   summary="A **gateway-aggression Protoss**: zealot/adept off many gateways with "
     "phoenix support. Aggressive but currently losing (51-71).",
   opening="Gateway-heavy zealot/adept (7 gates, 23 zealots seen) with a phoenix.",
   strategy=["Gateway zealot/adept pressure into a macro game; phoenix for air/"
     "harass."],
   strengths=["Best vs Protoss (19-14); the zealot/adept flood can overwhelm the "
     "unprepared."],
   weaknesses=["Very weak vs Terran (5-21) — tanks/hellions shred the gateway "
     "army; also weak vs Zerg (18-31).",
     "Melee-heavy, light on splash."],
   beat=["As Terran, wall + tanks/hellions crush the zealot flood.",
     "As Zerg, splash (banelings) + mass; hold the aggression then out-macro."]),
 "muravevtest": dict(
   summary="A test build of **muravev** — a strong **speedling/macro Zerg** "
     "(drone + creep + ling with melee upgrades). Excellent record (89-31), "
     "crushing Terran (43-6). One of this tier's strongest.",
   opening="Fast pool/speed into drone + creep macro; ling with queens.",
   strategy=["Mass speedling off a big drone economy with heavy creep and "
     "upgrades; remax fast.",
     "Overwhelms with ling numbers + map control (creep)."],
   strengths=["Dominant vs Terran (43-6) and Protoss (29-8) in-sample — the ling "
     "flood + upgrades out-trades unprepared bio/gateway.",
     "Efficient economy-to-army conversion + creep control."],
   weaknesses=["Zerglings are light/melee — splash (tanks/hellions, colossus/"
     "storm, banelings) is the structural counter; weaker in the Zerg mirror "
     "(12-16)."],
   beat=["Splash before the flood: tanks+hellions (T), colossus/storm (P), "
     "banelings (Z).",
     "Wall and hold; deny creep; keep pace on armor upgrades then punish the "
     "economy."]),
 "BigDaddy": dict(
   summary="A **Terran bio** bot: mass marine/medivac off many barracks with a "
     "starport, into upgrades. Solid form (76-54).",
   opening="Bio expand; marine-heavy with medivacs, factory/starport support.",
   strategy=["Marine/medivac bio ball with stim + upgrades; drops for pressure."],
   strengths=["Good vs Zerg (28-17) and Protoss (27-15); strong marine count."],
   weaknesses=["Weak vs Terran (15-20); bio-heavy, light on tanks/splash."],
   beat=["Bring splash (banelings, colossus/storm) and defend drops.",
     "In the mirror, out-tank and out-position it."]),
 "norman": dict(
   summary="Currently **broken / badly underperforming** — 4-142 in the sample, "
     "losing essentially every game across all races. Ranked here on older Elo "
     "but not currently a functional threat. (Build not captured.)",
   strategy=["Not executing a coherent game in its current state."],
   strengths=["None in the current sample."],
   weaknesses=["Loses to everything right now (0-41 vs Terran, 4-70 vs Zerg)."],
   beat=["Macro straight up — a free win in its current state."]),
 "AvocaDEV": dict(
   summary="A development build of the **Avocado / AvocaDOS** Terran bio line — "
     "marine/marauder bio. Even form (64-69). See AvocaDOS.",
   opening="Bio (marine/marauder) macro — dev variant.",
   strategy=["Standard MMM bio; a work-in-progress version of the Avocado bots."],
   strengths=["Roughly even across matchups."],
   weaknesses=["Bio-heavy, light on splash; no standout matchup."],
   beat=["Splash + defend drops; out-tank in the mirror."]),
 "Mulebot": dict(
   summary="A **Terran bio-mech** bot (Python): marine + siege tank + hellion. "
     "Struggling recently (49-83), notably vs Random (1-14).",
   opening="Bio into siege tank + hellion; standard rax/factory.",
   strategy=["Marine/tank/hellion mix — positional Terran with some mech."],
   strengths=["Competitive in the Terran mirror (25-22)."],
   weaknesses=["Losing form; weak vs Protoss (11-25), Zerg (12-22), Random (1-14)."],
   beat=["Bring splash/mass and exploit mech immobility with drops/multi-prong.",
     "As Protoss, immortal/colossus; as Zerg, mass + flanks."]),
 "Dovahkiin": dict(
   summary="A **macro Zerg**, even-ish form (60-69). (Closed source, build not "
     "captured — from race + record.)",
   strategy=["Zerg macro (roach/ling/drone — build not observed; scout it)."],
   strengths=["Competitive vs Protoss (23-26) and Zerg (21-19)."],
   weaknesses=["Weak vs Terran (12-19) — tanks/mech splash punish it."],
   beat=["As Terran, tanks/mech + splash and hold position; hit a timing before "
     "its remax.",
     "Deny creep; out-range its army."]),
 "72Tortoises": dict(
   summary="A **macro Zerg** (the Zerg cousin of 27turtles/72-series): drone "
     "economy into roach/ling with creep. Solid form (77-63).",
   opening="Economic Zerg; drones + creep into roach/ling with queens.",
   strategy=["Drone macro into roach/ling remax; creep control and defense."],
   strengths=["Well-rounded; competitive vs Terran (27-20) and Zerg (30-23)."],
   weaknesses=["Roach/ling lacks splash — colossus/tanks out-range it; even vs "
     "Protoss (19-19)."],
   beat=["Out-range roaches (tanks/colossus/tempest) and keep splash for the ling.",
     "Hit a timing before remax; deny creep."]),
 "FlowerPrincess": dict(
   summary="A **ling-flood Zerg**: mass zerglings (60+) off a drone economy. "
     "Aggressive but currently losing (56-88).",
   opening="Fast pool into mass zergling + drones; ling flood with creep.",
   strategy=["Zergling flood to overwhelm early, drone economy behind if held."],
   strengths=["Best vs Terran (36-26) — the ling flood punishes un-walled bio.",
     "Early army value can overwhelm the unprepared."],
   weaknesses=["Weak vs Protoss (7-25) and Zerg (13-26) — splash (colossus/storm, "
     "banelings) shreds the flood.",
     "Melee into a wall stalls; thin tech."],
   beat=["Wall + splash (tanks/hellions, colossus/storm, banelings) and hold — "
     "don't fight lings in the open.",
     "Then punish its thin economy once the flood is spent."]),
 "Dodo": dict(
   summary="A **macro Zerg** with a **Nydus** twist: heavy drone economy (76 "
     "drones) into roach, using Nydus networks to reposition/attack. Losing form "
     "(50-94).",
   opening="Very economic Zerg (drone-heavy) into roach + Nydus network.",
   strategy=["Over-drones into a big economy, uses Nydus to move army or drop "
     "into bases; roach-centric."],
   strengths=["Huge economy potential; Nydus enables surprise attacks/defense."],
   weaknesses=["Over-drones with a thin army — a wide vulnerability window; weak "
     "vs Terran (24-40) and Protoss (13-23).",
     "Nydus is all-or-nothing; a killed Nydus wastes the investment."],
   beat=["Punish the over-drone window with a timing before its army/Nydus is "
     "ready.",
     "Keep vision for Nydus exits (kill the worm on sight); splash the roach."]),
 "CynEX": dict(
   summary="A strong **skytoss/stalker macro Protoss** (the current, stronger Cyne "
     "line): stalkers + Stargate air + cannons behind a good economy. 92-58, "
     "strong across the board.",
   opening="Gateway/stalker into Stargate (air) with cannon defense and cyber "
     "upgrades.",
   strategy=["Stalker core + Stargate air (void/phoenix) with static defense; "
     "macro into a mixed deathball.",
     "Balanced army with air support and upgrades."],
   strengths=["Strong all-round (vs P 30-19, Z 30-19, T 27-12); air + stalker "
     "flexibility.",
     "Cannons make it hard to punish early."],
   weaknesses=["Can be out-macroed if it over-invests in static defense; stalker "
     "core still light on splash."],
   beat=["Match upgrades and force splash-favorable fights; bring anti-air for "
     "the Stargate units.",
     "Don't attack into cannons — out-expand and take favorable trades."]),
 "PerilousProtossBot": dict(
   summary="A **Protoss** bot (zealot/cannon pressure) currently **badly "
     "underperforming** (15-121) — losing nearly every game, especially vs Zerg "
     "(2-60). Not a functional threat in its current state.",
   opening="Gateway zealot + photon cannon pressure (from prior observation).",
   strategy=["Zealot/cannon aggression that is not currently converting."],
   strengths=["None reliable in the current sample."],
   weaknesses=["Broadly losing (15-121); collapses vs Zerg mass army (2-60)."],
   beat=["Macro straight up; it is not defending or converting right now — a "
     "free win with basic safety."]),
 "Voltron": dict(
   summary="A **Terran bio-tank** bot (marine/marauder + tank + medivac + "
     "starport). Struggling recently (36-71).",
   opening="Bio into siege tanks + starport (medivac/support); positional Terran.",
   strategy=["Marine/tank/medivac — a splash-supported bio that trades positionally."],
   strengths=["Best vs Zerg (9-24 is poor though) — actually most competitive vs "
     "Protoss (21-22) in-sample; tanks give splash."],
   weaknesses=["Losing form; weak vs Zerg (9-24) and Terran (6-18) and Random (0-7)."],
   beat=["Exploit tank immobility (drops, flanks, air); out-macro it.",
     "As Zerg, mass + flanks overwhelm; as Terran, out-tank and out-position."]),
 "Forgefiend": dict(
   summary="A **cannon-turtle / cannon-rush Protoss**: forge + mass photon "
     "cannons (8+). Static, defensive/aggressive cannons. Losing form (53-81).",
   opening="Forge-first into mass photon cannons (turtle or cannon rush).",
   strategy=["Static cannon walls + tech; shuts down aggression, or rushes cannons "
     "into the opponent."],
   strengths=["Cannons punish frontal attacks; can end games early vs the "
     "unprepared."],
   weaknesses=["Immobile — cedes the map; weak vs Protoss (14-30) and Zerg (23-31).",
     "A denied cannon rush leaves it far behind."],
   beat=["Scout for a cannon rush and deny it; don't attack into cannons.",
     "Out-expand and siege from range (tanks/tempest); take the map."]),
 "Creepy_duo_canon": dict(
   summary="A **cannon-rush Protoss** (Creepy family): a two-pronged photon-cannon "
     "rush with zealot backup. It lives or dies on the rush — strong vs Terran "
     "(21-8) and Protoss (24-9) but crushed by Zerg (9-37).",
   opening="Proxy/double photon-cannon rush with forge and zealots.",
   strategy=["Rush cannons into the opponent's base/natural; if it connects, it "
     "can end the game early.",
     "Zealots support the cannons."],
   strengths=["Beats bots that don't scout the rush — strong vs Terran and Protoss.",
     "Can win outright before macro matters."],
   weaknesses=["Hard-countered by Zerg (9-37) — fast lings kill probes/cannons and "
     "the economy is too thin to recover.",
     "A scouted, denied rush loses on the spot."],
   beat=["Scout early (probe/pylon/cannon near your base) and kill the probe/"
     "pylon before cannons finish.",
     "As Zerg, fast lings crush it; as any race, deny the rush then punish the "
     "thin economy."]),
 "nida": dict(
   summary="A **gateway macro Protoss**: stalker/sentry with phoenix support and "
     "robo tech. Even-ish form (65-72).",
   opening="Gateway expand into cyber; stalker/sentry with phoenix, robo support.",
   strategy=["Stalker/sentry army (forcefields) with phoenix harass; macro into a "
     "mixed deathball."],
   strengths=["Competitive vs Protoss (26-21); sentries + phoenix give control "
     "and harass."],
   weaknesses=["Weak vs Terran (12-21); stalker/sentry light on splash."],
   beat=["As Terran, tanks/drops + splash; dodge/bait forcefields.",
     "Bring anti-air for phoenix; match upgrades."]),
 "clone": dict(
   summary="A **Terran** bot (reaper opening into starport tech). Even-to-losing "
     "form (61-72). (From the opponents pool; reaper/air-leaning.)",
   opening="Reaper opening (KD8) into starport tech; bio/air mix.",
   strategy=["Reaper harass early into a starport-based bio/air macro."],
   strengths=["Competitive in the Terran mirror (24-16)."],
   weaknesses=["Weak vs Random (4-11) and Zerg (15-27); light, harass-oriented."],
   beat=["Defend the reaper/air harass (turrets/keep-back units), then out-macro.",
     "Bring anti-air if it goes starport; splash its bio."]),
 "PiG_Bot": dict(
   summary="A **gateway/robo macro Protoss**: stalker/zealot with observer and "
     "robo tech, sometimes high templar, off three bases. Balanced deathball "
     "macro (67-71).",
   opening="Gateway expand into cyber/robo; stalker/zealot with observer, "
     "expanding to three bases.",
   strategy=["Gateway/robo deathball with upgrades and observer detection; macro "
     "into a strong mid-game army (adds templar/storm in longer games).",
     "Plays the game straight — no gimmick, wins on execution."],
   strengths=["Balanced army + economy; observer detection; even across matchups."],
   weaknesses=["No exploitable extreme; gateway/robo core can be out-splashed if "
     "it clumps, and out-macroed."],
   beat=["Match upgrades and force splash-favorable fights; keep tanks sieged so "
     "its deathball eats splash.",
     "Out-macro via cleaner production; take only favorable engagements."]),
})


def clean_build(pairs):
    return [(n, c) for n, c in pairs]


def race_line(byrace):
    order = ["T", "P", "Z", "R", "?"]
    cells = []
    for rc in order:
        if rc in byrace:
            w, l = byrace[rc]
            g = w + l
            if g:
                cells.append(f"| vs {RACE.get(rc, rc)} | {w}-{l} | {100*w//g}% |")
    return cells


def bot_md(name, e):
    m = e["meta"]; r = e["record"]
    a = ANALYSIS.get(name, {})
    L = []
    L.append(f"# {name}\n")
    L.append("*Objective scouting profile — the bot's own strategy, build, and "
             "record, independent of any particular opponent.*\n")
    if a.get("summary"):
        L.append("## Summary\n")
        L.append(a["summary"] + "\n")

    L.append("## Identity\n")
    L.append("| | |")
    L.append("|---|---|")
    L.append(f"| **Race** | {RACE.get(m['race'], m['race'])} |")
    L.append(f"| **Bot type** | {m['type']} |")
    L.append(f"| **AI Arena Elo** | ~{m['elo']} (top-tier ladder bot) |")
    L.append(f"| **On ladder since** | {m['created']} |")
    L.append(f"| **Last source update** | {m['updated']} |")
    CODE_READ = {"12PoolBot", "who"}  # bots whose source I actually read
    if name in CODE_READ:
        src = "yes — Python source read directly for this profile"
    elif m["pub"]:
        kind = "Python source" if m["type"] == "python" else "compiled/binary zip"
        src = f"yes ({kind} publicly downloadable; this profile is from replays + record)"
    else:
        src = "no (closed source; profiled from replays + record)"
    L.append(f"| **Source public** | {src} |")
    L.append("")

    if a.get("opening") or a.get("strategy"):
        L.append("## Strategy\n")
        if a.get("opening"):
            L.append(f"**Opening:** {a['opening']}\n")
        for s in a.get("strategy", []):
            L.append(f"- {s}")
        L.append("")

    # Record
    tot = r["W"] + r["L"]
    L.append("## Performance (recent ladder sample)\n")
    L.append(f"**Overall: {r['W']}–{r['L']} ({100*r['W']//max(1,tot)}%)** "
             f"over {tot} decided games"
             + (f" (+{r['draw']} draws/no-result)" if r["draw"] else "") + ".\n")
    rl = race_line(r["byrace"])
    if rl:
        L.append("| Matchup | Record | Win % |")
        L.append("|---|---|---|")
        L.extend(rl)
        L.append("")
    if e["tough"]:
        L.append("**Toughest opponents:** "
                 + ", ".join(f"{n} {w}-{l} ({rc})" for n, w, l, rc in e["tough"][:8]) + ".\n")
    if e["best"]:
        L.append("**Best matchups:** "
                 + ", ".join(f"{n} {w}-{l} ({rc})" for n, w, l, rc in e["best"][:8]) + ".\n")

    # Observed builds
    if e["builds"]:
        L.append("## Observed builds (from its own replays)\n")
        for b in e["builds"][:3]:
            bs = ", ".join(f"{n}×{c}" for n, c in clean_build(b["build"]))
            res = "won" if b["won"] else "lost"
            L.append(f"**vs {b['opp']} ({b['opp_race']}), {b['min']} min, {res}:** {bs}")
            if b["traj"]:
                L.append("")
                L.append("| min | its supply | opp supply | its army$ | opp army$ | its wk | opp wk |")
                L.append("|--:|--:|--:|--:|--:|--:|--:|")
                for t in b["traj"]:
                    L.append(f"| {t['m']} | {t['sup']:.0f} | {t['opp_sup']:.0f} | {t['army']} "
                             f"| {t['opp_army']} | {t['wk']} | {t['opp_wk']} |")
            L.append("")

    if a.get("strengths"):
        L.append("## Strengths\n")
        for s in a["strengths"]:
            L.append(f"- {s}")
        L.append("")
    if a.get("weaknesses"):
        L.append("## Weaknesses\n")
        for w in a["weaknesses"]:
            L.append(f"- {w}")
        L.append("")
    if a.get("beat"):
        L.append("## How to beat it\n")
        for i, s in enumerate(a["beat"], 1):
            L.append(f"{i}. {s}")
        L.append("")

    L.append("---")
    src = a.get("sources", "")
    L.append(f"*{src or 'Sources: AI Arena API (record + per-race + per-opponent over a recent match sample) and build orders extracted from this bot’s own replays. Closed-source: strategy inferred from observed builds and results.'}*")
    return "\n".join(L)


README_HEAD = """# AI Arena Bot Profiles

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
"""

STYLE = {
 "Deimos": "Macro Protoss, adept/phoenix harass", "Eris": "Macro Zerg (roach/ling)",
 "Phobos": "Terran bio (MMM)", "BenBotBC": "Terran bio, marine micro",
 "Zozo": "Macro Protoss", "Xena": "Random, adaptive macro",
 "MicroMachine": "Terran marine-micro specialist", "ArgoBot": "Skytoss (cannon+tempest)",
 "GPT": "Terran bio-tank", "SharpenedEdge": "Macro Protoss",
 "tito": "Macro Zerg", "who": "Random cheese/proxy specialist",
 "Caninana": "Micro macro Zerg", "smallBly": "Zerg",
 "DominionDog": "Terran bio", "chito": "Speedling macro Zerg",
 "VeTerran-revived": "Terran bio/mech macro", "WickedBot": "Terran bio",
 "TyrP": "Protoss macro", "WoundMaker": "Mutalisk Zerg",
 "Roro": "Terran", "PhantomBot": "Zerg",
 "BotTato": "Terran mech/reaper", "sharkbot": "Protoss macro",
 "whalemean": "Random", "JimmyBotP": "Protoss (stalker/immortal/oracle)",
 "TyrT": "Terran macro", "LunaxVRR": "Skytoss (cannon+tempest)",
 "WaterLeak": "Roach/ling Zerg", "JimmyBot": "Random (Zerg-leaning)",
 "JimmyBotT": "Terran bio-tank", "12PoolBot": "12-pool speedling macro Zerg",
}
STYLE.update({
 "MechaShark": "Terran macro (mech-leaning)", "ArgoTest": "Skytoss cannon+tempest (ArgoBot dev)",
 "Sharkling": "Zerg", "LunaxVRRTest": "Skytoss void/tempest (LunaxVRR dev)",
 "JimmyBotZ": "Roach/drone macro Zerg", "ZeratulsRevengeTest": "Protoss zealot (dev, unstable)",
 "Aeolus": "Stalker/blink macro Protoss", "zig-spudde": "Terran bio-tank",
 "Cyne": "Protoss gateway/robo (weak form)", "LordSuperKing": "Protoss stalker+tempest",
 "AvocaDOS": "Terran bio", "Battler": "Terran reaper bio/mech",
 "Apidae": "Protoss cannon turtle/rush", "Clicadinha": "Roach macro Zerg",
 "Arpy": "Protoss gateway zealot/adept", "muravevtest": "Speedling macro Zerg (muravev dev)",
 "BigDaddy": "Terran bio (marine/medivac)", "norman": "Broken/losing (current)",
 "AvocaDEV": "Terran bio (dev)", "Mulebot": "Terran bio-mech",
 "Dovahkiin": "Zerg macro", "72Tortoises": "Roach/ling macro Zerg",
 "FlowerPrincess": "Ling-flood Zerg", "Dodo": "Drone macro Zerg (Nydus)",
 "CynEX": "Skytoss/stalker macro Protoss", "PerilousProtossBot": "Protoss zealot/cannon (weak form)",
 "Voltron": "Terran bio-tank", "Forgefiend": "Protoss cannon turtle/rush",
 "Creepy_duo_canon": "Protoss double cannon rush", "nida": "Protoss gateway stalker/phoenix",
 "clone": "Terran reaper/starport", "PiG_Bot": "Protoss gateway/robo macro",
})


def _best_worst(byrace):
    best = worst = None
    bv, wv = -1, 2
    for rc, (w, l) in byrace.items():
        g = w + l
        if g < 4 or rc == "?":
            continue
        pct = w / g
        if pct > bv:
            bv, best = pct, rc
        if pct < wv:
            wv, worst = pct, rc
    return (best or "-"), (worst or "-")


def readme():
    rows = sorted(DATA.items(), key=lambda kv: -kv[1]["meta"]["elo"])
    out = [README_HEAD.rstrip("\n")]
    for i, (name, e) in enumerate(rows, 1):
        m = e["meta"]
        best, worst = _best_worst(e["record"]["byrace"])
        out.append(f"| {i} | [{name}]({name.replace('/', '_')}/PROFILE.md) | "
                   f"{m['race']} | {m['elo']} | {STYLE.get(name, '')} | {best} | "
                   f"{worst} | {'yes' if m['pub'] else ''} |")
    out.append("\n*Best/Worst vs = the race this bot has the highest / lowest "
               "win-rate against in the sample. Regenerate with "
               "`python bot_profiles/_generate_objective.py`.*")
    return "\n".join(out)


def main():
    n = 0
    for name, e in DATA.items():
        if name == "12PoolBot":
            continue  # bespoke code-read profile, hand-maintained
        d = os.path.join(HERE, name.replace("/", "_"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "PROFILE.md"), "w") as f:
            f.write(bot_md(name, e))
        n += 1
    with open(os.path.join(HERE, "README.md"), "w") as f:
        f.write(readme())
    print(f"wrote {n} objective profiles + README.md")


if __name__ == "__main__":
    main()
