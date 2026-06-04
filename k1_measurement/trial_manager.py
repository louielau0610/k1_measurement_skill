"""Dry-run trial planning for K1 forward velocity measurement."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class TrialSpec:
    """Backward-compatible compact trial spec."""

    trial_id: str
    vx_cmd_mps: float
    repeat_index: int


class K1TrialManager:
    """Generate and validate a dry-run-only forward baseline trial plan."""

    def __init__(self, config_path: str = "config/experiment_forward_v0.yaml") -> None:
        self.config_path = Path(config_path)
        self._config: dict[str, Any] | None = None

    def load_config(self) -> dict[str, Any]:
        """Load the experiment YAML config."""

        with self.config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        if not isinstance(config, dict):
            raise ValueError("experiment config must be a YAML object")
        self._config = config
        return config

    @property
    def config(self) -> dict[str, Any]:
        if self._config is None:
            return self.load_config()
        return self._config

    def generate_trial_plan(self) -> list[dict[str, Any]]:
        """Generate deterministic dry-run trials from config/experiment_forward_v0.yaml."""

        config = self.config
        trial_config = config["trial_plan"]
        environment = config["environment"]
        experiment = config["experiment"]

        trials: list[dict[str, Any]] = []
        for vx_cmd in trial_config["vx_cmd_values_mps"]:
            for repeat_index in range(1, int(trial_config["repeats_per_speed"]) + 1):
                trials.append(
                    {
                        "trial_id": f"trial_vx_{float(vx_cmd):.2f}".replace(".", "p")
                        + f"_rep_{repeat_index:02d}",
                        "vx_cmd_mps": float(vx_cmd),
                        "vy_cmd_mps": float(trial_config["vy_cmd_mps"]),
                        "wz_cmd_radps": float(trial_config["wz_cmd_radps"]),
                        "repeat_index": repeat_index,
                        "baseline_duration_sec": float(trial_config["baseline_duration_sec"]),
                        "command_duration_sec": float(trial_config["command_duration_sec"]),
                        "stop_duration_sec": float(trial_config["stop_duration_sec"]),
                        "stable_window_start_sec": float(trial_config["stable_window_start_sec"]),
                        "stable_window_end_sec": float(trial_config["stable_window_end_sec"]),
                        "floor_type": environment["floor_type"],
                        "condition": environment["condition"],
                        "slope": environment["slope"],
                        "mode": experiment.get("mode", "measurement_only"),
                    }
                )
        return trials

    def print_trial_plan(self, trial_plan: list[dict[str, Any]]) -> None:
        """Print a readable trial plan without executing it."""

        print("DRY RUN ONLY. No robot command is sent.")
        for trial in trial_plan:
            print(
                f"{trial['trial_id']}: vx={trial['vx_cmd_mps']} m/s, "
                f"repeat={trial['repeat_index']}, env="
                f"{trial['floor_type']}/{trial['condition']}/{trial['slope']}"
            )

    def validate_trial_plan(self, trial_plan: list[dict[str, Any]]) -> bool:
        """Validate safety and timing constraints for the dry-run trial plan."""

        if not trial_plan:
            raise ValueError("trial_plan must not be empty")

        safety = self.config["safety"]
        max_vx = float(safety["max_vx_cmd_mps"])
        allow_lateral_motion = bool(safety.get("allow_lateral_motion", False))
        allow_turning = bool(safety.get("allow_turning", False))

        for index, trial in enumerate(trial_plan):
            vx = float(trial["vx_cmd_mps"])
            vy = float(trial["vy_cmd_mps"])
            wz = float(trial["wz_cmd_radps"])
            baseline_duration = float(trial["baseline_duration_sec"])
            command_duration = float(trial["command_duration_sec"])
            stop_duration = float(trial["stop_duration_sec"])
            stable_start = float(trial["stable_window_start_sec"])
            stable_end = float(trial["stable_window_end_sec"])

            if vx < 0:
                raise ValueError(f"trial {index} vx_cmd_mps must be non-negative")
            if vx > max_vx:
                raise ValueError(f"trial {index} vx_cmd_mps exceeds safety.max_vx_cmd_mps")
            if not allow_lateral_motion and vy != 0.0:
                raise ValueError(f"trial {index} vy_cmd_mps must be 0 when lateral motion is disabled")
            if not allow_turning and wz != 0.0:
                raise ValueError(f"trial {index} wz_cmd_radps must be 0 when turning is disabled")
            if command_duration <= 0:
                raise ValueError(f"trial {index} command_duration_sec must be > 0")
            if baseline_duration < 0:
                raise ValueError(f"trial {index} baseline_duration_sec must be >= 0")
            if stop_duration < 0:
                raise ValueError(f"trial {index} stop_duration_sec must be >= 0")
            if stable_start >= stable_end:
                raise ValueError(f"trial {index} stable window start must be before end")
            if stable_start < 0 or stable_end > command_duration:
                raise ValueError(f"trial {index} stable window must lie inside command duration")

        return True


def build_forward_trial_plan(vx_values_mps: list[float], repeats_per_speed: int) -> list[TrialSpec]:
    """Build a deterministic forward-only trial plan for compatibility."""

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
