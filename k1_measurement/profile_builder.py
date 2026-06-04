"""Build measurement-only environment profiles from raw trial logs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from k1_measurement.metrics import (
    compute_absolute_error,
    compute_actual_velocity,
    compute_lateral_drift_rate,
    compute_relative_error,
    compute_speed_gain,
    compute_tracking_rmse,
    compute_yaw_drift_rate,
    summarize_trials,
)


FULL_PROJECT = "K1 Velocity Measurement, Compensation and Navigation Safety Pipeline"
DUMMY_WARNING = "Dummy data only; not collected from a real K1 robot."
NO_NAV_WARNING = "Do not use this profile for compensation or navigation."

NUMERIC_FIELDS = {
    "timestamp",
    "vx_cmd",
    "vy_cmd",
    "wz_cmd",
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
}


def _coerce_row(row: dict[str, str]) -> dict[str, Any]:
    coerced: dict[str, Any] = {}
    for key, value in row.items():
        if key in NUMERIC_FIELDS:
            coerced[key] = float(value)
        else:
            coerced[key] = value
    return coerced


def load_raw_log(csv_path: str | Path) -> list[dict[str, Any]]:
    """Load a raw measurement CSV into a list of typed row dictionaries."""

    path = Path(csv_path)
    with path.open("r", encoding="utf-8", newline="") as file:
        return [_coerce_row(row) for row in csv.DictReader(file)]


def _group_by_trial(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["trial_id"])].append(row)
    return dict(grouped)


def _stable_command_rows(trial_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    command_rows = [row for row in trial_rows if row["command_phase"] == "command"]
    if len(command_rows) < 2:
        raise ValueError("each trial must contain at least two command-phase rows")

    command_start = min(float(row["timestamp"]) for row in command_rows)
    stable_rows = [
        row
        for row in command_rows
        if 2.0 <= float(row["timestamp"]) - command_start <= 5.0
    ]
    return sorted(stable_rows or command_rows, key=lambda row: float(row["timestamp"]))


def _summarize_single_trial(trial_rows: list[dict[str, Any]]) -> dict[str, float]:
    rows = sorted(trial_rows, key=lambda row: float(row["timestamp"]))
    stable_rows = _stable_command_rows(rows)
    first = stable_rows[0]
    last = stable_rows[-1]
    vx_cmd = float(first["vx_cmd"])
    vx_actual = compute_actual_velocity(
        first["odom_x"],
        last["odom_x"],
        first["timestamp"],
        last["timestamp"],
    )

    return {
        "vx_cmd_mps": vx_cmd,
        "vx_actual_mps": vx_actual,
        "speed_gain": compute_speed_gain(vx_actual, vx_cmd),
        "absolute_error_mps": compute_absolute_error(vx_actual, vx_cmd),
        "relative_error": compute_relative_error(vx_actual, vx_cmd),
        "lateral_drift_rate_mps": compute_lateral_drift_rate(
            first["odom_y"],
            last["odom_y"],
            first["timestamp"],
            last["timestamp"],
        ),
        "yaw_drift_rate_radps": compute_yaw_drift_rate(
            first["odom_yaw"],
            last["odom_yaw"],
            first["timestamp"],
            last["timestamp"],
        ),
        "tracking_rmse_mps": compute_tracking_rmse(
            [row["odom_vx"] for row in stable_rows],
            vx_cmd,
        ),
    }


def _environment_from_rows(rows: list[dict[str, Any]]) -> dict[str, str]:
    if not rows:
        raise ValueError("raw log must not be empty")
    first = rows[0]
    return {
        "floor_type": str(first["floor_type"]),
        "condition": str(first["condition"]),
        "slope": str(first["slope"]),
        "notes": "Dummy profile generated from dummy raw log only. Not real robot data.",
    }


def build_environment_profile(
    raw_df: list[dict[str, Any]],
    schema_version: str = "0.1.0",
) -> dict[str, Any]:
    """Build a schema-compliant dummy environment profile from raw log rows."""

    if not raw_df:
        raise ValueError("raw_df must not be empty")

    grouped = _group_by_trial(raw_df)
    trial_metrics = [_summarize_single_trial(rows) for rows in grouped.values()]
    trial_summary = summarize_trials(trial_metrics)
    vx_values = sorted(trial_summary)

    velocity_profile = []
    for vx_cmd in vx_values:
        summary = trial_summary[vx_cmd]
        velocity_profile.append(
            {
                "vx_cmd_mps": vx_cmd,
                "vx_actual_mean_mps": summary["vx_actual_mean_mps"],
                "vx_actual_std_mps": summary["vx_actual_std_mps"],
                "speed_gain_mean": summary["speed_gain_mean"],
                "speed_gain_std": summary["speed_gain_std"],
                "absolute_error_mean_mps": summary["absolute_error_mean_mps"],
                "relative_error_mean": summary["relative_error_mean"],
                "n_trials": summary["n_trials"],
            }
        )

    return {
        "schema_version": schema_version,
        "metadata": {
            "robot": "Booster K1",
            "skill_version": "measurement_v0",
            "experiment_name": "k1_forward_velocity_tracking_baseline_v0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "profile_id": "dummy_tile_dry_flat_measurement_v0_generated",
            "repository_role": "measurement_predecessor",
            "full_project": FULL_PROJECT,
        },
        "environment": _environment_from_rows(raw_df),
        "valid_speed_range": {
            "min_vx_cmd_mps": min(vx_values),
            "max_vx_cmd_mps": max(vx_values),
        },
        "velocity_profile": velocity_profile,
        "quality": {
            "confidence": "low",
            "ground_truth_method": "unknown",
            "odom_validated": False,
            "warnings": [DUMMY_WARNING, NO_NAV_WARNING],
        },
        "downstream_usage": {
            "recommended_for_compensation": False,
            "extrapolation_allowed": False,
            "notes": "Dummy data only. This generated profile is for pipeline validation only.",
        },
    }


def save_environment_profile(profile: dict[str, Any], output_path: str | Path) -> None:
    """Write a measurement profile as UTF-8 JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")


