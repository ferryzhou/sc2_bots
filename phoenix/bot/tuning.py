"""Cross-entropy parameter tuner persisted across games.

Adapted from the design of 12PoolBot's `leitwerk` optimizer (xNES there;
diagonal-Gaussian CEM here for simplicity): each game draws one parameter
sample from the current search distribution, reports a lexicographic
(outcome, efficiency) objective at game end, and when a batch fills the
distribution moves toward the elite half. State lives in the bot data dir
(`data/tuning.json`), which AI Arena persists between ladder games, so the
bot keeps learning on the ladder as well as locally.

Serial access only: concurrent games sharing one data dir will race.
"""

import json
import math
import os
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path

BATCH_SIZE = 8
ELITE_FRAC = 0.5
MIN_SCALE_FRAC = 0.15  # never shrink exploration below this fraction of init
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Param:
    name: str
    mean: float
    scale: float
    lo: float
    hi: float


# The tunable strategy surface. Means match the previously hand-tuned
# constants so learning starts from the validated build.
SCHEMA: list[Param] = [
    Param("attack_at_supply", 26.0, 8.0, 8.0, 60.0),
    Param("pressure_valve_supply", 60.0, 12.0, 30.0, 110.0),
    Param("regroup_below_supply", 10.0, 4.0, 2.0, 24.0),
    Param("emergency_exit_seconds", 45.0, 15.0, 10.0, 120.0),
    Param("emergency_zealot_proportion", 0.5, 0.15, 0.1, 0.9),
]


class Tuner:
    def __init__(self, data_dir: Path):
        self.path = Path(data_dir) / "tuning.json"
        self.state = self._load()
        self._sample: dict[str, float] | None = None

    # -- persistence ---------------------------------------------------
    def _fresh_state(self) -> dict:
        return {
            "version": SCHEMA_VERSION,
            "params": {
                p.name: {"mean": p.mean, "scale": p.scale} for p in SCHEMA
            },
            "batch": [],  # [{"sample": {...}, "outcome": float, "eff": float}]
            "batches_done": 0,
            "games": 0,
        }

    def _load(self) -> dict:
        try:
            state = json.loads(self.path.read_text())
        except (OSError, ValueError):
            return self._fresh_state()
        if state.get("version") != SCHEMA_VERSION:
            return self._fresh_state()
        # schema reconciliation: keep learning for unchanged params,
        # (re)initialise added ones, drop removed ones
        fresh = self._fresh_state()
        merged = fresh["params"]
        for name, entry in state.get("params", {}).items():
            if name in merged:
                merged[name] = entry
        state["params"] = merged
        # drop in-flight batch results that reference a stale schema
        state["batch"] = [
            b for b in state.get("batch", [])
            if set(b.get("sample", {})) == set(merged)
        ]
        return state

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(self.state, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    # -- optimizer -----------------------------------------------------
    def ask(self) -> dict[str, float]:
        """Draw one parameter sample for this game."""
        sample: dict[str, float] = {}
        for p in SCHEMA:
            entry = self.state["params"][p.name]
            value = random.gauss(entry["mean"], entry["scale"])
            sample[p.name] = min(p.hi, max(p.lo, value))
        self._sample = sample
        return sample

    def tell(self, won: bool, tied: bool, killed_value: float,
             lost_value: float) -> None:
        """Report this game's result and update the distribution if the
        batch is complete."""
        if self._sample is None:
            return
        outcome = 1.0 if won else (0.5 if tied else 0.0)
        eff = math.log1p(max(0.0, killed_value)) - math.log1p(
            max(0.0, lost_value)
        )
        self.state["batch"].append(
            {"sample": self._sample, "outcome": outcome, "eff": eff}
        )
        self.state["games"] += 1
        self._sample = None

        if len(self.state["batch"]) >= BATCH_SIZE:
            self._update()
        self._save()

    def _update(self) -> None:
        batch = self.state["batch"]
        # lexicographic: outcome dominates, efficiency breaks ties
        batch.sort(key=lambda b: (b["outcome"], b["eff"]), reverse=True)
        elites = batch[: max(2, int(len(batch) * ELITE_FRAC))]
        by_param = {p.name: p for p in SCHEMA}
        for name, entry in self.state["params"].items():
            values = [e["sample"][name] for e in elites]
            mean = sum(values) / len(values)
            var = sum((v - mean) ** 2 for v in values) / len(values)
            init_scale = by_param[name].scale
            entry["mean"] = mean
            entry["scale"] = max(
                init_scale * MIN_SCALE_FRAC, math.sqrt(var)
            )
        self.state["batch"] = []
        self.state["batches_done"] += 1
