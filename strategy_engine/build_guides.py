"""Scripted build guides: reproduce a published build order step by step.

Complements ``strategy_engine.openings`` (statistical, structure-level averages
mined from many replays) with *exact, named* build orders authored by pros and
ingested from spawningtool.com (``analysis/spawningtool_build.py``). A guide is a
full ordered script -- structures, units, AND upgrades -- with supply/time
triggers, e.g. "Serral's Safe Macro Opener".

This module makes a guide *reproducible*:

- ``NAME_TO_UNIT`` / ``NAME_TO_UPGRADE`` map each human step name to the sc2
  id *token* a bot issues (kept as strings so this stays ``sc2``-free; a bot
  resolves ``getattr(UnitTypeId, token)`` / ``getattr(UpgradeId, token)``).
- ``ScriptedBuild.coverage`` reports what fraction of a guide maps to game
  entities we can actually issue -- i.e. "where we can reproduce these".
- ``BuildExecutor`` walks the script: given what the bot has produced so far,
  it returns the next action (with its supply/time target) to execute.

Pure Python: no ``sc2`` import, so it unit-tests without StarCraft II.
"""

from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import dataclass, field
from typing import Mapping, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "build_guides")

# spawningtool display name -> sc2 UnitTypeId token (structures + units)
NAME_TO_UNIT = {
    # Protoss
    "Pylon": "PYLON", "Gateway": "GATEWAY", "Nexus": "NEXUS",
    "Assimilator": "ASSIMILATOR", "Cybernetics Core": "CYBERNETICSCORE",
    "Forge": "FORGE", "Twilight Council": "TWILIGHTCOUNCIL",
    "Robotics Facility": "ROBOTICSFACILITY", "Stargate": "STARGATE",
    "Photon Cannon": "PHOTONCANNON", "Shield Battery": "SHIELDBATTERY",
    "Probe": "PROBE", "Zealot": "ZEALOT", "Stalker": "STALKER",
    "Adept": "ADEPT", "Sentry": "SENTRY", "Oracle": "ORACLE",
    "Phoenix": "PHOENIX", "Immortal": "IMMORTAL", "Observer": "OBSERVER",
    # Terran
    "Supply Depot": "SUPPLYDEPOT", "Barracks": "BARRACKS", "Refinery": "REFINERY",
    "Command Center": "COMMANDCENTER", "Orbital Command": "ORBITALCOMMAND",
    "Factory": "FACTORY", "Starport": "STARPORT", "Engineering Bay": "ENGINEERINGBAY",
    "Bunker": "BUNKER", "Barracks Reactor": "BARRACKSREACTOR",
    "Barracks Tech Lab": "BARRACKSTECHLAB", "Factory Tech Lab": "FACTORYTECHLAB",
    "Factory Reactor": "FACTORYREACTOR", "Starport Tech Lab": "STARPORTTECHLAB",
    "Starport Reactor": "STARPORTREACTOR",
    "SCV": "SCV", "Marine": "MARINE", "Marauder": "MARAUDER", "Reaper": "REAPER",
    "Hellion": "HELLION", "Siege Tank": "SIEGETANK", "Medivac": "MEDIVAC",
    "Widow Mine": "WIDOWMINE", "Liberator": "LIBERATOR", "Cyclone": "CYCLONE",
    "Viking": "VIKINGFIGHTER", "Banshee": "BANSHEE", "Raven": "RAVEN",
    "Ghost": "GHOST", "Thor": "THOR", "Battlecruiser": "BATTLECRUISER",
    "Armory": "ARMORY", "Fusion Core": "FUSIONCORE", "Ghost Academy": "GHOSTACADEMY",
    "Sensor Tower": "SENSORTOWER", "Missile Turret": "MISSILETURRET",
    "Planetary Fortress": "PLANETARYFORTRESS",
    # Zerg
    "Hatchery": "HATCHERY", "Spawning Pool": "SPAWNINGPOOL", "Extractor": "EXTRACTOR",
    "Lair": "LAIR", "Baneling Nest": "BANELINGNEST", "Roach Warren": "ROACHWARREN",
    "Evolution Chamber": "EVOLUTIONCHAMBER", "Hydralisk Den": "HYDRALISKDEN",
    "Infestation Pit": "INFESTATIONPIT", "Spire": "SPIRE",
    "Spine Crawler": "SPINECRAWLER", "Spore Crawler": "SPORECRAWLER",
    "Drone": "DRONE", "Overlord": "OVERLORD", "Overseer": "OVERSEER",
    "Queen": "QUEEN", "Zergling": "ZERGLING", "Baneling": "BANELING",
    "Roach": "ROACH", "Ravager": "RAVAGER", "Hydralisk": "HYDRALISK",
    "Mutalisk": "MUTALISK",
}

