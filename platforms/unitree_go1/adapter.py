"""Unitree GO1 scaffold-only adapter.

No Unitree GO1 hardware source has been validated in this repository.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class UnitreeGo1CommandAdapter:
    platform_id = "unitree_go1"
    hardware_validated_reference = False
    validation_status = "scaffold_only"

    def connect(self) -> None:
        raise NotImplementedError("Unitree GO1 hardware access is scaffold-only and not validated.")

    def prepare(self) -> None:
        raise NotImplementedError("Unitree GO1 command preparation is not implemented.")

    def enter_motion_mode(self) -> None:
        raise NotImplementedError("Unitree GO1 motion mode is not implemented.")

    def send_velocity(self, vx_mps: float, vy_mps: float = 0.0, yaw_rate_radps: float = 0.0) -> None:
        raise NotImplementedError("Unitree GO1 velocity commands must not be faked.")

    def stop(self) -> None:
        raise NotImplementedError("Unitree GO1 stop command is not implemented.")

    def close(self) -> None:
        return None


class UnitreeGo1ScaffoldLogger:
    platform_id = "unitree_go1"
    source_name = "unvalidated"

    def supports_position(self) -> bool:
        return False

    def supports_yaw(self) -> bool:
        return False

    def start_trial(self, trial_id: str, output_path: Path) -> None:
        raise NotImplementedError("Unitree GO1 logging source is not validated.")

    def stop_trial(self) -> None:
        raise NotImplementedError("Unitree GO1 logging source is not validated.")


class UnitreeGo1ScaffoldExtractor:
    platform_id = "unitree_go1"

    def extract_trial(self, log_path: Path) -> dict[str, Any]:
        raise NotImplementedError("Unitree GO1 measurements cannot be extracted without real validated logs.")

    def extract_batch(self, log_dir: Path, output_csv: Path, output_dir: Path) -> dict[str, Any]:
        raise NotImplementedError("Unitree GO1 batch extraction cannot generate fake measurements.")
