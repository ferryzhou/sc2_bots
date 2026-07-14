# StarCraft II Combat: Battles, Defense, Attack, Efficiency

How engagements are actually won. This is the tactical layer beneath the
"Fighting well" principles in [`PRINCIPLES.md`](PRINCIPLES.md), and it is where
the model's strongest empirical result lives: across 65 pro and 90 AI Arena games
([`analysis/REPLAY_FINDINGS.md`](analysis/REPLAY_FINDINGS.md)), **winning trades
was the single best predictor of the winner** — 88% of pro games, 99% of bot
games. Everything below serves one goal: *kill more value than you lose.*

## How to win battles

A battle is rarely decided by raw supply — it's decided by how much of each
army's damage actually lands. The levers, roughly in order of impact:

- **Composition / counters.** The most one-sided fights are decided before they
  start, by the unit matchup (splash vs. clumped light, anti-air vs. air, armored
  counters). Supply-for-supply, the better-countered army wins. Fix composition
  *before* engaging, not during.
- **Terrain.** Fight on high ground (attackers up a ramp miss and are seen late),
  at a choke that limits how many of the enemy can shoot at once, or with vision
  advantage. Never fight blind up a ramp or in the open against superior range.
- **Concave / surround.** Spread your army into an arc so more units are in range
  of the enemy front while fewer of theirs reach you. A good surround multiplies a
  ranged army; being surrounded (or fighting in a line down a corridor) wastes
  most of your DPS.
- **Focus fire and target priority.** Kill the highest-value, highest-threat
  targets first — spellcasters, siege units, key damage dealers — so their damage
  leaves the fight immediately. Overkill (many units on one cheap target) wastes
  shots; spread damage to remove whole units.
- **Splash management.** Split against splash (banelings, siege, storms, disruptors)
  and clump only when the enemy has no splash. A single bad clump against splash
  can lose a fight outright.
- **Ability usage.** Proactive spells win fights: stim, blink, EMP, storm, fungal,
  force fields. Hoarding energy is wasted efficiency; a well-placed spell is often
  worth more than several units.
- **Unit preservation.** Pull low-health units out (blink, stutter-step back,
  retreat medivacs/overlords). A wounded unit that survives fights again at full
  value next battle; a dead one doesn't.
- **Engage on your terms.** Decide the fight, don't stumble into it: fight with
  reinforcements close, near your own production/defense, when your spells are off
  cooldown and theirs aren't. If the setup is bad, *disengage* — a fight declined
  is value preserved.

## How to defend

Defense is the cheapest efficiency in the game: the defender fights with
advantages the attacker paid to overcome.

- **Defender's advantage is real.** Near your own bases you reinforce faster,
  fight on known terrain, and can lean on static defense. Accept slightly worse
  odds at home that you'd never take deep in enemy territory.
- **Walls and chokes.** Wall the ramp/natural to deny early aggression and to
  force the enemy to fight through a narrow front where your surround and splash
  are strongest. Hold the choke; don't step off it into the open.
- **Static defense, placed to cover.** Bunkers / spines / photon cannons /
  spores + turrets cost less than the workers a raid would kill. Place them to
  cover worker lines, chokes, and expansions — the spots the attacker wants.
- **Detection everywhere it matters.** Cloak, burrow, and drops punish missing
  detection. Cover vulnerable spots *before* the threat lands, reacting to the
  enabling tech, not the units.
- **Trade space for time when behind.** You don't have to hold every base. Give
  ground, keep your army alive, and defend a tighter perimeter until an upgrade,
  tech, or reinforcement swings the fight back. A lost base is recoverable; a lost
  army usually isn't.
- **Defend multiple fronts without over-committing.** Keep a small holding force
  and static defense at home so harassment doesn't drag your whole army out of
  position — that split is exactly what the attacker is buying.
- **Pull workers efficiently.** Move threatened workers out of a raid and right
  back to mining; don't let a small poke stall your economy longer than the poke
  itself.

## How to attack

Attacking well is about choosing *when* and *where* so the fight is favorable
before it begins — never trading down just to be doing something.

- **Attack the window, not the clock.** Hit when you have a power spike (finished
  upgrade, key tech, production round) and the opponent has a weakness (mid-
  expansion, mid-tech, missing detection/anti-air). Attacking off-spike into a
  ready defender feeds the defender's advantage.
- **Don't attack into strength.** Refuse fights into static defense, up ramps, or
  through chokes the enemy holds. If the front is fortified, don't push it — go
  around it (harass, expand, take the map) until you can force a fight in the open.
- **Multi-prong to split attention.** Two threats at once (a drop while the main
  army pressures, or attacks on two bases) exploit the fact that the opponent has
  one army and finite attention. Whoever defends multiple places while macroing
  wins; make them fail that test.
- **Choose the target: economy, army, or tech.** Often the best "attack" isn't
  the army at all — it's the economy (harass workers) or a tech/production
  building. Attack the *investment*, which is harder to replace than units.
- **Contain, don't always commit.** A contain (holding the map/chokes, denying
  expansions) can starve an opponent without a risky all-in fight. Pressure that
  forces bad trades or worker pulls is a win even without a big engagement.
- **Snowball a won fight.** After winning an engagement, immediately convert:
  take bases, kill workers, deny their expansions, push into the window while
  their army is rebuilding. Failing to follow up lets a temporary lead expire.

## How to be efficient

Efficiency is the through-line — the lens the replay data ranks #1. It's two
things: **trade up in fights**, and **never let resources sit idle.**

- **Trade up.** Judge every engagement by value killed vs. value lost, not by who
  held the ground. A won fight that cost more than it killed is a loss on the
  balance sheet. Seek fights where you trade up; avoid the ones where you don't.
- **Don't feed / don't over-commit.** Reinforcing piecemeal into a lost fight, or
  chasing a retreat into their defense, throws away units for nothing. Cut losses;
  the army you keep fights again.
- **Preserve and reuse.** Retreating a damaged army to fight again next battle is
  often worth more than the ground you'd hold by standing. Keep spellcasters and
  key units alive above all.
- **Idle resources are wasted efficiency.** The COUNTER games — where a *bigger*
  economy still lost — were all floating minerals, idle production, and supply
  blocks. Money not working, larva not used, workers not mining, and production
  sitting idle are all silent losses. Convert economy into army/tech/upgrades
  continuously.
- **Cost-efficient tools.** Splash, abilities, and upgrades are force multipliers:
  they add damage across your whole army for a fixed cost. An upgraded, well-cast
  smaller army beating a bigger raw one is efficiency in one picture.
- **Buy efficiency in advance with tech and upgrades.** Trade efficiency has two
  sources: *in the moment* (the micro and positioning above) and *built in
  beforehand* — higher-tier units and attack/armor upgrades raise your trade ratio
  in every fight before a command is issued. Research is efficiency you pay for up
  front; the more-upgraded side won ~49% of pro and ~72% of bot games in the data.
- **Efficiency = conversion.** The whole point of economy is to be *spent* into a
  board advantage. A lead you can't convert into dead enemy value isn't a lead
  yet.

## Connects to

- [`PRINCIPLES.md`](PRINCIPLES.md) — "Fighting well" and the efficiency lens.
- [`STRATEGY.md`](STRATEGY.md) — when to pick attack vs. defense by opponent
  archetype (attack greed, defend aggression).
- [`RULES.md`](RULES.md) — concrete engagement/anti-waste rules.
- [`strategy_engine`](strategy_engine/) — `assess_efficiency` surfaces
  `should_seek_fights` / `should_avoid_fights` and idle-resource waste directly to
  a bot.
