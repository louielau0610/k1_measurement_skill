"""Common trial scheduling utilities."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrialSpec:
    platform: str
    surface_id: str
    command_velocity: float
    repeat_index: int
    block_index: int
    trial_id: str


class TrialScheduler:
    def build_trials(
        self,
        surfaces: list[str],
        speeds: list[float],
        repeats: int,
        block_order: list[list[float]] | None = None,
        platform: str = "generic",
        prefix: str = "CAL",
    ) -> list[TrialSpec]:
        if repeats <= 0:
            raise ValueError("repeats must be positive")
        blocks = block_order or [speeds for _ in range(repeats)]
        if len(blocks) != repeats:
            raise ValueError("block_order length must equal repeats")
        trials: list[TrialSpec] = []
        for surface in surfaces:
            for block_index, block_speeds in enumerate(blocks, start=1):
                for speed in block_speeds:
                    if speed not in speeds:
                        raise ValueError(f"block speed {speed} is not in speeds")
                    repeat_index = block_index
                    code = f"U{int(round(speed * 100)):03d}"
                    trial_id = f"{prefix}_{surface}_B{block_index}_{code}_R{repeat_index}"
                    trials.append(TrialSpec(platform, surface, speed, repeat_index, block_index, trial_id))
        return trials
