"""Common measurement schemas for cross-platform calibration."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

TRIAL_REQUIRED_FIELDS = [
    "robot_id",
    "robot_model",
    "platform",
    "trial_id",
    "session_id",
    "environment_id",
    "surface_type",
    "command_velocity",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "measurement_source",
    "measurement_method",
    "extraction_status",
    "confidence",
    "state_log_path",
    "timestamp",
]

AGGREGATE_REQUIRED_FIELDS = [
    "robot_model",
    "surface_type",
    "command_velocity",
    "n",
    "mean_actual_velocity",
    "std_actual_velocity",
    "mean_tracking_error",
    "relative_tracking_error",
    "no_motion_ratio",
    "mean_yaw_drift_deg",
    "response_uncertainty",
    "risk_score",
    "region_label",
]


@dataclass(frozen=True)
class TrialMeasurement:
    robot_id: str
    robot_model: str
    platform: str
    trial_id: str
    session_id: str
    environment_id: str
    surface_type: str
    command_velocity: float
    measured_actual_velocity: float
    yaw_drift_statistic: float
    measurement_source: str
    measurement_method: str
    extraction_status: str
    confidence: str
    state_log_path: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_trial_measurement(record: dict[str, Any]) -> list[str]:
    errors = [field for field in TRIAL_REQUIRED_FIELDS if field not in record]
    for field in ("command_velocity", "measured_actual_velocity", "yaw_drift_statistic"):
        if field in record:
            try:
                float(record[field])
            except (TypeError, ValueError):
                errors.append(f"{field}:not_numeric")
    return errors


def validate_aggregate_record(record: dict[str, Any]) -> list[str]:
    errors = [field for field in AGGREGATE_REQUIRED_FIELDS if field not in record]
    for field in ("command_velocity", "n", "mean_actual_velocity", "risk_score"):
        if field in record:
            try:
                float(record[field])
            except (TypeError, ValueError):
                errors.append(f"{field}:not_numeric")
    return errors
