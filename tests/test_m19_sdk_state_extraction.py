import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.extract_m19_measurements_from_sdk_state_logs import (
    OUTPUT_FIELDS,
    extract_from_logs,
    extract_trial_measurement,
    forward_displacement_m,
    select_window,
    wrapped_yaw_diff_deg,
)


def test_yaw_wrap_difference():
    assert wrapped_yaw_diff_deg(179.0, -179.0) == 2.0
    assert wrapped_yaw_diff_deg(-179.0, 179.0) == -2.0
    assert wrapped_yaw_diff_deg(10.0, 40.0) == 30.0


def test_forward_displacement_projection():
    start = {"x": 0.0, "y": 0.0}
    end = {"x": 0.0, "y": 2.0}
    assert abs(forward_displacement_m(start, end, 90.0) - 2.0) < 1e-9
    assert abs(forward_displacement_m(start, {"x": 2.0, "y": 0.0}, 0.0) - 2.0) < 1e-9


def test_extraction_window_selection():
    samples = [
        {"t_rel": "0.5", "x": "0", "y": "0", "yaw_deg": "0"},
        {"t_rel": "1.0", "x": "1", "y": "0", "yaw_deg": "0"},
        {"t_rel": "6.0", "x": "3", "y": "0", "yaw_deg": "10"},
        {"t_rel": "6.5", "x": "9", "y": "0", "yaw_deg": "10"},
    ]
    selected = select_window(samples, 1.0, 6.0)
    assert [row["t_rel"] for row in selected] == ["1.0", "6.0"]


def test_extract_trial_measurement():
    samples = [
        {"t_rel": "1.0", "x": "0", "y": "0", "yaw_deg": "0"},
        {"t_rel": "6.0", "x": "1.0", "y": "0", "yaw_deg": "2"},
    ]
    measurement, reason = extract_trial_measurement(samples)
    assert reason is None
    assert measurement is not None
    assert abs(measurement["measured_actual_velocity"] - 0.2) < 1e-9
    assert measurement["yaw_drift_statistic"] == 2.0


def test_missing_position_or_yaw_blocks_extraction():
    samples = [
        {"t_rel": "1.0", "x": "0", "y": "0"},
        {"t_rel": "6.0", "x": "1.0", "y": "0"},
    ]
    measurement, reason = extract_trial_measurement(samples)
    assert measurement is None
    assert reason == "insufficient_position_or_yaw_samples"


def test_extract_from_logs_outputs_schema_without_fabrication(tmp_path):
    log = tmp_path / "trial_log.csv"
    with log.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["trial_id", "t_rel", "x", "y", "yaw_rad"])
        writer.writeheader()
        writer.writerow({"trial_id": "M19_trial", "t_rel": "1.0", "x": "0", "y": "0", "yaw_rad": "0"})
        writer.writerow({"trial_id": "M19_trial", "t_rel": "6.0", "x": "1.0", "y": "0", "yaw_rad": str(math.radians(5))})
        writer.writerow({"trial_id": "blocked", "t_rel": "1.0", "x": "", "y": "", "yaw_rad": ""})
    output_csv = tmp_path / "measurements.csv"
    output_dir = tmp_path / "out"

    summary = extract_from_logs(log, output_csv, output_dir)

    assert summary["measurements_extracted"] == 1
    assert summary["statistics_computed"] is False
    rows = list(csv.DictReader(output_csv.open(encoding="utf-8")))
    assert list(rows[0].keys()) == OUTPUT_FIELDS
    assert rows[0]["trial_id"] == "M19_trial"
    assert rows[0]["measurement_source"] == "sdk_state_log"
    assert rows[0]["measured_actual_velocity"]
    assert not any(row["trial_id"] == "blocked" for row in rows)
