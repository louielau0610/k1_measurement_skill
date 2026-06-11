import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.extract_m19_measurements_from_ros2_odometer_logs import (
    OUTPUT_FIELDS,
    extract_from_logs,
    extract_trial_measurement,
    forward_displacement_m,
    select_window,
    wrap_to_pi,
)


def test_wrap_to_pi_handles_boundary():
    assert abs(wrap_to_pi(math.radians(358)) - math.radians(-2)) < 1e-12
    assert abs(wrap_to_pi(math.radians(-358)) - math.radians(2)) < 1e-12


def test_forward_displacement_uses_start_theta():
    start = {"x": 0.0, "y": 0.0, "theta": math.pi / 2.0}
    end = {"x": 0.0, "y": 1.5, "theta": math.pi / 2.0}
    assert abs(forward_displacement_m(start, end) - 1.5) < 1e-12


def test_window_selection_and_measurement_extraction():
    samples = [
        {"t_rel": "2.5", "x": "0", "y": "0", "theta": "0"},
        {"t_rel": "3.0", "x": "0", "y": "0", "theta": "0"},
        {"t_rel": "8.0", "x": "1.0", "y": "0", "theta": str(math.radians(5))},
        {"t_rel": "8.5", "x": "3.0", "y": "0", "theta": "0"},
    ]
    assert [row["t_rel"] for row in select_window(samples, 3.0, 8.0)] == ["3.0", "8.0"]
    measurement, reason = extract_trial_measurement(samples)
    assert reason is None
    assert measurement is not None
    assert abs(measurement["measured_actual_velocity"] - 0.2) < 1e-12
    assert abs(measurement["yaw_drift_statistic"] - 5.0) < 1e-12


def test_missing_theta_blocks_extraction():
    measurement, reason = extract_trial_measurement(
        [
            {"t_rel": "1.0", "x": "0", "y": "0"},
            {"t_rel": "6.0", "x": "1", "y": "0"},
        ]
    )
    assert measurement is None
    assert reason == "insufficient_odometer_samples"


def test_ros2_odometer_extract_from_logs_schema(tmp_path):
    log = tmp_path / "M19C_SMOKE.csv"
    with log.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["trial_id", "t_rel", "odom_x", "odom_y", "odom_theta", "imu_yaw"])
        writer.writeheader()
        writer.writerow({"trial_id": "M19C_SMOKE", "t_rel": "3.0", "odom_x": "0", "odom_y": "0", "odom_theta": "0", "imu_yaw": "0"})
        writer.writerow({"trial_id": "M19C_SMOKE", "t_rel": "8.0", "odom_x": "1", "odom_y": "0", "odom_theta": "0.1", "imu_yaw": "0.1"})
    output_csv = tmp_path / "measurements.csv"
    output_dir = tmp_path / "out"

    summary = extract_from_logs(log, output_csv, output_dir)

    assert summary["measurements_extracted"] == 1
    assert summary["full_m19c_measurement_run_ready"]
    rows = list(csv.DictReader(output_csv.open(encoding="utf-8")))
    assert list(rows[0].keys()) == OUTPUT_FIELDS
    assert rows[0]["measurement_source"] == "ros2_odometer_state"
    assert rows[0]["imu_yaw_drift_deg"]
    assert (output_dir / "m19c_ros2_odometer_smoke_summary.json").exists()
    assert (output_dir / "m19c_ros2_odometer_smoke_report.md").exists()
