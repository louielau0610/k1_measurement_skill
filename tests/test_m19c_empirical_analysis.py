import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.analyze_m19c_empirical_response import analyze, build_gold_profile, compute_cell_stats, read_measurements
from scripts.classify_m19c_risk_regions import classify_region, risk_score


FIELDS = [
    "trial_id",
    "measurement_source",
    "measurement_method",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "extraction_status",
    "distance_m",
    "time_sec",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "imu_yaw_drift_deg",
    "command_velocity",
]
TRIAL_FIELDS = ["trial_id", "environment_id"]


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def measurement(trial_id, command, actual, yaw, imu=None):
    return {
        "trial_id": trial_id,
        "measurement_source": "ros2_odometer_state",
        "measurement_method": "odometer_forward_projection_window_3_8s",
        "analysis_window_start_sec": "3.0",
        "analysis_window_end_sec": "8.0",
        "extraction_status": "ok",
        "distance_m": actual * 5,
        "time_sec": 5,
        "measured_actual_velocity": actual,
        "yaw_drift_statistic": yaw,
        "imu_yaw_drift_deg": yaw if imu is None else imu,
        "command_velocity": command,
    }


def test_empirical_statistic_and_tracking_error_computation():
    rows = [
        {"surface_id": "S1", **measurement("a", 0.4, 0.2, 2.0)},
        {"surface_id": "S1", **measurement("b", 0.4, 0.3, 4.0)},
        {"surface_id": "S1", **measurement("c", 0.4, 0.4, 6.0)},
    ]
    stats = compute_cell_stats(rows)[0]
    assert stats["n"] == 3
    assert abs(stats["mean_actual_velocity"] - 0.3) < 1e-12
    assert abs(stats["mean_tracking_error"] - (-0.1)) < 1e-12
    assert abs(stats["relative_tracking_error"] - (-0.25)) < 1e-12
    assert stats["mean_yaw_drift_deg"] == 4.0
    assert stats["odom_imu_yaw_disagreement_deg"] == 0.0


def test_no_motion_detection_and_risk_score():
    rows = [
        {"surface_id": "S1", **measurement("a", 0.1, 0.0, 0.1)},
        {"surface_id": "S1", **measurement("b", 0.1, 0.01, 0.2)},
        {"surface_id": "S1", **measurement("c", 0.1, 0.02, 0.3)},
    ]
    stats = compute_cell_stats(rows)[0]
    assert stats["no_motion_ratio"] == pytest.approx(1.0)
    assert classify_region(stats) == "deadzone"
    assert risk_score(stats) > 0.0


def test_region_classification_priority_and_threshold_config():
    assert classify_region({"n": 2}) == "insufficient_evidence"
    assert classify_region({"n": 3, "no_motion_ratio": 0.7}) == "deadzone"
    assert classify_region({"n": 3, "no_motion_ratio": 0, "response_uncertainty": 0.2}) == "unstable"
    assert classify_region({"n": 3, "no_motion_ratio": 0, "response_uncertainty": 0.0, "mean_yaw_drift_deg": 8}) == "drift_prone"
    assert classify_region({"n": 3, "relative_tracking_error": -0.25}) == "under_track"
    assert classify_region({"n": 3, "relative_tracking_error": 0.25}) == "over_response"
    assert classify_region({"n": 3, "relative_tracking_error": 0.15}, {"under_track_relative_threshold": 0.1, "over_response_relative_threshold": 0.1}) == "over_response"


def test_missing_measurement_blocks_read(tmp_path):
    data = tmp_path / "measurements.csv"
    trials = tmp_path / "trials.csv"
    write_csv(data, [measurement("M19C_S1_B1_U010_R1", 0.1, "", 1.0)], FIELDS)
    write_csv(trials, [{"trial_id": "M19C_S1_B1_U010_R1", "environment_id": "S1"}], TRIAL_FIELDS)
    with pytest.raises(ValueError):
        read_measurements(data, trials)


def test_analyze_outputs_gold_profile_schema(tmp_path):
    data = tmp_path / "measurements.csv"
    trials = tmp_path / "trials.csv"
    rows = []
    trial_rows = []
    for surface in ("S1_lab_hard_floor", "S2_marble_floor"):
        for repeat, actual in enumerate((0.1, 0.12, 0.11), start=1):
            tid = f"M19C_{surface}_B{repeat}_U010_R{repeat}"
            rows.append(measurement(tid, 0.1, actual, 1.0))
            trial_rows.append({"trial_id": tid, "environment_id": surface})
    write_csv(data, rows, FIELDS)
    write_csv(trials, trial_rows, TRIAL_FIELDS)
    summary = analyze(data, trials, tmp_path / "out")
    profile = json.loads((tmp_path / "out" / "k1_gold_profile_v1.json").read_text(encoding="utf-8"))
    assert summary["rows_ingested"] == 6
    assert profile["robot_id"] == "Booster_K1"
    assert profile["extraction_source"] == "ros2_odometer_state"
    assert "no cross-robot generalization yet" in profile["limitations"]
