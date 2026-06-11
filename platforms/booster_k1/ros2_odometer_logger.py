"""Booster K1 ROS2 odometer logger wrapper."""
from __future__ import annotations

from pathlib import Path


class BoosterK1Ros2OdometerLogger:
    platform_id = "booster_k1"
    source_name = "/odometer_state"
    secondary_source_name = "/low_state.imu_state.rpy"
    setup_requirement = "source /opt/booster/BoosterRos2Interface/install/setup.bash"

    def supports_position(self) -> bool:
        return True

    def supports_yaw(self) -> bool:
        return True

    def start_trial(self, trial_id: str, output_path: Path) -> None:
        raise NotImplementedError(
            "Use scripts/log_k1_ros2_odometer_state.py in the sourced Booster ROS2 environment "
            f"to record trial {trial_id} to {output_path}."
        )

    def stop_trial(self) -> None:
        raise NotImplementedError("The script-managed ROS2 logger owns trial shutdown.")
