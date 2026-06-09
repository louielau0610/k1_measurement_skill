"""Offline real K1 velocity profile construction utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = "real_k1_velocity_profile_v0"
DEFAULT_FIELD_TEST_YAML = "outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.yaml"
DEFAULT_ANALYSIS_SUMMARY_JSON = "outputs/real_k1_field_tests/forward_velocity_transition_summary_v0.json"


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("JSON input must contain an object")
    return data


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML object from disk."""

    with Path(path).open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError("YAML input must contain an object")
    return data


def _topic_profile(topic_data: dict[str, Any], usage: list[str]) -> dict[str, Any]:
    return {
        "topic": topic_data.get("topic"),
        "type": topic_data.get("type"),
        "usage": usage,
    }


def _trial_point(trial: dict[str, Any]) -> dict[str, Any]:
    point = {
        "trial_id": trial.get("trial_id"),
        "vx_cmd_mps": trial.get("vx_cmd_mps"),
        "duration_s": trial.get("duration_s"),
        "distance_m": trial.get("distance_m"),
        "v_actual_est_mps": trial.get("v_actual_est_mps"),
        "speed_gain_est": trial.get("speed_gain_est"),
        "dtheta_rad": trial.get("dtheta_rad"),
        "tracking_category": trial.get("tracking_category"),
        "interpretation": trial.get("interpretation"),
    }
    if trial.get("trial_id") == "vx_0_45_transition_upper":
        point["requires_repeat_due_to_yaw_drift"] = True
    return point


def build_velocity_profile(
    field_test_data: dict[str, Any],
    analysis_summary: dict[str, Any],
    field_test_yaml_path: str = DEFAULT_FIELD_TEST_YAML,
    analysis_summary_json_path: str = DEFAULT_ANALYSIS_SUMMARY_JSON,
) -> dict[str, Any]:
    """Build a deterministic measurement-only velocity profile."""

    measurement_scope = field_test_data["measurement_scope"]
    topics = measurement_scope["required_topics"]
    command_interface = field_test_data["command_interface"]
    profile = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "field_test_yaml": field_test_yaml_path,
            "analysis_summary_json": analysis_summary_json_path,
            "date": field_test_data["date"],
        },
        "platform": field_test_data["platform"],
        "environment": field_test_data["environment"],
        "command_interface": {
            "sdk": command_interface.get("sdk"),
            "client": command_interface.get("client"),
            "method": "Move(vx, 0.0, 0.0)",
            "network_interface": command_interface.get("network_interface"),
        },
        "measurement_topics": {
            "odometer": _topic_profile(topics["odometer"], ["within_trial_displacement", "relative_heading"]),
            "imu": _topic_profile(topics["imu"], ["rpy", "gyro", "acc", "yaw_cross_check"]),
            "robot_state": _topic_profile(
                topics["robot_state"],
                ["current_mode", "current_body_control", "current_actions"],
            ),
            "safety_state": _topic_profile(topics["safety_state"], ["fall_down_state", "is_recovery_available"]),
        },
        "excluded_or_optional_topics": measurement_scope["removed_or_optional"],
        "observed_velocity_regions": {
            "ineffective_or_deadzone": {
                "observed_vx_cmd_mps": [0.1],
                "interpretation": "almost no measurable translation",
            },
            "first_effective_region": {
                "observed_vx_cmd_mps": [0.3],
                "interpretation": "first clearly effective but weak response",
            },
            "transition_region": {
                "observed_vx_cmd_mps": [0.3, 0.4, 0.45],
                "interpretation": "nonlinear low-speed transition; gain increases rapidly",
            },
            "stable_tracking_region": {
                "observed_vx_cmd_mps": [0.45, 0.5],
                "interpretation": "near-stable to stable tracking, but 0.45 requires yaw repeat check",
            },
        },
        "profile_thresholds": {
            "last_ineffective_observed_vx_cmd_mps": 0.1,
            "first_effective_observed_vx_cmd_mps": analysis_summary["first_effective_command_speed_mps"],
            "stable_tracking_observed_vx_cmd_mps": 0.5,
            "stable_tracking_candidate_lower_bound_mps": 0.45,
            "effective_threshold_interval_mps": [0.1, 0.3],
        },
        "trial_points": [_trial_point(trial) for trial in analysis_summary["analyzed_trials"]],
        "modeling_recommendation": {
            "global_gain_model_recommended": False,
            "recommended_model_family": "piecewise_or_nonlinear_mapping",
            "reason": "low-speed response is nonlinear with deadzone and transition region",
        },
        "downstream_usage": {
            "compensation_ready": False,
            "navigation_warning_ready": True,
            "safe_command_adapter_ready": False,
            "recommended_use": [
                "warn on low target speeds below observed effective threshold",
                "treat 0.3-0.45 as transition/low-confidence region",
                "use 0.5 as current stable tracking reference for lab hard floor only",
            ],
        },
        "profile_rules": [
            "Do not compare absolute odometer coordinates across trials.",
            "Use only within-trial delta-derived values from the M10 analysis.",
            "Treat 0.1 m/s as observed ineffective/deadzone.",
            "Treat 0.3 m/s as first observed effective but weak.",
            "Treat 0.4 m/s as effective but under-tracking.",
            "Treat 0.45 m/s as near stable tracking, but repeat due to yaw drift.",
            "Treat 0.5 m/s as the current stable tracking reference.",
            "Do not output corrected command velocity from this profile.",
        ],
        "limitations": analysis_summary["limitations"],
    }
    validate_velocity_profile(profile)
    return profile


def validate_velocity_profile(profile: dict[str, Any]) -> None:
    """Validate the generated profile contract shape and critical safety flags."""

    required = [
        "schema_version",
        "source",
        "platform",
        "environment",
        "command_interface",
        "measurement_topics",
        "excluded_or_optional_topics",
        "observed_velocity_regions",
        "profile_thresholds",
        "trial_points",
        "modeling_recommendation",
        "downstream_usage",
        "limitations",
    ]
    missing = [field for field in required if field not in profile]
    if missing:
        raise ValueError(f"velocity profile missing fields: {missing}")
    if profile["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unexpected velocity profile schema_version")
    if profile["excluded_or_optional_topics"]["battery_state"]["status"] != "optional_future_only":
        raise ValueError("battery_state must remain optional/future only")
    if profile["excluded_or_optional_topics"]["remote_controller_state"]["status"] != "permanently_removed":
        raise ValueError("remote_controller_state must remain permanently removed")
    downstream = profile["downstream_usage"]
    if downstream["compensation_ready"] is not False:
        raise ValueError("compensation_ready must be false for v0")
    if downstream["navigation_warning_ready"] is not True:
        raise ValueError("navigation_warning_ready must be true for v0")

    trial_points = profile["trial_points"]
    if not isinstance(trial_points, list) or len(trial_points) != 5:
        raise ValueError("velocity profile must contain exactly 5 trial points")
    repeat_flags = [
        point
        for point in trial_points
        if point.get("trial_id") == "vx_0_45_transition_upper"
        and point.get("requires_repeat_due_to_yaw_drift") is True
    ]
    if not repeat_flags:
        raise ValueError("vx_0_45_transition_upper must require repeat due to yaw drift")


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    """Write JSON with stable formatting."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
