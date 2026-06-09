from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from k1_measurement.velocity_profile import build_velocity_profile, validate_velocity_profile


def sample_field_test_data() -> dict:
    return {
        "date": "2026-06-09",
        "platform": "Booster Robotics K1",
        "environment": {"floor_type": "lab_hard_floor", "condition": "dry"},
        "command_interface": {
            "sdk": "booster_robotics_sdk_python",
            "client": "B1LocoClient",
            "network_interface": "lo",
        },
        "measurement_scope": {
            "required_topics": {
                "odometer": {"topic": "/odometer_state", "type": "booster_interface/msg/Odometer"},
                "imu": {"topic": "/low_state", "type": "booster_interface/msg/LowState"},
                "robot_state": {"topic": "/robot_states", "type": "booster_interface/msg/RobotStatesMsg"},
                "safety_state": {"topic": "/fall_down", "type": "booster_interface/msg/FallDownState"},
            },
            "removed_or_optional": {
                "battery_state": {"status": "optional_future_only"},
                "remote_controller_state": {
                    "status": "permanently_removed",
                    "reason": "navigation-focused measurement excludes manual-control input",
                },
            },
        },
    }


def sample_analysis_summary() -> dict:
    return {
        "first_effective_command_speed_mps": 0.3,
        "analyzed_trials": [
            {
                "trial_id": "vx_0_1_smoke",
                "vx_cmd_mps": 0.1,
                "duration_s": 2.0,
                "distance_m": None,
                "v_actual_est_mps": None,
                "speed_gain_est": None,
                "dtheta_rad": None,
                "tracking_category": "ineffective_or_deadzone",
                "interpretation": "deadzone_or_ineffective_low_speed",
            },
            {
                "trial_id": "vx_0_3_transition",
                "vx_cmd_mps": 0.3,
                "duration_s": 2.0,
                "distance_m": 0.288544,
                "v_actual_est_mps": 0.144272,
                "speed_gain_est": 0.480907,
                "dtheta_rad": 0.033154,
                "tracking_category": "weak_response",
                "interpretation": "first_effective_but_weak_response",
            },
            {
                "trial_id": "vx_0_4_effective",
                "vx_cmd_mps": 0.4,
                "duration_s": 2.0,
                "distance_m": 0.548009,
                "v_actual_est_mps": 0.274004,
                "speed_gain_est": 0.685011,
                "dtheta_rad": 0.006043,
                "tracking_category": "under_tracking",
                "interpretation": "effective_but_under_tracking",
            },
            {
                "trial_id": "vx_0_5_stable",
                "vx_cmd_mps": 0.5,
                "duration_s": 2.0,
                "distance_m": 1.00394,
                "v_actual_est_mps": 0.50197,
                "speed_gain_est": 1.00394,
                "dtheta_rad": 0.005665,
                "tracking_category": "stable_tracking",
                "interpretation": "stable_tracking",
            },
            {
                "trial_id": "vx_0_45_transition_upper",
                "vx_cmd_mps": 0.45,
                "duration_s": 2.0,
                "distance_m": 0.839345,
                "v_actual_est_mps": 0.419672,
                "speed_gain_est": 0.932605,
                "dtheta_rad": -0.094939,
                "tracking_category": "stable_tracking",
                "interpretation": "near_stable_tracking_but_yaw_drift_needs_repeat",
            },
        ],
        "limitations": ["single_session"],
    }


def test_building_profile_from_minimal_valid_sample_data() -> None:
    profile = build_velocity_profile(sample_field_test_data(), sample_analysis_summary())

    validate_velocity_profile(profile)
    assert profile["platform"] == "Booster Robotics K1"
    assert profile["profile_thresholds"]["first_effective_observed_vx_cmd_mps"] == 0.3


def test_generated_profile_schema_version() -> None:
    profile = build_velocity_profile(sample_field_test_data(), sample_analysis_summary())

    assert profile["schema_version"] == "real_k1_velocity_profile_v0"


def test_excluded_topic_statuses_are_preserved() -> None:
    profile = build_velocity_profile(sample_field_test_data(), sample_analysis_summary())

    assert profile["excluded_or_optional_topics"]["battery_state"]["status"] == "optional_future_only"
    assert profile["excluded_or_optional_topics"]["remote_controller_state"]["status"] == "permanently_removed"


def test_downstream_readiness_flags() -> None:
    profile = build_velocity_profile(sample_field_test_data(), sample_analysis_summary())

    assert profile["downstream_usage"]["compensation_ready"] is False
    assert profile["downstream_usage"]["navigation_warning_ready"] is True


def test_vx_0_45_requires_repeat_due_to_yaw_drift() -> None:
    profile = build_velocity_profile(sample_field_test_data(), sample_analysis_summary())
    trial = next(point for point in profile["trial_points"] if point["trial_id"] == "vx_0_45_transition_upper")

    assert trial["requires_repeat_due_to_yaw_drift"] is True


def test_cli_generation_into_temporary_output_path(tmp_path: Path) -> None:
    output = tmp_path / "profile.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_real_k1_velocity_profile.py",
            "--output-profile",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "real_k1_velocity_profile_v0"
    assert data["downstream_usage"]["compensation_ready"] is False
