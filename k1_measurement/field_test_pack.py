"""Create M7 field-test preparation artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


GROUND_TRUTH_COLUMNS = [
    "trial_id",
    "date",
    "operator",
    "vx_cmd_mps",
    "repeat_index",
    "planned_distance_m",
    "measured_distance_m",
    "elapsed_time_s",
    "visible_motion_started",
    "start_marker",
    "end_marker",
    "floor_type",
    "condition",
    "slope",
    "battery_before",
    "battery_after",
    "robot_mode",
    "odom_topic",
    "imu_topic",
    "command_topic",
    "notes",
]


def write_ground_truth_trial_sheet(output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(GROUND_TRUTH_COLUMNS)
    return path