def build_measurement_profile(
    environment: dict[str, str],
    speed_points: list[dict[str, Any]],
    confidence: str = "low",
) -> dict[str, Any]:
    """Compatibility wrapper for older dummy scripts.

    New code should use build_environment_profile() so the output follows the M1
    downstream schema.
    """

    vx_values = [float(point["vx_cmd"]) for point in speed_points]
    return {
        "schema_version": "0.1.0",
        "metadata": {
            "robot": "Booster K1",
            "skill_version": "measurement_v0",
            "experiment_name": "manual_dummy_profile",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "profile_id": "manual_dummy_profile",
            "repository_role": "measurement_predecessor",
            "full_project": FULL_PROJECT,
        },
        "environment": {
            "floor_type": environment.get("floor_type", "unknown"),
            "condition": environment.get("condition", "unknown"),
            "slope": environment.get("slope", "unknown"),
            "notes": environment.get("notes", "Manual dummy profile only."),
        },
        "valid_speed_range": {
            "min_vx_cmd_mps": min(vx_values),
            "max_vx_cmd_mps": max(vx_values),
        },
        "velocity_profile": [
            {
                "vx_cmd_mps": float(point["vx_cmd"]),
                "vx_actual_mean_mps": float(point["vx_actual_mean"]),
                "vx_actual_std_mps": float(point["vx_actual_std"]),
                "speed_gain_mean": float(point["vx_actual_mean"]) / float(point["vx_cmd"]),
                "speed_gain_std": 0.0,
                "absolute_error_mean_mps": float(point["vx_error_mean"]),
                "relative_error_mean": float(point["vx_error_mean"]) / float(point["vx_cmd"]),
                "n_trials": int(point["sample_size"]),
            }
            for point in speed_points
        ],
        "quality": {
            "confidence": confidence if confidence in {"low", "medium", "high"} else "low",
            "ground_truth_method": "unknown",
            "odom_validated": False,
            "warnings": [DUMMY_WARNING, NO_NAV_WARNING],
        },
        "downstream_usage": {
            "recommended_for_compensation": False,
            "extrapolation_allowed": False,
            "notes": "Dummy data only. Do not use for compensation or navigation.",
        },
    }
