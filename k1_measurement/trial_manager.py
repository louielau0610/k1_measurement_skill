"""Trial planning skeleton for forward velocity measurement."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrialSpec:
    trial_id: str
    vx_cmd_mps: float
    repeat_index: int


def build_forward_trial_plan(vx_values_mps: list[float], repeats_per_speed: int) -> list[TrialSpec]:
    """Build a deterministic forward-only trial plan."""

    trials: list[TrialSpec] = []
    for vx in vx_values_mps:
        for repeat in range(repeats_per_speed):
            trials.append(
                TrialSpec(
                    trial_id=f"vx_{vx:.2f}_repeat_{repeat + 1}",
                    vx_cmd_mps=vx,
                    repeat_index=repeat + 1,
                )
            )
    return trials
