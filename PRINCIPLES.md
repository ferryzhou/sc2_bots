# StarCraft II Gameplay Principles

High-level principles of strong StarCraft II play. These are race-agnostic
fundamentals — the "why" behind good decisions. Execution differs by race and
matchup, but the underlying ideas are universal.

For the concrete, checkable rules that drill down from each principle, see
[`RULES.md`](RULES.md).

## Macro fundamentals

1. **Never stop producing workers.** Economy is the foundation of everything.
   Keep making workers until saturated, so money converts to army faster.
2. **Don't get supply blocked.** Build supply ahead of need. A block means idle
   production — wasted resources and time.
3. **Spend your resources — don't float.** Banked minerals and gas do nothing.
   Keep your money low and working: more production, army, tech, or expansions.

## Growth and information

4. **Expand.** More bases means more income means more army. Timely expansions
   are how most games are won economically — balanced against the risk of
   defending more ground.
5. **Scout constantly.** You can't react to what you can't see. Track the
   opponent's tech, army size, and timings so nothing catches you unprepared.
   But you never see everything — for making decisions under the permanent fog of
   war, see [`INFORMATION.md`](INFORMATION.md).
6. **Keep production saturated.** Match production buildings to your income so
   resources convert to army continuously. Idle production is wasted potential.

## Fighting well

7. **Only fight favorable engagements.** Good terrain, good surround, right
   composition. Winning battles you should not have taken is how most games are
   lost.
8. **Composition beats numbers.** Build to counter what the opponent has.
   Supply-for-supply, the better-countered army wins.
9. **Micro to multiply your army.** Kiting, focus fire, spellcasters, and
   splitting let a smaller army beat a larger one.
10. **Upgrades matter.** Attack and armor upgrades compound across every unit
    and every fight. Neglecting them quietly loses engagements.

For the tactical layer — how to win battles, defend, attack, and be efficient in
combat — see [`COMBAT.md`](COMBAT.md).

## The meta-principle

11. **Multitask — do everything at once.** The real skill is holding macro
    (workers, supply, production, expansions) while simultaneously scouting,
    positioning, and microing fights. Whoever keeps more plates spinning wins.

## The central tension: economy vs. army

Every resource can go to **economy** (workers, expansions) or **army** (units,
tech, upgrades) — not both. This is the fundamental strategic choice, and the
principles above pull in opposite directions:

- **Investing in economy** (expand, more workers) makes you *stronger later* but
  *weaker now* — you have fewer units on the field while the investment pays off.
- **Investing in army** makes you *stronger now* but *weaker later* — units spent
  on early pressure are resources not compounding into more income.

There is no fixed right answer; the balance depends on what the opponent is
doing. Key ideas:

- **Greed vs. safety.** Expanding or teching greedily maximizes your ceiling but
  widens the window where you can be punished. Play only as greedy as your
  scouting says is safe.
- **Match investment to threat.** More army when the opponent is aggressive or
  hitting a timing; more economy when the map is quiet or the opponent is also
  teching/expanding.
- **Drone/probe/SCV pulls both ways.** Every worker is economy that could have
  been a unit — over-saturating while under threat is as wrong as under-building
  workers while safe.

The whole game is a running negotiation of this trade-off. Falling behind on
economy loses slowly; dying to a timing loses instantly.

For common strategy archetypes along this spectrum — and how to detect and
counter each — see [`STRATEGY.md`](STRATEGY.md). For how these principles
specialize when the opponent is a *deterministic bot* that plays the same build
every game (the AI Arena ladder) — opponent priors, opening safety, and
per-opponent counters — see [`OPPONENTS.md`](OPPONENTS.md) and the concrete
per-bot dossiers in [`bot_profiles/`](bot_profiles/).

## Tech and upgrades: the third investment

Economy and army are not the only places resources go. **Tech** (new buildings,
units, and abilities) and **upgrades** (attack/armor and unit improvements) are a
third form of investment — and, like economy, they pay off *over time* rather
than immediately. Every gas spent on research or a tech building is army you
don't have *right now*, in exchange for a stronger army *later*. So tech sits on
the same now-vs-later tension as economy.

What makes tech and upgrades distinct:

- **Upgrades compound with army size and game length.** A +1/+1 attack/armor
  bonus applies to *every* current and future unit. The bigger your army and the
  longer the game, the more each upgrade is worth — they multiply your army
  rather than add to it. An upgraded smaller army routinely beats a larger
  unupgraded one.
- **Tech changes what's *possible*, not just how much.** Economy and army are
  quantities; tech unlocks new options — a new unit, an ability, detection,
  anti-air. It's how you access answers you simply don't have at lower tech.
- **Tech creates power spikes and timing windows.** Finishing a key upgrade or
  tech is a moment you're suddenly stronger (a spike to attack on), while the
  research is in progress you're weaker (a window to be punished). See the timing
  section below.
- **Tech and upgrades buy combat efficiency — structurally.** Efficiency (winning
  trades: killing more value than you lose) comes from two sources. One is *in the
  moment* — micro, positioning, terrain, focus fire. The other is *built in ahead
  of time* — higher-tier units and attack/armor upgrades raise your trade ratio in
  every fight, before a single command is issued. A +1 edge or a tech-tier
  advantage means each of your units does more and dies less, so you trade up even
  with equal control. This is why the efficiency lens and the tech/upgrade
  investment are the same coin: **research is efficiency you pay for in advance.**
  The replay data bears it out — winners were the more-upgraded side in ~49% of
  pro games and ~72% of bot games ([`analysis/REPLAY_FINDINGS.md`](analysis/REPLAY_FINDINGS.md)).

