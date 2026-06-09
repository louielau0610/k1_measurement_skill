from __future__ import annotations

import csv
from pathlib import Path

import yaml

from scripts.analyze_real_k1_forward_velocity import (
    analyze_record,
    analyze_trial,
    load_yaml_record,
    run_analysis,
    tracking_category,
    validate_record,
)


def sample_record() -> dict:
    return {
        "schema_version": "real_k1_forward_velocity_field_test_v0",
        "date": "2026-06-09",
        "platform": "Booster Robotics K1",
        "environment": {"floor_type": "lab_hard_floor", "condition": "dry"},
        "command_interface": {"sdk": "booster_robotics_sdk_python", "client": "B1LocoClient"},
        "measurement_scope": {
            "removed_or_optional": {
                "battery_state": {"status": "optional_future_only"},
                "remote_controller_state": {"status": "permanently_removed"},
            }
        },
        "trials": [
            {
                "trial_id": "vx_0_1_smoke",
                "vx_cmd_mps": 0.1,
                "duration_s": 2.0,
                "movement_observed": "almost_none",
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
                "fall_down_state_post": 0,
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
                "fall_down_state_post": 0,
                "interpretation": "effective_but_under_tracking",
            },
            {
                "trial_id": "vx_0_5_stable",
                "vx_cmd_mps": 0.5,
                "duration_s": 2.0,
                "distance_m": 1.003940,
                "v_actual_est_mps": 0.501970,
                "speed_gain_est": 1.003940,
                "dtheta_rad": 0.005665,
                "fall_down_state_post": 0,
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
                "fall_down_state_post": 0,
                "interpretation": "near_stable_tracking_but_yaw_drift_needs_repeat",
            },
        ],
        "preliminary_findings": {
            "first_effective_vx_cmd_mps": 0.3,
            "stable_tracking_region_mps": "0.45_to_0.5",
            "global_gain_model_recommended": False,
            "recommended_model": "piecewise_or_nonlinear_mapping",
        },
        "limitations": ["single_session"],
    }


def test_yaml_loading_and_schema_validation(tmp_path: Path) -> None:
    path = tmp_path / "record.yaml"
    path.write_text(yaml.safe_dump(sample_record()), encoding="utf-8")

    record = load_yaml_record(path)
    validate_record(record)

    assert record["schema_version"] == "real_k1_forward_velocity_field_test_v0"


def test_derived_metric_computation() -> None:
    analyzed = analyze_trial(
        {
            "trial_id": "vx_0_4_effective",
            "vx_cmd_mps": 0.4,
            "duration_s": 2.0,
            "distance_m": 0.548009,
            "speed_gain_est": 0.685011,
            "dtheta_rad": -0.006043,
        }
    )

    assert analyzed["commanded_distance_m"] == 0.8
    assert round(analyzed["distance_error_m"], 6) == -0.251991
    assert round(analyzed["relative_distance_error"], 6) == -0.314989
    assert analyzed["abs_dtheta_rad"] == 0.006043


def test_tracking_category_assignment() -> None:
    assert tracking_category({"movement_observed": "almost_none"}) == "ineffective_or_deadzone"
    assert tracking_category({"distance_m": 0.1, "speed_gain_est": 0.5}) == "weak_response"
    assert tracking_category({"distance_m": 0.1, "speed_gain_est": 0.7}) == "under_tracking"
    assert tracking_category({"distance_m": 0.1, "speed_gain_est": 1.0}) == "stable_tracking"
    assert tracking_category({"distance_m": 0.1, "speed_gain_est": 1.2}) == "over_tracking"


def test_vx_0_1_smoke_trial_with_no_numeric_distance() -> None:
    summary = analyze_record(sample_record())
    smoke = summary["analyzed_trials"][0]

    assert smoke["trial_id"] == "vx_0_1_smoke"
    assert smoke["commanded_distance_m"] == 0.2
    assert smoke["distance_error_m"] is None
    assert smoke["relative_distance_error"] is None
    assert smoke["tracking_category"] == "ineffective_or_deadzone"


def test_end_to_end_artifact_generation_into_temp_directory(tmp_path: Path) -> None:
    input_yaml = tmp_path / "record.yaml"
    output_csv = tmp_path / "trials.csv"
    output_json = tmp_path / "summary.json"
    output_report = tmp_path / "report.md"
    output_plot = tmp_path / "curve.png"
    input_yaml.write_text(yaml.safe_dump(sample_record()), encoding="utf-8")

    summary = run_analysis(input_yaml, output_csv, output_json, output_report, output_plot)

    assert summary["best_tracking_trial"]["trial_id"] == "vx_0_5_stable"
    assert summary["highest_yaw_drift_trial"]["trial_id"] == "vx_0_45_transition_upper"
    for path in [output_csv, output_json, output_report, output_plot]:
        assert path.exists()
        assert path.stat().st_size > 0
    with output_csv.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 5
    assert rows[0]["tracking_category"] == "ineffective_or_deadzone"
