"""Production planner: convert a mined economy into army at professional tempo.

The failure this fixes (measured on Aiur vs the pro benchmark): the bot *out-mines*
the pro yet fields a fraction of the army, because production is idle. Three
mechanisms, all reproduced from pro replays as the fix:

  1. Too few facilities for the income  -- pros add a Gateway/Robo/Stargate as soon
     as the income outruns current throughput (5 gates by 5:30, ~10 facilities by
     max), so there is always somewhere to spend.
  2. Warpgates never warping                -- the entire gateway army engine. A pro
     warps every warpgate the instant it comes off cooldown; an idle warpgate is a
     macro error. (Aiur made 10 gateway units in the 9 min AFTER warp gate research
     -- essentially none: no warp-in logic existed.)
  3. One resource floods                    -- a Zealot costs no gas, so a mineral
     army floats gas (Aiur floated 900 gas). Pros drain whatever is piling by
     picking the unit that spends it (Stalker/Immortal/Void Ray for gas).

This module is sc2-free and framework-agnostic. The caller passes a
:class:`ProductionState` (its resources, income, how many producers are *ready to
build right now*, and which tech it has) plus a desired composition; it answers
two questions:

    plan = plan_production(state, composition)
    plan.add_gateways / add_robos / add_stargates   # facilities to start now
    plan.gateway_units / robo_units / stargate_units # tokens to make NOW, one per
                                                      # ready producer, resource- and
                                                      # supply-balanced

Execution (where to place a warp-in, which idle producer to use) stays in the bot;
every *decision* -- how many facilities, what to build, which resource to drain --
lives here so it is reusable and testable without a game.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional


@dataclass(frozen=True)
class UnitSpec:
    """A producible unit: its cost, supply, and the tech building it needs (if any)."""
    token: str
    minerals: int
    vespene: int
    supply: int
    tech: Optional[str] = None   # required tech building key, or None if always available


# Gateway MASS roster -- the pro core you actually a-move with: Zealot is the
# pure-mineral sink, Stalker the staple gas sink. Deliberately just these two so
# the resource-drain rule is clean (gas floats -> Stalker; minerals float ->
# Zealot). Adept, Sentry, and High Templar are excluded on purpose: they are
# tactical adds you want a fixed handful of (harass / guardian shield / storm),
# never a massed line -- the bot's composition layer adds them by count. A "drain
# the most gas" planner set loose on them mono-masses the mid-cost one (we saw it
# field 90+ Adepts because Adept, at 25 gas, was the priciest gas unit still
# affordable once a batch drained gas below the Stalker's 50).
GATEWAY_UNITS = [
    UnitSpec("ZEALOT", 100, 0, 2),
    UnitSpec("STALKER", 125, 50, 2, "CYBERNETICSCORE"),
]
ROBO_UNITS = [
    UnitSpec("OBSERVER", 25, 75, 1),
    UnitSpec("IMMORTAL", 275, 100, 4),
    UnitSpec("COLOSSUS", 300, 200, 6, "ROBOTICSBAY"),
]
STARGATE_UNITS = [
    UnitSpec("PHOENIX", 150, 100, 2),
    UnitSpec("VOIDRAY", 250, 150, 4),
    UnitSpec("CARRIER", 350, 250, 6, "FLEETBEACON"),
]


@dataclass(frozen=True)
class ProductionState:
    """Everything the planner needs, all plain numbers -- no sc2 objects.

    ``ready_*`` is the count of that producer that can start a unit THIS step (an
    idle Gateway, an off-cooldown Warpgate, an idle Robo/Stargate). ``have_tech`` is
    the set of tech-building keys that are built and ready (e.g. ``CYBERNETICSCORE``,
    ``ROBOTICSBAY``, ``TEMPLARARCHIVE``, ``FLEETBEACON``, and the producers
    ``ROBOTICSFACILITY`` / ``STARGATE`` themselves, so their desired count is unlocked).
    """
    minerals: float
    vespene: float
    mineral_income: float          # per minute (collection rate)
    vespene_income: float
    supply_left: float
    bases: int
    gateways: int                  # gateways + warpgates we own (any state)
    robos: int
    stargates: int
    ready_gateways: int
    ready_robos: int
    ready_stargates: int
    have_tech: FrozenSet[str] = frozenset()
    need_observer: bool = False    # we have no observer and want detection


@dataclass
class ProductionPlan:
    add_gateways: int = 0
    add_robos: int = 0
    add_stargates: int = 0
    gateway_units: List[str] = field(default_factory=list)
    robo_units: List[str] = field(default_factory=list)
    stargate_units: List[str] = field(default_factory=list)


# --- facility targets: enough production to spend the income, capped by bases ----
# One saturated warpgate absorbs very roughly ~250 minerals/min (a ~112-mineral
# gateway unit every ~28s). So aim gateway count at mineral_income/250, floored to
# 1 and capped so we don't build more than the bases can power/afford. This
# reproduces the pro's "5 gates by 5:30" without hardcoding a timing.
MINS_PER_GATEWAY = 250.0


def desired_gateways(state: ProductionState) -> int:
    by_income = round(state.mineral_income / MINS_PER_GATEWAY)
    return int(max(1, min(by_income, 3 * max(1, state.bases))))


def desired_robos(state: ProductionState, comp) -> int:
    if "ROBOTICSFACILITY" not in state.have_tech:
        return 0
    want = 2 if (getattr(comp, "need_splash", False) or state.vespene_income > 250) else 1
    return min(want, max(1, state.bases))


def desired_stargates(state: ProductionState, comp) -> int:
    if "STARGATE" not in state.have_tech:
        return 0
    heavy = getattr(comp, "need_anti_air", False) and state.vespene_income > 300
    return 2 if heavy else 1


def _prefer_gas(state: ProductionState) -> bool:
    """True when gas is the resource piling up, so we should drain it. Gas floats
    whenever a mineral-heavy (Zealot) army leaves the geysers unspent; this catches
    it from either a fat bank or a gas-rich income mix."""
    return state.vespene >= 75 and (state.vespene >= 0.5 * max(1.0, state.minerals)
                                    or state.vespene_income >= state.mineral_income)


def _choose(specs: List[UnitSpec], m: float, v: float, sup: float,
            tech: FrozenSet[str], prefer_gas: bool) -> Optional[UnitSpec]:
    ok = [s for s in specs
          if (s.tech is None or s.tech in tech)
          and s.minerals <= m and s.vespene <= v and s.supply <= sup]
    if not ok:
        return None
    # drain the piling resource: most gas when gas floats, else least gas (mineral dump)
    return max(ok, key=lambda s: s.vespene) if prefer_gas else min(ok, key=lambda s: s.vespene)


def _fill(specs, ready, m, v, sup, tech, prefer_gas):
    """Saturate ``ready`` producers, reserving resources/supply as we assign so the
    batch is jointly affordable. Returns (tokens, remaining_m, remaining_v, remaining_sup)."""
    out = []
    for _ in range(int(ready)):
        pick = _choose(specs, m, v, sup, tech, prefer_gas)
        if pick is None:
            break
        out.append(pick.token)
        m -= pick.minerals
        v -= pick.vespene
        sup -= pick.supply
    return out, m, v, sup


def plan_production(state: ProductionState, comp=None) -> ProductionPlan:
    """The full plan: facilities to add, and units to make now (resource-balanced,
    supply-capped, saturating every ready producer). Robo/Stargate get first claim
    on gas (their units are the biggest gas sinks); gateways spend what's left."""
    plan = ProductionPlan()

    # facilities: add toward the income-scaled target (one at a time; the caller's
    # spend allocator decides if we can afford it without starving an expansion).
    plan.add_gateways = max(0, desired_gateways(state) - state.gateways)
    plan.add_robos = max(0, desired_robos(state, comp) - state.robos)
    plan.add_stargates = max(0, desired_stargates(state, comp) - state.stargates)

    m, v, sup = state.minerals, state.vespene, state.supply_left
    prefer_gas = _prefer_gas(state)

    # ROBO first (heaviest gas sink + detection). Observer once, then Colossus for
    # splash if the bay is up, else Immortal.
    robo_specs = []
    if state.need_observer:
        robo_specs = [s for s in ROBO_UNITS if s.token == "OBSERVER"]
    if not robo_specs:
        want_col = getattr(comp, "need_splash", False) and "ROBOTICSBAY" in state.have_tech
        robo_specs = [s for s in ROBO_UNITS
                      if s.token == ("COLOSSUS" if want_col else "IMMORTAL")]
        # allow falling back to the other if the preferred is unaffordable
        robo_specs += [s for s in ROBO_UNITS if s.token in ("IMMORTAL", "COLOSSUS")
                       and s not in robo_specs]
    plan.robo_units, m, v, sup = _fill(robo_specs, state.ready_robos, m, v, sup,
                                       state.have_tech, prefer_gas=True)

    # STARGATE (anti-air / air escalation): Void Ray by default, Phoenix vs light air.
    sg_specs = STARGATE_UNITS
    plan.stargate_units, m, v, sup = _fill(sg_specs, state.ready_stargates, m, v, sup,
                                           state.have_tech, prefer_gas=True)

    # GATEWAY: the bulk. Drain whichever of min/gas is piling; supply-capped.
    plan.gateway_units, m, v, sup = _fill(GATEWAY_UNITS, state.ready_gateways, m, v, sup,
                                          state.have_tech, prefer_gas)
    return plan
