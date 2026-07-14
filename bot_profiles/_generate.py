#!/usr/bin/env python3
"""Generate bot_profiles/<bot>/PROFILE.md from data/profile_data.json.

Data was pulled from the AI Arena API (GriffinBot id 1187 match history) and
the opponent build orders were extracted from replay tracker events with
s2protocol (see analysis/aa_analyze.py / harness/analyze_replays.py for the
same machinery). This script is the single source of truth for the per-bot
files so they can be regenerated when new games are played.

    python bot_profiles/_generate.py
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data", "profile_data.json")))

# Units that are AI-Arena arena-client control markers, not real game units.
NOISE = {f"Beacon{s}" for s in ("Army", "Defend", "Attack", "Harass", "Idle",
         "Auto", "Detect", "Scout", "Claim", "Expand", "Rally", "Custom01",
         "Custom02", "Custom03", "Custom04")}
WORKERS = {"SCV", "Drone", "Probe"}
SUPPLY = {"SupplyDepot", "Pylon", "Overlord"}

# ---------------------------------------------------------------------------
# Archetype library. Each entry is grounded in STRATEGY.md's economy-army
# spectrum + the two lenses in PRINCIPLES.md. `counter` is written from
# GriffinBot's point of view (a slow-but-safe Terran bio/tank macro bot).
# ---------------------------------------------------------------------------
ARCH = {
 "p_gate_allin": {
   "label": "Protoss one-base gateway all-in (zealot/stalker flood)",
   "spectrum": "ALL-IN / CHEESE — no economy, all army, hits ~7-9 min",
   "summary": "Pumps zealots (and/or stalkers) out of 4-6 gateways on one or "
     "two bases and a-moves the flood into our natural before our tanks and "
     "bio are online. Army value is 3-15x ours at the 8-minute mark.",
   "strengths": ["Overwhelming army supply at 7-9 min — the exact window our "
     "fixed macro opening is weakest.", "Warp-in reinforcements arrive on the "
     "front, so a broken first engagement is immediately re-flooded.",
     "Zealots trade efficiently into un-sieged bio caught in the open."],
   "weaknesses": ["No economy behind it — if the first flood is held, its "
     "bank is empty and it never takes a real third.", "Zealots are melee: a "
     "walled ramp + a couple of sieged tanks + a bunker shreds them.",
     "Zero tech answer to air or splash; the all-in is the whole plan."],
   "counter": "Treat as CHEESE (STRATEGY.md #1): survive, don't out-trade. "
     "Wall the ramp, pull SCVs, get a bunker + 1-2 tanks sieged behind the "
     "wall and hold the choke with defender's advantage (RULES 7/9a). Do NOT "
     "move out — GriffinBot's army-wipe losses come from committing into the "
     "flood. If we hold to ~10 min their economy is dead and we win by "
     "simply expanding.",
 },
 "p_gate_pressure": {
   "label": "Protoss two-base gateway pressure (adept/stalker/zealot)",
   "spectrum": "TIMING ATTACK — light economy, pressures then expands",
   "summary": "Gateway army (often adept/stalker with a sentry or two) applies "
     "early pressure off two bases, then transitions to a macro deathball if "
     "the pressure is contained.",
   "strengths": ["Adept/stalker pressure can snipe workers and pin us at home "
     "while it expands behind (harassment lens, PRINCIPLES.md).",
     "More economy than a pure all-in, so it doesn't auto-lose if contained."],
   "weaknesses": ["Commits enough to army that a clean hold leaves it behind on "
     "economy.", "Gateway-only army melts to sieged tanks + upgraded bio once "
     "we stabilize.", "Rarely has detection or an air answer early."],
   "counter": "Hold the first pressure at the wall (defender's advantage), keep "
     "tanks sieged, then punish the window: it over-invested in army, so once "
     "the pressure is spent we out-macro it. Match upgrades — an upgraded bio "
     "ball beats raw gateway units (PRINCIPLES 'upgrades compound').",
 },
 "p_robo_timing": {
   "label": "Protoss robo / immortal timing",
   "spectrum": "TIMING ATTACK — two-base immortal push",
   "summary": "Gateway + Robotics into an immortal-backed timing (immortal/"
     "stalker/zealot, sometimes an observer). The immortals give it a heavy "
     "front-line that out-trades our early bio.",
   "strengths": ["Immortals hard-counter our marauders and shrug off tank "
     "shots with barrier — a real composition edge (PRINCIPLES #8).",
     "Observer gives it detection and vision our stalker-less openings lack."],
   "weaknesses": ["Robo tech delays economy — it is on two bases and thin if "
     "the timing is held.", "Immortals are slow; sieged tanks + a wall let us "
     "concentrate fire and split.", "Light on anti-air."],
   "counter": "Defend the immortal timing at the choke with sieged tanks (splash "
     "ignores the barrier's HP pool) and focus the immortals down. Don't fight "
     "it in the open. After it's held, its robo-delayed economy is behind — "
     "expand and grind with upgrades.",
 },
 "p_air_tech": {
   "label": "Protoss stargate / skytoss (void ray / tempest / oracle / phoenix)",
   "spectrum": "GREEDY / TECH — trades early tempo for a strong air late-game",
   "summary": "Rushes Stargate tech for oracles (harass), void rays, phoenixes, "
     "or tempests. Bets on an air composition we have no scouted answer to.",
   "strengths": ["Air units bypass our ground wall entirely — oracles snipe "
     "workers, tempests out-range everything (harassment + tech lenses).",
     "If we never build anti-air we simply lose to a tech we could have "
     "scouted (STRATEGY.md 'cloak/air need a specific answer')."],
   "weaknesses": ["Stargate tech is slow and gas-heavy — very thin on the "
     "ground during the tech window.", "A bio timing before the air mass "
     "arrives punishes the greed.", "Turrets/vikings/thors hard-counter it."],
   "counter": "Scout the Stargate and REACT (STRATEGY.md 'read the tech "
     "building, not the unit'): add engineering-bay turrets over the worker "
     "line and vikings/thors before the air lands. Or hit the two-base tech "
     "window with a bio timing before it spikes. Anti-air BEFORE it arrives, "
     "not after.",
 },
 "p_cannon_turtle": {
   "label": "Protoss forge / photon-cannon turtle",
   "spectrum": "TURTLE — static defense + tech behind cannons",
   "summary": "Forge-first into rings of photon cannons, teching behind the "
     "static defense toward a stronger army. Sometimes a cannon-rush variant.",
   "strengths": ["Cannons make a frontal bio attack very inefficient — attacking "
     "into static defense is the classic mistake (STRATEGY.md #5).",
     "Buys time to reach a powerful late-game composition."],
   "weaknesses": ["Cannons don't take map — it cedes the whole map and every "
     "expansion.", "Immobile: it can't defend a fourth/fifth or punish our "
     "greed.", "Falls behind on economy if we simply out-expand."],
   "counter": "Do NOT attack into the cannons. Take the map — out-expand it "
     "(PRINCIPLES 'time is on the side of whoever has more bases'), out-upgrade, "
     "and either hit before its key tech or tech to a siege composition "
     "(tanks/liberators) that out-ranges the cannon line.",
 },
 "p_macro": {
   "label": "Protoss standard macro / gateway-robo deathball",
   "spectrum": "STANDARD MACRO — balanced expand + army",
   "summary": "Plays the game straight: expands on a normal timing, builds a "
     "gateway/robo/templar deathball with upgrades. Wins on execution, not a "
     "gimmick.",
   "strengths": ["No free window to punish — it keeps army and economy "
     "balanced.", "Storm/colossus/immortal deathballs out-trade unupgraded "
     "bio in a straight fight."],
   "weaknesses": ["Slower to a critical mass than an all-in — vulnerable to a "
     "bio+tank timing.", "Bot deathball control is usually poor: it clumps "
     "(splash-vulnerable) and mis-engages."],
   "counter": "Out-macro and out-micro (STRATEGY.md #3). Match upgrades, keep "
     "tanks sieged so its clumped deathball eats splash, and take a favorable "
     "engagement only — never a coin-flip in the open.",
 },
 "z_ling_flood": {
   "label": "Zerg mass-zergling flood / ling all-in",
   "spectrum": "ALL-IN / AGGRESSION — early ling flood off 2-3 hatch",
   "summary": "Saturates larva into zerglings (40-120 by 8 min) and floods our "
     "natural, sometimes with a drone economy behind if the flood is held.",
   "strengths": ["Enormous early army value — 2-3x ours at 4-5 min before we "
     "have a wall or tanks.", "Speed lets it flank, run by into the worker "
     "line, and re-flood instantly from a nearby hatch."],
   "weaknesses": ["Zerglings evaporate to any splash — one sieged tank or a "
     "handful of hellions is a hard counter (PRINCIPLES #8/#9).",
     "If the flood is held its economy is thin and it has no tech.",
     "Melee into a wall = it can't connect."],
   "counter": "Wall the natural and get splash online FAST: hold with a bunker "
     "and a sieged tank / hellions behind the wall (defender's advantage). Do "
     "not fight lings in the open. Hold the flood → its larva went to dead "
     "lings, not drones → we win on economy. (Our 1-1 vs Crawler is exactly "
     "this: the game we held, its army collapsed to nothing by 12 min.)",
 },
 "z_macro_drone": {
   "label": "Zerg mass-drone macro (into roach / hydra / queen)",
   "spectrum": "GREEDY / ECONOMIC — over-drones, out-econs, then remaxes",
   "summary": "Drones hard (70-100 drones, 4-5 hatch), spreads creep, and "
     "converts a huge economy into wave after wave of roach/hydra/ling. It "
     "simply out-produces our slow macro and remaxes faster after every fight.",
   "strengths": ["Biggest economy on the ladder — reaches 150+ supply and 75+ "
     "workers while we're at ~100/50 (this is where most of our macro losses "
     "come from).", "Remax speed: a Zerg economy refills supply after a lost "
     "fight far faster than ours — losing one trade to it loses the game.",
     "Creep gives it map vision and unit speed."],
   "weaknesses": ["Over-drones — there is a wide window where it has a huge "
     "worker count and a thin army (STRATEGY.md #4 'lots of bases + few units "
     "= greed').", "Poor worker defense (REPLAY_FINDINGS: bots bleed up to 118 "
     "workers to harass).", "Roach/hydra without splash melts to sieged tanks."],
   "counter": "PUNISH THE DRONE WINDOW — this is our single biggest un-taken "
     "edge (REPLAY_FINDINGS: harassment decides 94% of bot games). Hit the "
     "over-drone timing with a bio+tank push or hellion/medivac runbys before "
     "it remaxes; every dead drone compounds. If we let it reach the late game "
     "even, its remax beats us — so we must be ahead by ~10 min, not floating "
     "and passive.",
 },
 "z_muta": {
   "label": "Zerg mutalisk harass",
   "spectrum": "TECH / HARASS — fast lair into mutalisks",
   "summary": "Fast lair into a mutalisk pack that raids the worker line and "
     "picks off anything without anti-air, dodging our ground army entirely.",
   "strengths": ["Mutas ignore our wall and out-maneuver bio — pure harassment "
     "on the economy leg.", "Force us to build turrets/vikings we'd rather "
     "spend on the front."],
   "weaknesses": ["Muta tech is thin on the ground — a bio timing into its base "
     "while the mutas are away is devastating.", "Thors/vikings/massed marines "
     "with +armor hard-counter mutas."],
   "counter": "Anti-air BEFORE they pop (STRATEGY.md 'air needs a specific "
     "answer'): turrets over the mineral lines, keep marines home, add vikings/"
     "thor. Then push the muta-thinned ground while they're committed to "
     "raiding. Don't chase mutas with the main army.",
 },
 "t_bio_macro": {
   "label": "Terran bio macro (marine/marauder/medivac +tank)",
   "spectrum": "STANDARD MACRO — the mirror of our own plan",
   "summary": "Standard bio off 2-3 bases with combat shield/stim/upgrades, "
     "sometimes a tank or two. A near-mirror of GriffinBot — these games are "
     "decided by upgrades, tank count, positioning, and who mis-engages.",
   "strengths": ["No exploitable extreme — balanced army and economy.",
     "Stim + upgrades let a bio ball out-trade ours if it's ahead on either."],
   "weaknesses": ["No gimmick to catch us off-guard — comes down to execution.",
     "Bot bio control (splitting, focus fire) is usually mediocre."],
   "counter": "Win the mirror on the fundamentals (STRATEGY.md #3): be equal-"
     "or-ahead on +1/+1 timings (upgrades compound), keep more tanks sieged so "
     "our concave out-splashes its clump, and only take fights with position. "
     "Out-macro via cleaner production and no floating.",
 },
 "t_mech_macro": {
   "label": "Terran mech / turtle-mech (hellion/cyclone/tank/liberator)",
   "spectrum": "TURTLE → STANDARD — factory army, defensive, upgrades to a strong mid",
   "summary": "Factory-based mech: hellions early (worker harass + anti-light), "
     "into cyclones/tanks/liberators behind a defensive posture, grinding to a "
     "strong positional mid-game.",
   "strengths": ["Sieged tanks + liberators make a frontal attack very "
     "inefficient (defensive-position edge).", "Hellions punish us if we don't "
     "wall and can clear our own light harass."],
   "weaknesses": ["Mech is immobile and slow to take the map — cedes expansions.",
     "Thin against multi-pronged pressure; can't be everywhere.",
     "Slow tech/economy start behind the factory."],
   "counter": "Don't run bio into sieged mech head-on. Out-expand it (it turtles), "
     "out-upgrade, and use medivac drops / multi-pronged bio to exploit mech's "
     "immobility (harassment lens). Pick off the liberators/tanks with vikings "
     "or superior positioning before committing.",
 },
 "t_allin": {
   "label": "Terran one-base all-in (mass reaper / mass marauder)",
   "spectrum": "ALL-IN / CHEESE — one base, all army by ~8 min",
   "summary": "Pumps a single unit type (20+ reapers, or 20+ marauders from "
     "3 tech-lab rax) on one base and hits before we have tanks. Reapers "
     "grenade+kite our bio; marauders just out-mass it early.",
   "strengths": ["Wipes our army at the 8-min window (both replays: our supply "
     "crashed to 0 by 8-10 min).", "Reapers kite and pick off workers; "
     "marauders out-range and out-tank our marines one-base-for-one-base."],
   "weaknesses": ["One base, no economy — a held all-in leaves it dead.",
     "Reapers do nothing into a bunker + wall; marauders melt to sieged "
     "tanks and are slow.", "No anti-air, no splash, no tech."],
   "counter": "Same as any cheese (STRATEGY.md #1): wall, bunker, 1-2 tanks "
     "sieged, pull SCVs, HOLD — do not trade into it. This is a pure "
     "opening-safety problem: if our default opening isn't all-in-safe we "
     "lose the same way every game (see OPPONENTS.md). Survive → its one base "
     "loses to our expand.",
 },
 "t_air": {
   "label": "Terran starport air (banshee / liberator harass)",
   "spectrum": "TECH / HARASS — starport tech for cloaked/air harass",
   "summary": "Rushes Starport for banshees (often cloaked) or liberators to "
     "harass the worker line and zone our army, teching behind the pressure.",
   "strengths": ["Cloaked banshees demand detection we may not have — a "
     "specific-answer tech (STRATEGY.md).", "Air harass hits the economy leg "
     "and forces turrets."],
   "weaknesses": ["Starport tech is thin on the ground during the window.",
     "Turrets + vikings + a scan hard-counter it; marines with +1 shred it.",
     "Over-invests in harass that a prepared defense neutralizes."],
   "counter": "Detection early (scan/raven/turrets) the moment a Starport is "
     "scouted, turrets over the worker lines, keep marines home. Then punish "
     "the tech-thin ground with a bio+tank timing while the air is off "
     "harassing.",
 },
 "passive_broken": {
   "label": "Passive / broken / underperforming bot",
   "spectrum": "N/A — fails to execute a coherent economy or army",
   "summary": "In our game(s) this bot barely functioned: it got stuck at a "
     "handful of workers and near-zero army, idled, or crashed. GriffinBot's "
     "normal macro rolls over it. (One data point — the bot may perform "
     "better vs other opponents or in other games.)",
   "strengths": ["None observed in our sample — it did not contest the game."],
   "weaknesses": ["Stalled economy and/or army; idle production; possible "
     "crash or pathing lock. Loses to any bot that simply macros."],
   "counter": "Macro straight up and roll it — no special preparation needed. "
     "Keep producing workers, don't get greedy into an unscouted surprise, "
     "attack once maxed. Free win as long as we don't throw it.",
 },
}

# ---------------------------------------------------------------------------
# Per-bot classification. Key = archetype; note = specifics from the replay.
# Only bots we actually played (and mostly parsed) are listed. Grounded in the
# observed 8-minute build in data/profile_data.json.
# ---------------------------------------------------------------------------
CLASS = {
 # --- Protoss gateway all-ins (our worst cluster) ---
 "Klakinn": ("p_gate_allin", "31 zealots + 6 gateways by 8 min; our army 0 vs "
   "3375 at 8 min, GG ~11 min. The textbook build-order loss."),
 "ZEALOCALYPSE": ("p_gate_allin", "31 zealots off 4 gates; wiped our army to 0 "
   "by 9.7 min. Pure zealot flood."),
 "OneBaseStalkerBot": ("p_gate_allin", "21 stalkers on one base; 3325 army vs "
   "our 150 at 8 min. Stalker variant of the flood — ranged, so a bare wall "
   "isn't enough; needs tanks + bunker."),
 "protossinger": ("p_gate_allin", "15 zealot + 7 stalker off 5 gates; 2625 vs "
   "our 200 at 8 min."),
 "PerilousProtossBot": ("p_gate_allin", "10 zealots + 4 photon cannons; a "
   "cannon-backed zealot push that wiped us by 8 min."),
 # --- Protoss gateway pressure / robo / macro ---
 "GenesisLotus": ("p_gate_pressure", "7 gateways + adept/stalker/sentry "
   "(cpplinux). We won both — held the pressure and out-macroed. Source is "
   "publicly downloadable."),
 "PrimordialOrigin": ("p_gate_pressure", "8 gateways + stalker/sentry; strong "
   "3425 army at 8 min but we held and won. Source public."),
 "CryptBotRevival": ("p_gate_pressure", "Stalker/zealot off 2 gates; we won. "
   "Source public."),
 "WildLupo": ("p_gate_pressure", "Zealot/stalker off 5 gates into macro; even "
   "game we won at 21 min."),
 "Creepy_sentry": ("p_gate_pressure", "Adept/sentry pressure + 2 oracles; we won."),
 "iGottaCRush": ("p_gate_allin", "Named a rush bot but in our game it stalled "
   "at 15 pylons / ~16 probes and did nothing — we rolled it. Likely a "
   "proxy/cannon rush that failed to execute here."),
 "DasyBot": ("p_robo_timing", "Gateway + Robotics immortal timing (3 immortals, "
   "stalker, zealot); 8100 vs our 7250 at 12 min — lost both narrowly. "
   "Immortals out-trade our marauders; needs tanks + focus fire."),
 "TheCatSC2Bot": ("p_robo_timing", "Zealot + Robotics/observer (java); we won. "
   "Observer gives it detection most Protoss bots lack."),
 "PiG_Bot": ("p_macro", "Zealot/stalker/high-templar + 3 nexus + cannons; a "
   "macro/deathball Protoss. Out-scaled us; storm is a real splash threat."),
 # --- Protoss air / cannon turtle ---
 "Asteria": ("p_air_tech", "Stargate into 2 tempests + 6 cannons; tempests "
   "out-ranged everything and we had no anti-air. Classic un-scouted air loss."),
 "sharpy_protoss_test1": ("p_air_tech", "2 stargates + void rays behind zealots; "
   "we had no anti-air answer."),
 "Thssprtssbt": ("p_air_tech", "GREEDY: 4 nexus + oracles off a fast expand "
   "(source public). Out-econed us hard (80 vs 35 workers at 12 min). Punish "
   "the greed early or lose the macro game."),
 "Apidae": ("p_cannon_turtle", "6 photon cannons + gateway (java); a cannon "
   "turtle/rush that shut us out — we crawled to 3 supply by 12 min."),
 "Starlight": ("p_cannon_turtle", "Forge + cannons + shield batteries into "
   "zealots; we won by out-macroing the turtle."),
 "Laser-Circus": ("p_cannon_turtle", "Forge + cannons + batteries; we out-"
   "expanded and won."),
 "Forge": ("p_air_tech", "Gateway + phoenixes (cpplinux); game went to the "
   "84-min cap = a tie (neither could close). Air it teched, we couldn't kill it."),
 # --- Zerg ling floods ---
 "Crawler": ("z_ling_flood", "120 zerglings by 8 min — the purest ling flood. "
   "1-1: the game we HELD, its army collapsed to 175 by 12 min and we won. "
   "The single best proof that holding beats trading vs aggression."),
 "Princess-Mika": ("z_ling_flood", "66 lings + drone; 925 vs our 400 army at "
   "4 min. 0-3 — the ling timing arrives before our wall/splash."),
 "Princess-Mika-Test": ("z_ling_flood", "34 lings + spine crawlers; the test "
   "build of the above. Rushed us before we set up."),
 "Lissy": ("z_ling_flood", "46 lings + evo-chamber upgrades into macro; ling "
   "pressure into a drone economy."),
 "MY_SCRIPTING_SON": ("z_ling_flood", "60 lings + 40 drones (source public); "
   "ling flood that broke us by 15 min."),
 # --- Zerg drone macro ---
 "GLM_Bot": ("z_macro_drone", "80 drones, 4 hatch, ling/roach remax; 85 workers "
   "vs our 44 at 8 min. 1-2 — the one we won was a 44-min grind. Out-econ + "
   "remax is the danger."),
 "KoB": ("z_macro_drone", "58 drones into hydralisks; 153 vs our 97 supply at "
   "12 min. Out-macroed and out-remaxed us both games."),
 "SiriusBot": ("z_macro_drone", "64 drones + ling/queen macro (dotnet, plays "
   "Random→Zerg here); out-worker/out-supply by 12 min. 0-2."),
 "Persephone": ("z_macro_drone", "75 drones + 13 roaches; 152 vs our 78 supply "
   "at 8 min — a very fast roach remax."),
 "muravev": ("z_macro_drone", "70 drones + roach/creep; 100 workers by 12 min. "
   "Pure economic overrun."),
 "LoremIpsum": ("z_macro_drone", "74 drones + roach/spore; out-econed us."),
 "BobbyBotV13": ("z_macro_drone", "52 drones + roach (dotnet Random→Zerg); "
   "out-macro."),
 "Creepy_macro": ("z_macro_drone", "47 drones + heavy creep (49 tumors!) + "
   "queen; hit 200 supply by 12 min vs our 102. Extreme macro."),
 "QueenBot": ("z_macro_drone", "76 drones + 10 queens + mass creep (85 tumors); "
   "a queen/creep macro bot (source public)."),
 "Siriusly": ("z_macro_drone", "99 drones by 8 min (!) — over-drones massively "
   "(dotnet Random→Zerg). We WON: it drone-flooded so hard it had no army when "
   "we hit. The over-drone window, punished."),
 "DoopyBot": ("z_macro_drone", "Ling/drone macro; out-teched us to 200 by mid. "
   "0-1."),
 "DoopyBot-Test": ("z_macro_drone", "63 drones + ling/roach; 116 vs our 75 "
   "supply at 8 min but we won the 25-min game — held the roach waves and "
   "out-traded late."),
 "Myztery": ("z_macro_drone", "63 drones + spore/queen defensive macro; we won "
   "by out-trading (5000 vs 1325 army at 12 min)."),
 "kas": ("z_muta", "35 drones into 10 mutalisks; the mutas raided freely and "
   "wiped us — we had no anti-air. A specific-answer tech we missed."),
 # --- Terran bio macro ---
 "StarK234_0000": ("t_bio_macro", "25 marines off 5 rax + tech labs; standard "
   "bio that out-macroed us. 0-2."),
 "Stark234_PR02": ("t_bio_macro", "27 marines + 2 siege tanks + turrets; bio-"
   "tank, the PR variant of StarK234. 0-2."),
 "Terranosaur": ("t_bio_macro", "37 marines off 4 rax (dotnet); a near-mirror. "
   "We won the 39-min game on execution."),
 "WorkingAsIntended": ("t_bio_macro", "Marine/hellion + 4 bunkers + 3-3 macro "
   "(plays Random→Terran here); our worst repeat Terran, 0-3. Bunkered defense "
   "into a superior macro."),
 "Montka": ("t_bio_macro", "Marine/marauder/medivac (Random→Terran); a clean "
   "bio push we held and beat."),
 "Alexa": ("t_bio_macro", "Marine bio, slow start; we out-macroed and won."),
 "BioBot": ("t_bio_macro", "Marine + bunkers, slow bio; out-macroed us in the "
   "one game we lost."),
 "Slowpoke": ("t_bio_macro", "Marine + reaper + starport; a slower bio/air mix "
   "that out-positioned us late. 0-1."),
 "smokinggunbot": ("t_bio_macro", "Marine + 2 tanks + bunkers (java); a bio-"
   "tank turtle. Close 24-min loss — it out-lasted us."),
 # --- Terran mech ---
 "Hestia": ("t_mech_macro", "11 hellions + factory mech; 148 vs our 98 supply "
   "at 12 min. Hellions punished our un-walled front, mech out-macroed. 0-2."),
 "muravevTerran": ("t_mech_macro", "Reaper/cyclone/hellion mech; 143 vs our "
   "125 supply at 12 min. 0-2."),
 "27turtles": ("t_mech_macro", "Mech turtle — tanks/liberators/factories "
   "(source-name says it all). We WON both by out-expanding the turtle "
   "(STRATEGY.md turtle counter)."),
 "DownedStar1": ("t_mech_macro", "Reaper + siege tank + marauder; a tank-mech "
   "mix we out-macroed and beat."),
 "Horizon": ("t_air", "Bio + 3 starports (marauder/starport tech); teched to "
   "air/liberators and out-scaled us to 198 supply. 0-1."),
 "onlyfans": ("t_air", "Marine + 3 starports + banshees (cpplinux, source "
   "public); cloaked banshee harass we couldn't detect. Lost + 1 no-result."),
 # --- Terran one-base all-ins ---
 "oberon": ("t_allin", "23 marauders off 3 tech-lab rax by 8 min (cpplinux, "
   "source public); wiped our army to 0 by 8 min. A marauder all-in. 0-2."),
 "zig-reapers": ("t_allin", "24 reapers + 7 barracks by 8 min (cpplinux, source "
   "public); reaper flood grenaded our bio to 0 by 8 min. 0-1."),
 "AxeFighter": ("t_bio_macro", "Marine off 7 rax + 2 ebay (dotnet, source "
   "public); a mass-rax bio macro that out-produced us. 0-2."),
 # --- Passive / broken in our sample ---
 "JackBot2.0": ("passive_broken", "Stuck at 24 SCVs / 0 army the entire game; "
   "we won both (2-0)."),
 "BioBotGod": ("passive_broken", "Stuck at 24 SCVs / 0 army for 57 min; free win."),
 "CyraxxDKAkron": ("passive_broken", "Stuck at 24 SCVs / 0 army; free win."),
 "Zummok": ("passive_broken", "Stuck at 15 SCVs / 0 army (cpplinux); free win."),
 "Chance": ("passive_broken", "Reached ~18 SCVs + 4 marines then stalled "
   "(Random, source public); we won."),
 "Visenya": ("passive_broken", "Stalled at 11 drones / 0 army (cpplinux); we "
   "won both (2-0). Barely functioned in our games."),
 "CodeX001": ("passive_broken", "Stuck at 12 probes / 0 army; game hit the "
   "84-min cap as a tie because neither side could end it."),
 "MangoShark": ("passive_broken", "No result recorded / no army seen; treat as "
   "unconfirmed."),
 "Leviabyss": ("passive_broken", "Match cancelled / no-result in our sample; "
   "unconfirmed."),
 "Starcraft-Agent-v01": ("passive_broken", "No decisive result in our sample; "
   "a learning-agent bot, behavior unconfirmed."),
 "Creepy_duo_canon": ("p_cannon_turtle", "Cannon-rush variant of the Creepy "
   "family; our game was a no-result/tie — treat as a cannon-rush threat, "
   "prepare for early cannons."),
 "lishimin": ("passive_broken", "Our own older Protoss bot (cannon-rush "
   "lishimin) — appears as an opponent in a mirror test. Not a real ladder rival."),
}

RACE_FULL = {"P": "Protoss", "T": "Terran", "Z": "Zerg", "R": "Random"}


def clean_build(pairs):
    out = []
    for name, cnt in pairs:
        if name in NOISE:
            continue
        out.append((name, cnt))
    return out


def slugify(name):
    return name.replace("/", "_").replace(" ", "_")


def bot_md(name, entry):
    m = entry["meta"]
    r = entry["record"]
    race = RACE_FULL.get(m.get("race", "?"), m.get("race", "?"))
    cls = CLASS.get(name)
    arch_key = cls[0] if cls else None
    note = cls[1] if cls else ""
    a = ARCH.get(arch_key)
    g = r["W"] + r["L"] + r["tie"] + r["other"]
    L = []
    L.append(f"# {name}\n")
    verdict = ("**We lose this matchup.**" if r["L"] > r["W"] else
               "**We win this matchup.**" if r["W"] > r["L"] else
               "**Even / unresolved matchup.**")
    L.append(f"> {verdict}  GriffinBot record vs {name}: "
             f"**{r['W']}W – {r['L']}L**"
             + (f" (+{r['tie']} tie)" if r["tie"] else "")
             + (f" (+{r['other']} no-result)" if r["other"] else "")
             + f" over {g} game(s).\n")

    L.append("## Identity\n")
    L.append(f"| | |")
    L.append(f"|---|---|")
    L.append(f"| **Race** | {race}"
             + (f" (played {RACE_FULL.get(_replay_race(entry), _replay_race(entry))} "
                "in our sampled game)" if _replay_race(entry) and
                _replay_race(entry) != m.get("race") else "") + " |")
    L.append(f"| **Bot type** | {m.get('type','?')} |")
    L.append(f"| **AI Arena id** | {m.get('id','?')} |")
    L.append(f"| **First seen** | {m.get('created','?')} |")
    L.append(f"| **Source public** | {'yes — downloadable for study' if m.get('zip_public') else 'no'} |")
    if a:
        L.append(f"| **Archetype** | {a['label']} |")
        L.append(f"| **Spectrum** | {a['spectrum']} |")
    L.append("")

    if a:
        L.append("## Strategy\n")
        L.append(a["summary"] + "\n")
        if note:
            L.append(f"**In our games:** {note}\n")

    # observed build + trajectory
    for p in entry["replays_parsed"]:
        build = clean_build(p["enemy_build_8min"])
        bstr = ", ".join(f"{n}×{c}" for n, c in build)
        L.append(f"## Observed build — game {p['match']} "
                 f"({p['minutes']} min, we {_outcome(p['our_outcome'])})\n")
        L.append(f"**First 8 min production (opponent):** {bstr}\n")
        traj = p["trajectory"]
        if traj:
            L.append("| min | our supply | their supply | our army $ | their army $ | our workers | their workers |")
            L.append("|----:|----:|----:|----:|----:|----:|----:|")
            for t in traj:
                L.append(f"| {t['m']} | {t['our_supply']:.0f} | {t['their_supply']:.0f} "
                         f"| {t['our_army']} | {t['their_army']} | {t['our_workers']} "
                         f"| {t['their_workers']} |")
            L.append("")

    if a:
        L.append("## Strengths\n")
        for s in a["strengths"]:
            L.append(f"- {s}")
        L.append("\n## Weaknesses\n")
        for w in a["weaknesses"]:
            L.append(f"- {w}")
        L.append("\n## How GriffinBot should play it\n")
        L.append(a["counter"] + "\n")

    L.append("---")
    L.append("*Auto-generated by `bot_profiles/_generate.py` from replay "
             "tracker data. Build orders are from one sampled game; "
             "deterministic bots repeat them, but re-scout to confirm.*")
    return "\n".join(L)


def _replay_race(entry):
    for p in entry["replays_parsed"]:
        rr = p.get("opp_race_in_replay", "")
        return {"Prot": "P", "Terr": "T", "Zerg": "Z"}.get(rr[:4], "")
    return ""


def _outcome(o):
    return {"W": "won", "L": "lost", "tie": "tied"}.get(o, o)


ARCHLABEL = {
 "p_gate_allin": "P gateway all-in", "p_gate_pressure": "P gateway pressure",
 "p_robo_timing": "P robo/immortal", "p_air_tech": "P air/skytoss",
 "p_cannon_turtle": "P cannon turtle", "p_macro": "P macro deathball",
 "z_ling_flood": "Z ling flood", "z_macro_drone": "Z drone macro",
 "z_muta": "Z mutalisk", "t_bio_macro": "T bio macro", "t_mech_macro": "T mech",
 "t_allin": "T one-base all-in", "t_air": "T starport air",
 "passive_broken": "passive/broken",
}

README_HEAD = """# AI Arena Opponent Profiles

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
"""


def readme():
    rows = []
    for name, e in DATA.items():
        if not name.strip():
            continue
        r = e["record"]; m = e["meta"]
        gm = r["W"] + r["L"] + r["tie"] + r["other"]
        cls = CLASS.get(name)
        arch = ARCHLABEL.get(cls[0], "?") if cls else "?"
        rec = f"{r['W']}-{r['L']}" + (f"+{r['tie']}T" if r["tie"] else "")
        res = ("**WIN**" if r["W"] > r["L"] else
               "**LOSS**" if r["L"] > r["W"] else "even")
        rows.append((gm, 0 if res == "**LOSS**" else 1, name.lower(),
                     name, m.get("race", "?")[0], arch, rec, res,
                     "yes" if m.get("zip_public") else ""))
    rows.sort(key=lambda x: (-x[0], x[1], x[2]))
    lines = [README_HEAD.rstrip("\n")]
    for gm, _, _, name, race, arch, rec, res, src in rows:
        lines.append(f"| [{name}]({slugify(name)}/PROFILE.md) | {race} | "
                     f"{arch} | {rec} | {res} | {src} |")
    lines.append("\n*Regenerate with `python bot_profiles/_generate.py`.*")
    return "\n".join(lines)


def main():
    written = 0
    for name, entry in DATA.items():
        if not name.strip():
            continue
        slug = slugify(name)
        d = os.path.join(HERE, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "PROFILE.md"), "w") as f:
            f.write(bot_md(name, entry))
        written += 1
    with open(os.path.join(HERE, "README.md"), "w") as f:
        f.write(readme())
    print(f"wrote {written} profiles + README.md")


if __name__ == "__main__":
    main()