# spawningtool display name -> sc2 UpgradeId token (research steps)
NAME_TO_UPGRADE = {
    "Metabolic Boost": "ZERGLINGMOVEMENTSPEED",
    "Pneumatized Carapace": "OVERLORDSPEED",
    "Centrifugal Hooks": "CENTRIFICALHOOKS",
    "Glial Reconstitution": "GLIALRECONSTITUTION",
    "Zerg Ground Armor Level 1": "ZERGGROUNDARMORSLEVEL1",
    "Zerg Melee Weapons Level 1": "ZERGMELEEWEAPONSLEVEL1",
    "Zerg Missile Weapons Level 1": "ZERGMISSILEWEAPONSLEVEL1",
    "Adrenal Glands": "ZERGLINGATTACKSPEED",
    "Warp Gate": "WARPGATERESEARCH",
    "Charge": "CHARGE", "Blink": "BLINKTECH",
    "Stimpack": "STIMPACK", "Combat Shield": "SHIELDWALL",
    "Concussive Shells": "PUNISHERGRENADES",
    # Terran mech/bio/air upgrades (levels share a stem)
    "Terran Infantry Armor Level 1": "TERRANINFANTRYARMORSLEVEL1",
    "Terran Infantry Armor Level 2": "TERRANINFANTRYARMORSLEVEL2",
    "Terran Infantry Armor Level 3": "TERRANINFANTRYARMORSLEVEL3",
    "Terran Infantry Weapons Level 1": "TERRANINFANTRYWEAPONSLEVEL1",
    "Terran Infantry Weapons Level 2": "TERRANINFANTRYWEAPONSLEVEL2",
    "Terran Infantry Weapons Level 3": "TERRANINFANTRYWEAPONSLEVEL3",
    "Terran Ship Weapons Level 1": "TERRANSHIPWEAPONSLEVEL1",
    "Terran Ship Weapons Level 2": "TERRANSHIPWEAPONSLEVEL2",
    "Terran Vehicle Weapons Level 1": "TERRANVEHICLEWEAPONSLEVEL1",
    "Terran Vehicle Weapons Level 2": "TERRANVEHICLEWEAPONSLEVEL2",
    "Terran Vehicle And Ship Armor Level 1": "TERRANVEHICLEANDSHIPARMORSLEVEL1",
    "Cloaking Field": "BANSHEECLOAK", "Personal Cloaking": "PERSONALCLOAKING",
    "Drilling Claws": "DRILLCLAWS", "Advanced Ballistics": "LIBERATORAGRANGEUPGRADE",
    "Caduceus Reactor": "MEDIVACCADUCEUSREACTOR",
}


