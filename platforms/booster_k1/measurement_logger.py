"""Booster K1 measurement state logger.

Provides the ROS2 logger-process interface for the split-process K1 design.
The logger runs in a separate process from the SDK command client.
"""
from __future__ import annotations

from pathlib import Path


class BoosterK1MeasurementLogger:
    """State logger for the ROS2 logger process.

    In the split-process design, this logger runs in a process that has
    sourced the Booster ROS2 environment and subscribes to /odometer_state.
    It NEVER imports or uses Booster SDK native command APIs.
    """

    platform_id = "booster_k1"
    split_process_required = True
    source_name = "/odometer_state"
    secondary_source_name = "/low_state.imu_state.rpy"
    setup_requirement = "source /opt/booster/BoosterRos2Interface/install/setup.bash"

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self._active = False

    def supports_position(self) -> bool:
        return True

    def supports_yaw(self) -> bool:
        return True

    def start_trial(self, trial_id: str) -> Path:
        """Prepare for a trial log.

        Returns the expected output path. The actual ROS2 subscription and
        data recording is handled by the separate logger script
        (scripts/log_k1_ros2_odometer_state.py) running in the sourced
        Booster ROS2 environment.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{trial_id}.csv"
        self._active = True
        return output_path

    def stop_trial(self) -> None:
        """Mark the trial logger as stopped."""
        self._active = False

    def is_active(self) -> bool:
        return self._active
