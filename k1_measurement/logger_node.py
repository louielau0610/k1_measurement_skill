"""Safe logger skeleton for K1 measurement.

This module intentionally does not import rclpy, subscribe to ROS2 topics, publish
commands, or move the robot. Real logging must wait until K1 topic names and
message types are manually verified.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml


CSV_HEADER = [
    "timestamp",
    "trial_id",
    "vx_cmd",
    "vy_cmd",
    "wz_cmd",
    "command_phase",
    "odom_x",
    "odom_y",
    "odom_yaw",
    "odom_vx",
    "odom_vy",
    "odom_wz",
    "imu_acc_x",
    "imu_acc_y",
    "imu_acc_z",
    "imu_gyro_x",
    "imu_gyro_y",
    "imu_gyro_z",
    "battery_level",
    "robot_mode",
    "floor_type",
    "condition",
    "slope",
    "operator_note",
]


class K1MeasurementLogger:
    """Logger skeleton that refuses unsafe or incomplete real logging setup."""

    def __init__(
        self,
        topic_mapping_path: str = "config/topic_mapping_template.yaml",
        dry_run: bool = True,
    ) -> None:
        self.topic_mapping_path = Path(topic_mapping_path)
        self.dry_run = dry_run
        self.is_running = False

    def load_topic_mapping(self) -> dict[str, Any]:
        """Load topic mapping YAML without assuming any topic is verified."""

        with self.topic_mapping_path.open("r", encoding="utf-8") as file:
            mapping = yaml.safe_load(file) or {}
        if not isinstance(mapping, dict):
            raise ValueError("topic mapping must be a YAML object")
        return mapping

    def _missing_requirements(self) -> list[str]:
        mapping = self.load_topic_mapping()
        required_topics = mapping.get("required_topics", {})
        validation = mapping.get("validation", {})
        safety = mapping.get("safety", {})
        missing: list[str] = []

        for key in ["odom_topic", "imu_topic", "robot_state_topic"]:
            value = required_topics.get(key)
            if not value or value == "TBD":
                missing.append(f"required_topics.{key}")

        for key in ["odom_verified", "imu_verified", "robot_state_verified"]:
            if validation.get(key) is not True:
                missing.append(f"validation.{key}")

        if safety.get("allow_real_logging") is not True:
            missing.append("safety.allow_real_logging")

        if safety.get("allow_real_robot_command") is True:
            missing.append("safety.allow_real_robot_command must remain false")

        return missing

    def is_mapping_complete(self) -> bool:
        """Return True only when required read-only logging topics are verified."""

        return not self._missing_requirements()

    def validate_mapping_for_logging(self) -> bool:
        """Validate whether real logging may start.

        Dry-run mode always returns False because no real ROS2 subscriptions should
        be started. Incomplete mappings also return False with a clear message.
        """

        if self.dry_run:
            print("Dry-run mode: no real ROS2 subscription will be started.")
            return False

        missing = self._missing_requirements()
        if missing:
            print("Topic mapping is incomplete. Missing requirements:")
            for item in missing:
                print(f"- {item}")
            return False

        return True

    def start_logging(self) -> None:
        """Start logger skeleton.

        In dry-run mode this only prints a message. Real subscription support is
        deliberately not implemented in M4.
        """

        if self.dry_run:
            print("Dry-run logger: no real ROS2 subscription is started.")
            self.is_running = False
            return

        if not self.is_mapping_complete():
            raise RuntimeError("Cannot start real logging: topic mapping is incomplete.")

        raise NotImplementedError(
            "Real ROS2 subscription will be implemented only after verified K1 topics are confirmed."
        )

    def stop_logging(self) -> None:
        """Stop the skeleton logger without ROS2 side effects."""

        self.is_running = False
        print("Logger stopped. No real ROS2 subscription was active in M4 skeleton mode.")

    def save_csv(self, output_path: str) -> None:
        """Write an empty CSV header only; this is not real robot data."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
        print(f"Wrote empty logger skeleton CSV header only: {path}")


class LoggerNodePlaceholder:
    """Backward-compatible placeholder without ROS2 side effects."""

    def __init__(self, topics: dict[str, str] | None = None) -> None:
        self.topics = topics or {}

    def verified_topics(self) -> bool:
        return bool(self.topics) and all(value not in {"", "TBD"} for value in self.topics.values())
