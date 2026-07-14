# StarCraft II Concrete Rules

Drilldown of the high-level principles in [`PRINCIPLES.md`](PRINCIPLES.md) into
concrete, checkable rules. Each rule is meant to be specific enough that a bot
(or a player) can evaluate it against game state and act on it. Numbers are
sensible defaults, not gospel — tune per race, matchup, and map.

Each section maps to a principle by number.

## 1. Never stop producing workers

- Build a worker whenever a production structure (Command Center / Nexus /
  Hatchery) is idle and you are below the saturation cap.
- Saturation target: ~16 workers on minerals + 3 per gas geyser per base
  (~22 per fully saturated base).
- Stop worker production at a base once it is saturated; shift to expanding or
  transferring workers to the next base.
- Rule of thumb: worker count should roughly track `16 × number_of_bases` in
  the early/mid game.

## 2. Don't get supply blocked

- Build supply when `supply_left <= threshold`, where the threshold scales with
  production capacity (e.g. `2 + 2 × num_production_buildings`).
- Never sit at 0 supply remaining with unspent minerals.
- Queue a second supply structure early if multiple production buildings will
  finish around the same time.

## 3. Spend your resources — don't float

- Keep unspent minerals under ~400 and gas under ~300 in the mid game; if above,
  add production, army, tech, or an expansion.
- If minerals are floating high, the usual fix is: more production buildings or
  another base.
- If gas is floating, you likely have too many gas-light units queued — spend it
  on tech/upgrades or gas-heavy units.

## 4. Expand

- Take a natural expansion once your main is near mineral saturation and you can
  defend it (or the map is quiet).
- General economic pacing: aim to start a new base roughly every 1.5–3 minutes
  when not under pressure.
- Never take an expansion you cannot defend — pair each new base with defensive
  structures or army presence.

## 5. Scout constantly

- Send an early scout (worker or first fast unit) to find the opponent's build
  before your first key tech/timing decision.
- Maintain persistent map vision: watchtowers, and a cheap recurring scout
  (overlord / reaper / adept / medivac) every ~60–90 seconds.
- Track and store: opponent race, base count, army supply/composition, and tech
  buildings seen. Re-scout when this data goes stale.

## 6. Keep production saturated

- No production building should sit idle with resources available — always have
  something queued or a reason not to.
- Add production buildings until income can no longer keep them all busy, then
  expand to raise income.
- Balance production to your economy: add production buildings only as fast as
  income can keep them all continuously busy (tune per unit cost).

## 7. Only fight favorable engagements

- Engage only when the estimated outcome is favorable: compare army value,
  composition matchup, terrain, and reinforcement proximity.
- Prefer fighting with a concave/surround, on high ground, or at a choke that
  limits the enemy's effective width.
- Disengage (retreat/kite) when caught in a bad spot rather than committing to a
  losing fight.
- Defender's advantage: near your own production and static defense, accept
  slightly worse odds; deep in enemy territory, demand better odds.

## 8. Composition beats numbers

- Continuously compare your composition against the scouted enemy composition and
  add counter units (e.g. splash vs. clumped light, anti-air vs. air).
- Avoid over-committing to a single unit type that has a hard counter on the
  field.
- Adjust the build in response to scouting, not just to a fixed opening.

## 9. Micro to multiply your army

- Kite ranged-vs-melee: attack, then reposition while on cooldown.
- Focus fire high-value targets first (spellcasters, siege units, key damage
  dealers).
- Split against splash damage (banelings, siege tanks, storms); clump only when
  safe.
- Use spellcasters and abilities proactively (stim, blink, EMP, storm, fungal)
  rather than hoarding energy.

## 9a. Fight only favorable engagements

Encoded in `strategy_engine/combat.py` (`assess_engagement`).

- Estimate effective strength, not raw supply: `army_supply x upgrade_edge x
  situational`, where situational stacks terrain/surround (+15%), defender's
  advantage at home (+15%), reinforcements close (+10%), favorable composition
  (+20%), minus bad position (-20%) and enemy cloak/air without detection (-20%).
- Engage when the effective ratio is comfortably favorable (>= ~1.1) **and** you
  are not already trading down.
- Avoid / disengage when the ratio is unfavorable (<= ~0.9) away from home, or
  when trades are going against you regardless of size — don't feed a losing
  fight.
- Hold (don't retreat) when behind at home if defender's advantage keeps the
  effective ratio close (>= ~0.7); don't take even coinflips out in the open.
- An upgrade/tech-tier edge is efficiency bought in advance: let it raise the
  effective ratio, and start fights that a raw-supply count would call even.
- Get detection/anti-air in place *before* engaging when the enemy has cloak or
  air; fighting blind applies the -20% penalty for a reason.

## 9b. Harass to attack the investment

Attacking:

- Commit only a small, mobile detachment to harass — never so much that your main
  army or defense is exposed.
- Target the economy first: workers, then tech/production, then supply. Dead
  workers compound as lost mining for the rest of the game.
- Retreat harass units the moment the defense arrives; preserve them to strike
  again rather than trading into a defended line.
- Judge each harass by return — workers killed, tech delayed, responses forced —
  versus what you committed and risked. Pull off harass that isn't paying.
- Harass to cover your own greed: expand or tech behind the pressure while the
  opponent is distracted.

Defending:

- Pre-place static defense and detection at vulnerable spots (worker lines, tech,
  expansions) before the raid lands.
- Keep a small holding force at home instead of pulling the main army back for
  every poke.
- Pull threatened workers out of the raid, then return them to mining as soon as
  it's safe — minimize mining downtime.
- Don't over-commit: never chase raiders with your main army or let harass stall
  your macro. Respond at proportionate cost and keep your own plan moving.

## 10. Tech and upgrades matter

Upgrades:

- Start attack/armor upgrades as soon as the economy supports it (typically once
  your natural is up and mineral income is steady); keep upgrade structures
  running continuously — never let one sit idle with gas available.
- Prioritize the upgrade that helps your core army most (attack for aggression,
  armor for durability against many small hits).
- Don't skip upgrades to over-produce units — an upgraded smaller army often
  beats an unupgraded larger one.
- Add a second upgrade structure when income can support two research paths at
  once, so attack and armor progress in parallel.

Tech:

- Tech only as fast as you can defend the window it comes online — if scouting
  shows aggression, hold army/defense before pushing tech higher.
- Tech reactively to scouted threats *before* they land: start detection when you
  see a cloak/burrow enabler, anti-air when you see an air tech building, splash
  when you see massing light units.
- Don't go tech-blind: if you have no answer to a scouted tech, prioritize the
  counter over more of your current units.
- When a tech switch is the right counter, cover the transition window with your
  existing army — don't move out or expand greedily while the switch is
  incomplete.
- Match gas income to tech ambitions: rushing tech needs early gas; if gas is
  floating, you likely have unspent tech/upgrade options.

## 11. Multitask — do everything at once

- Every "loop" (bot step, or player's attention cycle), touch each subsystem:
  economy, supply, production, tech/upgrades, scouting, army positioning.
- Never tunnel on a single fight while workers, supply, and production stall.
- Prioritize when resources are scarce: economy and supply first, then army,
  then tech — but keep all of them moving.

## Two lenses (evaluation heuristics)

- **Efficiency:** after each engagement, check that you traded up (killed more
  value than you lost); flag idle resources — banked money, idle production,
  unused larva, workers not mining.
- **Tempo / initiative:** when ahead in army/economy, apply pressure and expand;
  when behind, defend, delay, and look for a favorable engagement to swing
  momentum back.
