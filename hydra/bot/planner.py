"""planner: turn a high-level strategy into a concrete execution plan.

The ``Planner`` is the bridge between *strategy* (a declarative
``StrategyProfile``) and *execution* (what the managers do this step). Every
planning tick it produces a fresh ``ExecutionPlan`` -- a flat set of targets
(drone count, army composition, tech/upgrade targets, expansions, static
defense, and a combat stance). Because the plan is regenerated from the live
game state each time, the bot's behaviour is fully **dynamic**: the same profile
yields a different plan as the game changes, and swapping the profile mid-game
(the selector's job) immediately reshapes the plan.

The planner is also where *adaptation* happens. It starts from the profile's
knobs and then overlays the strategy_engine's reads -- defense emergencies,
engagement odds, power timing, detection/anti-air needs -- so the concrete plan
reflects both our chosen strategy and what the opponent is actually doing. All of
that adaptive logic lives here, in one place, rather than being scattered as
ad-hoc rules through the executors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from sc2.ids.unit_typeid import UnitTypeId as U
from sc2.ids.upgrade_id import UpgradeId

from strategy_engine import Advice, Engagement, PowerTiming

from .strategies import StrategyProfile, Stance
from . import zerg_data


# Combat stances the army executor understands.
ATTACK = "attack"
DEFEND = "defend"
HARASS = "harass"
HOLD = "hold"


@dataclass
class ExecutionPlan:
    """A concrete, fully-resolved set of targets for one planning window."""

    profile_name: str
    stance: Stance

    # economy
    drone_target: int = 20
    queen_target: int = 2
    gas_target: int = 4
    base_target: int = 3
    expand_now_ok: bool = True
    larva_econ_share: float = 0.5   # fraction of each step's larva spent on drones

    # army
    army_composition: Dict[U, float] = field(default_factory=dict)  # normalised
    tech_targets: List[U] = field(default_factory=list)
    prerequisite_structures: List[U] = field(default_factory=list)
    tier_target: zerg_data.Tier = zerg_data.Tier.HATCHERY
    upgrade_targets: List[UpgradeId] = field(default_factory=list)

    # defense
    spines: int = 0
    spores: int = 0
    need_detection: bool = False

    # combat
    combat_stance: str = HOLD
    attack_supply: float = 40.0
    regroup_supply: float = 12.0
    pull_workers: bool = False

    reasons: List[str] = field(default_factory=list)


class Planner:
    def plan(self, bot, profile: StrategyProfile, advice: Advice) -> ExecutionPlan:
        bases = max(1, bot.townhalls.amount)
        reasons: List[str] = []

        plan = ExecutionPlan(profile_name=profile.name, stance=profile.stance)

        # ---- economy -------------------------------------------------------
        plan.drone_target = min(profile.max_drones, profile.drones_per_base * bases)
        plan.queen_target = min(profile.queens_per_base * bases, 6)
        plan.gas_target = min(profile.gas_per_base * bases, 8)
        plan.base_target = profile.expand_to

        # Under a defensive emergency with too little army, freeze drone/base
        # growth and pour larva into units instead (the library's call, not ours).
        emergency = advice.defense.emergency or advice.defense.prioritize_army
        thin = bot.supply_army < max(8.0, (advice.enemy_estimate.army_supply or 0) * 0.8)
        if profile.all_in:
            plan.expand_now_ok = False
        elif emergency and thin:
            plan.drone_target = min(plan.drone_target, bot.supply_workers + 2)
            plan.expand_now_ok = False
            reasons.append("emergency+thin: freeze economy, larva -> army")

        # Larva split: how much of each step's larva goes to drones vs army.
        # Rushing the *initial* economy pays off, so drone hard until a baseline
        # is up; after that, split by stance so army grows alongside the economy
        # instead of hoarding larva into a full drone saturation first.
        plan.larva_econ_share = self._econ_share(bot, profile, plan, emergency, thin)

        # ---- army composition ---------------------------------------------
        comp = dict(profile.army)
        tech = list(profile.army_units)

        # Detection: if the enemy has cloak/burrow and we lack detection, fold an
        # Overseer into the composition and mark the need so defense adds a Spore.
        if advice.defense.need_detection or bot.enemy_memory.get("enemy_has_cloak"):
            plan.need_detection = True
            if U.OVERSEER not in tech:
                tech.append(U.OVERSEER)

        # Anti-air: if the enemy shows air and our comp has no anti-air, add
        # hydralisks (the generic Zerg anti-air) to the composition.
        if bot.enemy_memory.get("enemy_has_air"):
            if not any(u in zerg_data.ANTIAIR_UNITS for u in comp):
                comp[U.HYDRALISK] = comp.get(U.HYDRALISK, 0.0) + 0.4
                if U.HYDRALISK not in tech:
                    tech.append(U.HYDRALISK)
                reasons.append("enemy air: add hydralisks for anti-air")

        plan.army_composition = _normalise(comp)
        plan.tech_targets = tech
        plan.prerequisite_structures = zerg_data.all_prerequisite_structures(tech)
        plan.tier_target = zerg_data.tier_required(tech)
        plan.upgrade_targets = list(profile.upgrades)

        # ---- static defense ------------------------------------------------
        # Start from the profile's per-base intent, then take the max with the
        # library's emergency recommendation so a detected all-in always gets
        # enough regardless of how greedy the base strategy is.
        plan.spines = int(round(profile.spines_per_base * bases))
        plan.spores = int(round(profile.spores_per_base * bases))
        lib_static = advice.defense.static_defense
        if lib_static > 0:
            plan.spines = max(plan.spines, lib_static)
            reasons.append(f"library wants {lib_static} static defense")
        if plan.need_detection:
            plan.spores = max(plan.spores, 1)

        # ---- combat stance -------------------------------------------------
        plan.attack_supply = profile.attack_supply
        plan.regroup_supply = profile.regroup_supply
        plan.pull_workers = advice.defense.pull_workers

        # An all-in attacks as soon as it has its critical mass, full stop.
        if profile.all_in:
            plan.combat_stance = ATTACK if bot.supply_army >= profile.attack_supply else HOLD
        elif advice.defense.hold_position:
            plan.combat_stance = DEFEND
            reasons.append("library: hold at home")
        else:
            plan.combat_stance = self._offensive_stance(bot, profile, advice, reasons)

        # Power-timing nudge: if we are clearly ahead *now*, don't sit on the
        # lead -- lower the commit threshold so we use it before it fades.
        if advice.timing == PowerTiming.AHEAD_NOW and not profile.all_in:
            plan.attack_supply = max(profile.regroup_supply + 6,
                                     profile.attack_supply * 0.7)
            reasons.append("ahead now: press the timing")

        plan.reasons = reasons
        return plan

    def _econ_share(self, bot, profile, plan, emergency, thin) -> float:
        workers = bot.supply_workers
        if profile.all_in:
            return 0.1
        if workers >= plan.drone_target:
            return 0.0
        # Rush the opening economy hard, then *taper*: as the worker base fills
        # in, larva should shift to army rather than hoarding drones up to the
        # cap (which starves the army in long games). Greedier stances taper
        # more slowly, but every stance ends up army-heavy near saturation.
        if workers < 20:
            return 1.0
        early = {
            Stance.CHEESE: 0.15, Stance.TIMING: 0.45, Stance.STANDARD: 0.55,
            Stance.GREEDY: 0.7, Stance.TURTLE: 0.6,
        }.get(profile.stance, 0.55)
        prog = max(0.0, min(1.0, (workers - 20) / max(1.0, plan.drone_target - 20)))
        share = early * (1.0 - prog) + 0.15 * prog
        if emergency and thin:
            share = min(share, 0.2)   # pour larva into army under threat
        return share

    def _offensive_stance(self, bot, profile, advice, reasons) -> str:
        eng = advice.engagement.verdict
        army = bot.supply_army
        # Don't throw a handful of units across the map: only commit the army
        # with a real critical mass (or when about to cap, or on a genuinely
        # favourable read with enough supply to matter).
        commit_floor = max(8.0, 0.5 * profile.attack_supply)
        if bot.supply_used >= 190:            # about to cap -- move out
            reasons.append("near max supply")
            return ATTACK
        if army >= profile.attack_supply and eng != Engagement.AVOID:
            return ATTACK
        if eng == Engagement.ENGAGE and army >= commit_floor:
            reasons.append("engagement favourable with critical mass")
            return ATTACK
        # Harass to keep pressure / cover our own greed when the profile allows.
        if profile.harass and advice.harass.should_harass and army >= 8:
            return HARASS
        return HOLD


def _normalise(comp: Dict[U, float]) -> Dict[U, float]:
    total = sum(v for v in comp.values() if v > 0)
    if total <= 0:
        return {}
    return {u: v / total for u, v in comp.items() if v > 0}
