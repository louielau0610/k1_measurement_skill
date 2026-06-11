"""Booster K1 command adapter scaffold.

The validated M19C command path is kPrepare -> kWalking -> Move(vx, 0, 0).
This class documents that route for reusable scheduling, but hardware command
execution remains opt-in so tests and planning tools cannot move a robot.
"""
from __future__ import annotations


class BoosterK1CommandAdapter:
    platform_id = "booster_k1"
    hardware_validated_reference = True
    validation_status = "hardware_validated_reference"
    command_sequence = ("kPrepare", "kWalking", "Move(vx, 0, 0)")

    def __init__(self, execute_enabled: bool = False) -> None:
        self.execute_enabled = execute_enabled
        self.connected = False

    def _require_execution(self) -> None:
        if not self.execute_enabled:
            raise NotImplementedError(
                "Booster K1 hardware command execution is disabled by default; "
                "use the existing validated M19C runner on the robot-side environment."
            )

    def connect(self) -> None:
        self._require_execution()
        self.connected = True

    def prepare(self) -> None:
        self._require_execution()

    def enter_motion_mode(self) -> None:
        self._require_execution()

    def send_velocity(self, vx_mps: float, vy_mps: float = 0.0, yaw_rate_radps: float = 0.0) -> None:
        self._require_execution()
        if vy_mps != 0.0 or yaw_rate_radps != 0.0:
            raise ValueError("M20 K1 reference trials only expose forward Move(vx, 0, 0).")
        if vx_mps < 0:
            raise ValueError("forward calibration command velocity must be non-negative")

    def stop(self) -> None:
        self._require_execution()

    def close(self) -> None:
        self.connected = False