Key ideas for spending on tech:

- **Tech is an investment with the same greed risk.** Rushing high tech on a thin
  army is as punishable as a greedy economy — you're weak during the window it's
  coming online. Skipping tech entirely, though, leaves you outclassed once the
  opponent's stronger units and upgrades arrive.
- **Keep upgrade structures always working.** Idle research is wasted the same way
  idle production is. Start attack/armor upgrades as soon as the economy supports
  them, and prioritize the path that helps your core army most (attack to push,
  armor to survive many small hits).
- **Tech reactively as a counter.** Much teching is a response to scouting:
  detection against cloak, anti-air against air, splash against massed light.
  Reading the need before it's fatal is part of scouting.
- **Tech switches cost tempo.** Transitioning your composition to exploit or
  counter the opponent is powerful, but it costs time and resources and opens a
  vulnerability window while the new tech and units come online.

Think of it as three competing claims on every resource — **economy, army, and
tech/upgrades** — with economy and tech both being bets on *later* that leave you
thinner *now*.

## Timing: strength is relative and changes over time

Army strength is never absolute — it only matters **relative to the opponent at
a given moment**, and that relative balance swings constantly as both players
add economy, army, tech, and upgrades.

- **Power spikes.** Finishing an upgrade, a key tech, a critical unit count, or a
  round of production creates a moment where you are temporarily stronger. These
  spikes are when attacks are strongest.
- **Timing attacks.** A deliberate push built to hit exactly when you have a
  spike and the opponent does not — e.g. before their expansion pays off, before
  their tech finishes, or before they have detection/anti-air.
- **Windows of vulnerability.** Expanding, teching, or transitioning leaves a
  window where your on-field army is weak. Know when you are in one (defend
  carefully) and when the opponent is in one (attack).
- **Ahead now vs. ahead later.** A greedy economy is "ahead later"; an army
  investment is "ahead now." Whoever is "ahead now" should use that lead before
  it expires — attack, pressure, or force a favorable trade rather than sitting
  on a temporary advantage that the opponent's economy will erase.

The practical question every moment is: *am I stronger now or will I be stronger
later?* If now, find a way to use it. If later, survive until then.

## Harassment: attack the investment, not just the army

Most damage in a game doesn't have to come from a main-army battle. **Harassment**
— small, mobile forces striking the opponent's economy, tech, or production
without committing to a full engagement — attacks the *investments* directly.
Drops, runbys, air raids, cloaked units, and worker-line pokes all trade a little
army for damage the opponent can't easily recover.

Why it's powerful:

- **It hits the economy leg directly.** Killing workers or forcing a worker pull
  strikes the foundation everything else is built on. A handful of dead workers
  compounds — it's lost mining for the rest of the game, often a better return
  than the same units trading in a main fight.
- **It exploits the multitask principle.** Harassment forces the opponent to
  defend a second (or third) place while still running their macro. Whoever can
  defend the harass *and* keep macroing wins; harassment is how you punish an
  opponent who can only focus on one thing at a time.
- **It buys tempo and cover.** Pressure keeps the initiative and distracts the
  opponent while *you* do something greedy — expand, tech, or take the map behind
  the harass. Even a contained harass that does no direct damage has value if it
  pulled units back, forced static defense, or stuttered their production.

The cost side — harassment is still an investment:

- **The units could have been in the main army.** Harass that dies for no damage
  is a bad trade; it's a bet that the economic/tempo damage exceeds the army you
  committed.
- **Efficiency still rules.** Judge harassment by return: workers killed, tech
  delayed, responses forced — versus what you spent and risked. Don't feed
  mobile units into a defended line.

Defending harassment is the mirror image: static defense and detection at
vulnerable spots, keep-back units or turrets covering worker lines and tech, and
pull workers efficiently — but *don't over-commit* chasing raiders while your own
macro or main army suffers. Trading your whole focus to stop a small harass is
exactly the mistake the harasser wants.

## Two lenses

- **Efficiency (the strongest single lens):** win trades — kill more value than
  you lose — and never let resources (money, larva, production time, worker
  mining) sit idle. Analysis of 65 pro games
  ([`analysis/REPLAY_FINDINGS.md`](analysis/REPLAY_FINDINGS.md)) found trade
  efficiency to be the single best predictor of the winner (88% of games),
  out-predicting raw economy. A bigger economy loses anyway if you can't
  *convert* it — the games where the loser out-produced but still lost were all
  cases of floating resources, staying supply-blocked, and losing the decisive
  trade. Treat efficiency as first-order, not a footnote. And note efficiency is
  bought two ways: *in the moment* (micro, positioning, terrain) and *in advance*
  (tech tier and upgrades, which raise your trade ratio structurally — see the
  tech/upgrades section).
- **Tempo / initiative:** being ahead lets you dictate. Use a lead to pressure
  and expand; when behind, defend, stall, and look for a favorable swing.
