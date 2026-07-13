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

## 10. Upgrades matter

- Start attack/armor upgrades as soon as the economy supports it; keep upgrade
  structures running continuously.
- Prioritize the upgrade that helps your core army most (attack for aggression,
  armor for durability against many small hits).
- Don't skip upgrades to over-produce units — an upgraded smaller army often
  beats an unupgraded larger one.

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
