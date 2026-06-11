"""Unitree G1 scaffold-only adapter.

No Unitree G1 hardware source has been validated in this repository.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class UnitreeG1CommandAdapter:
    platform_id = "unitree_g1"
    hardware_validated_reference = False
    validation_status = "scaffold_only"

    def connect(self) -> None:
        raise NotImplementedError("Unitree G1 hardware access is scaffold-only and not validated.")

    def prepare(self) -> None:
        raise NotImplementedError("Unitree G1 command preparation is not implemented.")

    def enter_motion_mode(self) -> None:
        raise NotImplementedError("Unitree G1 motion mode is not implemented.")

    def send_velocity(self, vx_mps: float, vy_mps: float = 0.0, yaw_rate_radps: float = 0.0) -> None:
        raise NotImplementedError("Unitree G1 velocity commands must not be faked.")

    def stop(self) -> None:
        raise NotImplementedError("Unitree G1 stop command is not implemented.")

    def close(self) -> None:
        return None


class UnitreeG1ScaffoldLogger:
    platform_id = "unitree_g1"
    source_name = "unvalidated"

    def supports_position(self) -> bool:
        return False

    def supports_yaw(self) -> bool:
        return False

    def start_trial(self, trial_id: str, output_path: Path) -> None:
        raise NotImplementedError("Unitree G1 logging source is not validated.")

    def stop_trial(self) -> None:
        raise NotImplementedError("Unitree G1 logging source is not validated.")


class UnitreeG1ScaffoldExtractor:
    platform_id = "unitree_g1"

    def extract_trial(self, log_path: Path) -> dict[str, Any]:
        raise NotImplementedError("Unitree G1 measurements cannot be extracted without real validated logs.")

    def extract_batch(self, log_dir: Path, output_csv: Path, output_dir: Path) -> dict[str, Any]:
        raise NotImplementedError("Unitree G1 batch extraction cannot generate fake measurements.")
