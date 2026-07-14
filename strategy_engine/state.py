"""GameState: a framework-agnostic snapshot of what the strategy model needs.

The behavior modules never touch a live bot object directly; they read a plain
``GameState``. This keeps the strategic logic pure and testable without SC2, and
lets any bot (python-sc2, ares-sc2, or a test harness) feed it.

Own fields are things a bot always knows about itself. Enemy fields are what has
been *scouted* -- they are ``Optional`` because information is imperfect; unknown
values should stay ``None`` so the model can reason about uncertainty rather than
assume zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GameState:
    # --- clock ---
    game_time: float = 0.0  # seconds since game start

    # --- own economy ---
    worker_count: int = 0
    base_count: int = 1
    minerals: int = 0
    vespene: int = 0
    mineral_income: float = 0.0  # per-second collection rate, if known

    # --- own supply ---
    supply_used: int = 0
    supply_cap: int = 15
    supply_left: int = 0
    pending_supply: int = 0  # supply structures in progress (count)

    # --- own army / production / tech ---
    army_supply: float = 0.0
    production_structures: int = 0
    idle_production: int = 0  # production buildings idle with money available
    tech_structures: int = 0
    upgrades_in_progress: int = 0
    upgrades_done: int = 0
    upgrade_structures: int = 0
    idle_upgrade_structures: int = 0  # upgrade buildings idle with gas available

    # --- own mobile-harass capability ---
    has_harass_units: bool = False  # drops/air/cloak/fast raiders available

    # --- trade efficiency (cumulative resource value; the strongest empirical
    #     predictor of the winner -- see analysis/REPLAY_FINDINGS.md) ---
    value_killed: float = 0.0  # enemy resource value we have destroyed
    value_lost: float = 0.0    # our resource value the enemy has destroyed

    # --- engagement context (for the combat/should-engage decision) ---
    enemy_upgrades: Optional[int] = None   # scouted enemy upgrade count
    have_detection: bool = False           # we have detection with the army
    fighting_at_home: bool = False         # engagement near our bases/defense
    reinforcements_close: bool = False     # our production is near the fight
    have_terrain_advantage: bool = False   # high ground / choke / good surround
    positional_disadvantage: bool = False  # up a ramp / open vs. range / surrounded
    composition_favorable: Optional[bool] = None  # our comp counters theirs

    # --- scouted enemy state (None == unknown) ---
    last_scouted_time: Optional[float] = None
    enemy_base_count: Optional[int] = None
    enemy_worker_count: Optional[int] = None
    enemy_army_supply: Optional[float] = None
    enemy_production_structures: Optional[int] = None
    enemy_tech_structures: Optional[int] = None
    enemy_static_defense: Optional[int] = None
    enemy_gas_count: Optional[int] = None

    enemy_race: Optional[str] = None    # "Protoss" | "Terran" | "Zerg" | "Random" / None

    # scouted qualitative signals
    enemy_proxy: bool = False           # enemy buildings near our base
    enemy_army_moving_out: bool = False  # enemy army advancing early
    enemy_has_cloak: bool = False        # cloak/burrow tech or units seen
    enemy_has_air: bool = False          # air tech or units seen
    enemy_massing_light: bool = False    # many light units (splash target)

    # --- our exposure ---
    undefended_expansions: int = 0       # our bases without defense/detection
    incoming_harass: bool = False        # enemy raider en route / in our base

    # free-form notes a bot may attach (not used by the logic)
    notes: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ helpers
    @property
    def scouting_stale(self) -> bool:
        """True if we have never scouted or the last scout is old (>45s)."""
        if self.last_scouted_time is None:
            return True
        return (self.game_time - self.last_scouted_time) > 45.0

    @property
    def enemy_known(self) -> bool:
        """True if we have at least a base count for the enemy."""
        return self.enemy_base_count is not None

    @property
    def game_minutes(self) -> float:
        return self.game_time / 60.0

    # ---------------------------------------------------------------- adapter
    @classmethod
    def from_bot(cls, bot, enemy_memory: Optional[dict] = None) -> "GameState":
        """Best-effort snapshot from a python-sc2 ``BotAI`` instance.

        ``sc2`` is imported lazily here so importing this package never requires
        StarCraft II. ``enemy_memory`` is an optional dict a bot maintains from
        its own scouting (keys mirror the ``enemy_*`` fields above); pass it to
        populate the scouted-enemy portion, since a live snapshot only sees what
        is currently visible.
        """
        enemy_memory = enemy_memory or {}

        def _count(units):
            try:
                return units.amount
            except AttributeError:
                return len(units)

        st = cls(
            game_time=getattr(bot, "time", 0.0),
            worker_count=_count(getattr(bot, "workers", [])),
            base_count=_count(getattr(bot, "townhalls", [])) or 1,
            minerals=getattr(bot, "minerals", 0),
            vespene=getattr(bot, "vespene", 0),
            supply_used=getattr(bot, "supply_used", 0),
            supply_cap=getattr(bot, "supply_cap", 15),
            supply_left=getattr(bot, "supply_left", 0),
            army_supply=getattr(bot, "supply_army", 0.0),
        )

        # Best-effort trade values from python-sc2's score details, if present.
        score = getattr(getattr(bot, "state", None), "score", None)
        if score is not None:
            killed = getattr(score, "killed_value_units", 0) + getattr(
                score, "killed_value_structures", 0
            )
            lost = getattr(score, "lost_value_units", 0) + getattr(
                score, "lost_value_structures", 0
            )
            if killed:
                st.value_killed = float(killed)
            if lost:
                st.value_lost = float(lost)

        # Overlay any scouted-enemy memory the bot has accumulated.
        for key, value in enemy_memory.items():
            if hasattr(st, key):
                setattr(st, key, value)

        return st
