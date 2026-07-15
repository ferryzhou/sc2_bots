"""Openings: classify, reproduce, and verify standard opening builds.

The opening (first ~3 minutes) is the most standardized part of the game --
analysis of 66 pro replays (``analysis/OPENING_PATTERNS.md``) shows each race has
a handful of recognizable opening *families*, each an almost-deterministic
sequence of buildings at tight timings and placements. This module turns that
into reusable behavior:

- ``classify_opening`` -- name the family from scouted structures (the single
  source of truth; ``analysis/extract_openings.py`` imports it so the reference
  data is bucketed exactly the way a bot will classify an opponent live).
- ``Opening`` / ``OPENINGS`` -- the canonical builds, loaded from the mined
  reference data in ``data/openings.json`` (build order, timings, placement
  zones, and economy/unit reference bands).
- ``OpeningExecutor`` -- reproduce an opening: given what the bot has built so
  far, return the next structure + where to place it.
- ``verify_opening`` -- check a played opening's telemetry (economy, units,
  placements, positions) against the reference bands and report deviations.

Pure Python: no ``sc2`` import, so it unit-tests without StarCraft II. A bot maps
``Placement`` zones and structure names onto its own build/placement calls.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional, Sequence

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "openings.json")


class Placement(Enum):
    """Where a structure goes, as a zone a bot can map to its own placement."""
    MAIN = "main"             # in the main base / mineral line / core
    RAMP_WALL = "ramp_wall"   # the ramp / wall-off at the main's edge
    NATURAL = "natural"       # at (or powering) the natural expansion
    GAS = "gas"               # on a vespene geyser
    OUTER = "outer"           # third-base / forward staging area
    FORWARD = "forward"       # proxy: across the map, near the enemy

    @classmethod
    def from_zone(cls, zone: Optional[str]) -> "Placement":
        for p in cls:
            if p.value == zone:
                return p
        return cls.MAIN


# ----------------------------------------------------------------------------
# Classification -- the single source of truth (pure rules over scouted signals)
# ----------------------------------------------------------------------------

def classify_opening(race: str,
                     structures: Sequence[tuple],
                     first_gas: Optional[float],
                     expand_time: Optional[float]) -> str:
    """Name the opening family from what we've seen the opponent build.

    ``structures`` is a sequence of ``(name, second, zone)`` for the opponent's
    placed buildings (normalized base names: Gateway not WarpGate, Hatchery not
    Lair, etc.). ``first_gas`` / ``expand_time`` are seconds or ``None``. Returns
    a family key present in :data:`OPENINGS` (or a ``*_standard`` fallback).
    Mirrors the archetypes in ``STRATEGY.md`` at opening resolution.
    """
    first: dict = {}
    for name, sec, _zone in structures:
        first.setdefault(name, sec)
    zones = {name: zone for name, _sec, zone in structures}

    if race == "Protoss":
        if first.get("Forge") is not None and first["Forge"] < 60:
            return "protoss_forge_fast"
        if zones.get("Pylon") == "forward" or zones.get("Gateway") == "forward":
            return "protoss_proxy"
        if expand_time is not None:
            return "protoss_gate_expand"
        gates = sum(1 for n, _s, _z in structures if n == "Gateway")
        if gates >= 3:
            return "protoss_gate_allin"
        return "protoss_one_base"
    if race == "Terran":
        if zones.get("Barracks") == "forward":
            return "terran_proxy_rax"
        if expand_time is not None:
            return "terran_rax_expand"
        raxes = sum(1 for n, _s, _z in structures if n == "Barracks")
        if raxes >= 2:
            return "terran_2rax"
        return "terran_one_base"
    if race == "Zerg":
        pool = first.get("SpawningPool")
        if pool is not None and pool < 45:
            return "zerg_pool_rush"
        if expand_time is not None and (pool is None or expand_time <= pool):
            return "zerg_hatch_first"
        if pool is not None and pool < 90:
            return "zerg_pool_first"
        if first_gas is not None and (pool is None or first_gas < pool):
            return "zerg_gas_first"
        return "zerg_standard"
    return "unknown"


# ----------------------------------------------------------------------------
# Opening data model
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class BuildStep:
    index: int
    structure: str
    placement: Placement
    at_second: Optional[float]   # median placement time in the reference data
    pct: int                     # % of the family that built it (confidence)


@dataclass(frozen=True)
class Band:
    median: float
    p25: float
    p75: float

    @classmethod
    def of(cls, d: Optional[dict]) -> Optional["Band"]:
        if not d:
            return None
        return cls(d["median"], d["p25"], d["p75"])


@dataclass
class Opening:
    name: str
    race: str
    n: int                       # sample size behind this canonical opening
    steps: list                  # list[BuildStep] in modal order
    first_gas: Optional[Band]
    expand: Optional[Band]
    expand_pct: int
    economy: dict                # {mark_seconds: {metric: Band}}
    units: dict                  # {unit_name: {"count": Band, "first": Band, "pct": int}}

    def step_for(self, structure: str) -> Optional[BuildStep]:
        for s in self.steps:
            if s.structure == structure:
                return s
        return None

    def workers_at(self, second: int) -> Optional[Band]:
        e = self.economy.get(second) or self.economy.get(str(second))
        return Band.of(e["workers"]) if e else None

    def summary(self) -> str:
        order = " > ".join(f"{s.structure}" for s in self.steps)
        return f"{self.name} (n={self.n}): {order}"


def _build_opening(name: str, fam: dict) -> Opening:
    order = fam["modal_order"]
    structs = fam["structures"]
    steps = []
    for i, s in enumerate(order):
        info = structs.get(s, {})
        t = info.get("timing") or {}
        steps.append(BuildStep(
            index=i, structure=s,
            placement=Placement.from_zone(info.get("zone")),
            at_second=t.get("median"), pct=info.get("pct", 0)))
    econ = {int(m): v for m, v in fam.get("economy", {}).items()}
    return Opening(
        name=name, race=_race_of(name), n=fam["n"], steps=steps,
        first_gas=Band.of(fam.get("first_gas")),
        expand=Band.of(fam.get("expand")),
        expand_pct=fam.get("expand_pct", 0),
        economy=econ, units=fam.get("units", {}))


def _race_of(family: str) -> str:
    return {"protoss": "Protoss", "terran": "Terran",
            "zerg": "Zerg"}.get(family.split("_", 1)[0], "Unknown")


def _load(path: str = DATA_PATH) -> dict:
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return {name: _build_opening(name, fam)
            for name, fam in data.get("families", {}).items()}


OPENINGS: dict = _load()


def openings_for_race(race: str) -> list:
    return [o for o in OPENINGS.values() if o.race == race]


def get_opening(name: str) -> Optional[Opening]:
    return OPENINGS.get(name)


def best_opening(race: str) -> Optional[Opening]:
    """The most common (largest-sample) opening for a race -- a safe default."""
    ranked = sorted(openings_for_race(race), key=lambda o: o.n, reverse=True)
    return ranked[0] if ranked else None


# ----------------------------------------------------------------------------
# Reproduce
# ----------------------------------------------------------------------------

class OpeningExecutor:
    """Drive a bot through an opening's build order.

    The bot each step reports what it *has* (built + in-progress) as a mapping
    ``{structure_name: count}``; :meth:`next_step` returns the next structure to
    place (with its placement zone) or ``None`` when the opening is complete.
    Order is reproduced faithfully; exact timing emerges from the bot's economy,
    which is what keeps it robust across maps and interruptions (e.g. rebuilding
    after a building dies just re-satisfies that step).
    """

    def __init__(self, opening: Opening):
        self.opening = opening
        # cumulative count of each structure required through each step
        self._required = []
        seen: dict = {}
        for s in opening.steps:
            seen[s.structure] = seen.get(s.structure, 0) + 1
            self._required.append((s, seen[s.structure]))

    def next_step(self, have: Mapping[str, int]) -> Optional[BuildStep]:
        for step, need in self._required:
            if have.get(step.structure, 0) < need:
                return step
        return None

    def progress(self, have: Mapping[str, int]) -> float:
        done = sum(1 for step, need in self._required
                   if have.get(step.structure, 0) >= need)
        return done / len(self._required) if self._required else 1.0

    def is_complete(self, have: Mapping[str, int]) -> bool:
        return self.next_step(have) is None


# ----------------------------------------------------------------------------
# Verify
# ----------------------------------------------------------------------------

@dataclass
class Deviation:
    category: str    # "missing" | "timing" | "placement" | "economy" | "units"
    detail: str
    severity: str    # "info" | "warn" | "major"


def _band_ok(value, band: Optional[Band], slack: float, floor: float = 0.0) -> bool:
    if band is None:
        return True
    # A near-zero IQR (pros hit the same number every game) would make the band
    # unrealistically strict; `floor` guarantees a minimum cushion so only a
    # genuine departure -- not one worker of noise -- is flagged.
    spread = max(band.p75 - band.p25, floor)
    return band.p25 - slack * spread <= value <= band.p75 + slack * spread


def verify_opening(opening: Opening, telemetry: dict,
                   timing_slack_s: float = 20.0,
                   econ_slack: float = 0.5) -> list:
    """Compare a played opening to the canonical reference; list deviations.

    ``telemetry`` mirrors ``analysis/extract_openings.extract_player``::

        {"buildings": [{"t": sec, "s": name, "zone": zone}, ...],
         "economy":   {mark: {"workers": n, "supply": n, "mins_rate": n}},
         "units":     {name: count}}

    Checks each reference step was built (and roughly on time and in the right
    zone), and that the economy at each mark sits within the reference band.
    """
    devs: list = []
    built = {}
    zone_of = {}
    for b in telemetry.get("buildings", []):
        built.setdefault(b["s"], b["t"])
        zone_of.setdefault(b["s"], b.get("zone"))

    for step in opening.steps:
        if step.pct < 60:
            continue  # only hold the build to structures the family reliably makes
        if step.structure not in built:
            devs.append(Deviation("missing",
                        f"never built {step.structure} "
                        f"(ref {step.pct}% @ {_mmss(step.at_second)})", "major"))
            continue
        t = built[step.structure]
        if step.at_second is not None and t > step.at_second + timing_slack_s:
            devs.append(Deviation("timing",
                        f"{step.structure} late: {_mmss(t)} vs ref "
                        f"{_mmss(step.at_second)}", "warn"))
        if step.placement != Placement.GAS:
            z = zone_of.get(step.structure)
            if z and z != step.placement.value:
                devs.append(Deviation("placement",
                            f"{step.structure} in '{z}', ref "
                            f"'{step.placement.value}'", "info"))

    econ = telemetry.get("economy", {})
    for mark, ref in opening.economy.items():
        got = econ.get(mark) or econ.get(str(mark))
        if not got:
            continue
        for metric in ("workers", "supply"):
            band = Band.of(ref.get(metric))
            if got.get(metric) is not None and not _band_ok(
                    got[metric], band, econ_slack, floor=3):
                devs.append(Deviation("economy",
                            f"{metric}@{_mmss(mark)}={got[metric]} vs ref "
                            f"~{band.median if band else '?'}", "warn"))

    for uname, uref in opening.units.items():
        if uref.get("pct", 0) < 60:
            continue
        have = telemetry.get("units", {}).get(uname, 0)
        band = Band.of(uref.get("count"))
        if band and have == 0 and band.median >= 1:
            devs.append(Deviation("units",
                        f"no {uname} (ref ~{band.median})", "info"))
    return devs


def _mmss(sec) -> str:
    if sec is None:
        return "?"
    return f"{int(sec) // 60}:{int(sec) % 60:02d}"
