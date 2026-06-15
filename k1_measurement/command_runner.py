"""Dry-run command runner for K1 forward velocity measurement."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class VelocityCommand:
    """Forward-only velocity command used by the measurement plan."""

    vx_mps: float
    vy_mps: float = 0.0
    wz_radps: float = 0.0


class CommandSafetyError(ValueError):
    """Raised when a command violates measurement-stage safety constraints."""


class K1CommandRunner:
    """Dry-run-only command runner.

    This class does not import ROS2 packages, publish commands, or move the robot.
    Real execution is intentionally blocked until verified K1 command topics exist.
    """

    def __init__(
        self,
        config_path: str | None = None,
        dry_run: bool = True,
        max_vx_cmd_mps: float | None = None,
        safety_provenance: dict[str, Any] | None = None,
    ) -> None:
        self.config_path = None if config_path is None else Path(config_path)
        self.dry_run = dry_run
        self.max_vx_cmd_mps = max_vx_cmd_mps
        self.safety_provenance = safety_provenance or {}
        self._config: dict[str, Any] | None = None

    def load_config(self) -> dict[str, Any]:
        """Load the experiment YAML config."""

        if self.config_path is None:
            self._config = {}
            return self._config
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

    def safety_check(
        self,
        vx: float,
        vy: float,
        wz: float,
        manual_confirmation: bool = False,
        emergency_stop_ready: bool = False,
    ) -> bool:
        """Validate command safety limits without sending anything."""

        max_vx = self._resolved_max_vx()
        if vx < 0:
            raise CommandSafetyError("vx must be non-negative")
        if vx > max_vx:
            raise CommandSafetyError("vx exceeds resolved max_vx_cmd_mps")
        safety = self.config.get("safety", {})
        if not bool(safety.get("allow_lateral_motion", False)) and vy != 0.0:
            raise CommandSafetyError("vy must be 0 when lateral motion is disabled")
        if not bool(safety.get("allow_turning", False)) and wz != 0.0:
            raise CommandSafetyError("wz must be 0 when turning is disabled")

        if not self.dry_run:
            if not manual_confirmation:
                raise CommandSafetyError("manual confirmation is required for future real execution")
            if not emergency_stop_ready:
                raise CommandSafetyError("emergency stop must be ready for future real execution")

        return True

    def send_velocity_command(
        self,
        vx: float,
        vy: float,
        wz: float,
        manual_confirmation: bool = False,
        emergency_stop_ready: bool = False,
    ) -> None:
        """Dry-run a velocity command or block real execution."""

        self.safety_check(vx, vy, wz, manual_confirmation, emergency_stop_ready)
        if not self.dry_run:
            raise NotImplementedError("Real execution is disabled until K1 command interface is verified.")

        print(
            "DRY RUN ONLY. No robot command is sent. "
            f"Planned velocity: vx={vx}, vy={vy}, wz={wz}"
        )

    def send_stop_command(self) -> None:
        """Dry-run stop command."""

        if not self.dry_run:
            raise NotImplementedError("Real stop command is disabled until K1 command interface is verified.")
        print("DRY RUN ONLY. Planned stop command; no robot command is sent.")

    def run_single_trial(
        self,
        trial: dict[str, Any],
        manual_confirmation: bool = False,
        emergency_stop_ready: bool = False,
    ) -> None:
        """Dry-run one baseline-command-stop trial."""

        if not self.dry_run:
            raise NotImplementedError("Real execution is disabled until K1 command interface is verified.")

        print(f"Trial: {trial['trial_id']}")
        print(f"DRY RUN ONLY: baseline phase {trial['baseline_duration_sec']} sec")
        print(f"DRY RUN ONLY: command phase {trial['command_duration_sec']} sec")
        self.send_velocity_command(
            float(trial["vx_cmd_mps"]),
            float(trial["vy_cmd_mps"]),
            float(trial["wz_cmd_radps"]),
            manual_confirmation=manual_confirmation,
            emergency_stop_ready=emergency_stop_ready,
        )
        print(f"DRY RUN ONLY: stop phase {trial['stop_duration_sec']} sec")
        self.send_stop_command()

    def _resolved_max_vx(self) -> float:
        if self.max_vx_cmd_mps is not None:
            return float(self.max_vx_cmd_mps)
        safety = self.config.get("safety", {})
        value = safety.get("max_vx_cmd_mps")
        if value is None:
            raise CommandSafetyError("max_vx_cmd_mps must be explicitly configured before validation or execution")
        return float(value)


class CommandRunner(K1CommandRunner):
    """Backward-compatible wrapper around K1CommandRunner."""

    def __init__(
        self,
        max_vx_cmd_mps: float | None = None,
        dry_run: bool = True,
        safety_provenance: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            dry_run=dry_run,
            max_vx_cmd_mps=max_vx_cmd_mps,
            safety_provenance=safety_provenance,
        )

    def validate(self, command: VelocityCommand, manual_confirmed: bool = False) -> None:
        self.safety_check(
            command.vx_mps,
            command.vy_mps,
            command.wz_radps,
            manual_confirmation=manual_confirmed,
            emergency_stop_ready=manual_confirmed,
        )

    def run(self, command: VelocityCommand, manual_confirmed: bool = False) -> dict[str, object]:
        self.validate(command, manual_confirmed=manual_confirmed)
        return {
            "dry_run": self.dry_run,
            "sent_to_robot": False,
            "vx_mps": command.vx_mps,
            "vy_mps": command.vy_mps,
            "wz_radps": command.wz_radps,
            "safety_reminder": "Confirm emergency stop and open test area before real commands.",
        }