def _base_name(name: str) -> str:
    """Strip trailing modifiers like '(Chrono Boost)' before mapping."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()


@dataclass(frozen=True)
class BuildAction:
    index: int
    action: str                 # "build" | "train" | "research"
    name: str                   # human display name
    count: int
    at_supply: Optional[int]
    at_second: Optional[int]
    note: str = ""

    @property
    def kind(self) -> str:
        return "upgrade" if self.action == "research" else "unit"

    @property
    def token(self) -> Optional[str]:
        table = NAME_TO_UPGRADE if self.action == "research" else NAME_TO_UNIT
        return table.get(_base_name(self.name))

    @property
    def reproducible(self) -> bool:
        return self.token is not None

    @property
    def chrono(self) -> bool:
        return "chrono" in self.name.lower()


@dataclass
class ScriptedBuild:
    id: int
    title: str
    race: Optional[str]
    matchup: Optional[str]
    source: str
    actions: list                # list[BuildAction]

    def build_steps(self) -> list:
        """Only the real build/train/research steps (drops note annotations)."""
        return [a for a in self.actions if a.action in ("build", "train", "research")]

    def coverage(self) -> dict:
        steps = self.build_steps()
        total = len(steps)
        mapped = sum(1 for a in steps if a.reproducible)
        return {"mapped": mapped, "total": total,
                "fraction": (mapped / total) if total else 1.0}

    def unmapped(self) -> list:
        return sorted({a.name for a in self.build_steps() if not a.reproducible})

    def summary(self) -> str:
        c = self.coverage()
        return (f"{self.title} [{self.matchup or self.race}] -- {c['total']} steps, "
                f"{round(100 * c['fraction'])}% reproducible")


def _build_from(data: dict) -> ScriptedBuild:
    actions = [BuildAction(index=s["i"], action=s["action"], name=s["name"],
                           count=s.get("count", 1), at_supply=s.get("supply"),
                           at_second=s.get("t"), note=s.get("note", ""))
               for s in data.get("steps", [])]
    return ScriptedBuild(id=data["id"], title=data.get("title", str(data["id"])),
                         race=data.get("race"), matchup=data.get("matchup"),
                         source=data.get("source", ""), actions=actions)


def _load(dir_path: str = DATA_DIR) -> dict:
    out = {}
    for path in sorted(glob.glob(os.path.join(dir_path, "*.json"))):
        try:
            with open(path) as f:
                data = json.load(f)
            out[data["id"]] = _build_from(data)
        except (OSError, ValueError, KeyError):
            continue
    return out


BUILD_GUIDES: dict = _load()


def guides_for(race: Optional[str] = None, matchup: Optional[str] = None) -> list:
    out = list(BUILD_GUIDES.values())
    if race:
        out = [b for b in out if b.race == race]
    if matchup:
        out = [b for b in out if b.matchup == matchup]
    return out


def get_build(build_id: int) -> Optional[ScriptedBuild]:
    return BUILD_GUIDES.get(build_id)


class BuildExecutor:
    """Walk a scripted build: return the next action to execute.

    The bot reports what it has produced so far as ``{key: count}`` where key is
    the sc2 token (preferred) or the display name; :meth:`next_action` returns
    the first script action not yet satisfied. ``is_due`` tells whether the
    current supply/time has reached that action's target, so a bot can pace to
    the script's benchmarks rather than racing ahead.
    """

    def __init__(self, build: ScriptedBuild, reproducible_only: bool = True):
        self.build = build
        self.actions = [a for a in build.actions
                        if a.reproducible or not reproducible_only]
        # cumulative required count per key, in order
        self._required = []
        seen: dict = {}
        for a in self.actions:
            key = a.token or a.name
            seen[key] = seen.get(key, 0) + a.count
            self._required.append((a, key, seen[key]))

    def _have(self, have: Mapping, action: BuildAction) -> int:
        return have.get(action.token, have.get(action.name, 0)) if action.token \
            else have.get(action.name, 0)

    def next_action(self, have: Mapping) -> Optional[BuildAction]:
        for action, key, need in self._required:
            if have.get(key, self._have(have, action)) < need:
                return action
        return None

    @staticmethod
    def is_due(action: BuildAction, supply: Optional[int],
               seconds: Optional[float]) -> bool:
        if action.at_supply is not None and supply is not None:
            return supply >= action.at_supply
        if action.at_second is not None and seconds is not None:
            return seconds >= action.at_second
        return True

    def progress(self, have: Mapping) -> float:
        done = sum(1 for a, key, need in self._required
                   if have.get(key, self._have(have, a)) >= need)
        return done / len(self._required) if self._required else 1.0

    def is_complete(self, have: Mapping) -> bool:
        return self.next_action(have) is None
