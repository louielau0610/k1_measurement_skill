"""Platform-agnostic state logger interface."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class RobotStateLogger(Protocol):
    def start_trial(self, trial_id: str, command_velocity: float, output_path: Path) -> None: ...

    def stop_trial(self) -> None: ...

    def supports_position(self) -> bool: ...

    def supports_yaw(self) -> bool: ...

    def source_name(self) -> str: ...
