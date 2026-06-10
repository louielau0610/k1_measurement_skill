import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.qc_m19_real_test_records import (
    COMMAND_VELOCITIES,
    SURFACES,
    build_qc,
    compute_measurements_from_normalized,
    debug_indicator,
    parse_float,
)


FIELDNAMES = [
    "trial_id",
    "session_id",
    "robot_id",
    "environment_id",
    "environment_description",
    "surface_type",
    "command_velocity",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "trial_duration_sec",
    "valid",
    "invalid_reason",
    "raw_log_path",
    "normalized_record_path",
    "timestamp",
    "notes",
    "surface_id",
    "block_index",
    "repeat_index",
    "command_window_sec",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "battery_start",
    "battery_end",
    "measurement_source",
    "operator",
    "logger_version",
]


def row(surface, command, repeat, *, valid=True, actual="", yaw="", reason="", notes="", duration="11.0", norm=""):
    return {
        "trial_id": f"M19_{surface}_B1_U{int(round(command * 100)):03d}_R{repeat}",
        "session_id": "M19_TEST",
        "robot_id": "K1_001",
        "environment_id": surface,
        "environment_description": surface,
        "surface_type": surface.removeprefix("S1_").removeprefix("S2_").removeprefix("S3_"),
        "command_velocity": str(command),
        "measured_actual_velocity": actual,
        "yaw_drift_statistic": yaw,
        "trial_duration_sec": duration,
        "valid": "TRUE" if valid else "FALSE",
        "invalid_reason": reason,
        "raw_log_path": "",
        "normalized_record_path": norm,
        "timestamp": "2026-06-10T00:00:00",
        "notes": notes,
        "surface_id": surface,
        "block_index": "1",
        "repeat_index": str(repeat),
        "command_window_sec": "6.0",
        "analysis_window_start_sec": "1.0",
        "analysis_window_end_sec": "6.0",
        "battery_start": "",
        "battery_end": "",
        "measurement_source": "fixture",
        "operator": "fixture",
        "logger_version": "fixture",
    }


def write_records(path, records):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def test_parse_float_rejects_missing_and_nonfinite():
    assert parse_float("") is None
    assert parse_float("nan") is None
    assert parse_float("0.25") == 0.25


def test_debug_invalid_command_path_detection():
    rec = row("S1_lab_hard_floor", 0.1, 1, valid=False, reason="execution_error: Move returned 400", duration="1.0")
    assert debug_indicator(rec)


def test_qc_blocks_when_valid_measurements_are_missing(tmp_path):
    csv_path = tmp_path / "m19_trial_records.csv"
    records = [
        row("S1_lab_hard_floor", 0.1, 1),
        row("S1_lab_hard_floor", 0.1, 2),
        row("S1_lab_hard_floor", 0.1, 3, valid=False, reason="execution_error:RuntimeError:Move returned 400"),
    ]
    write_records(csv_path, records)

    output_dir = tmp_path / "out"
    summary = build_qc(csv_path, output_dir)

    assert summary["total_rows"] == 3
    assert summary["valid_rows"] == 2
    assert summary["invalid_or_debug_rows"] == 1
    assert summary["validation_status"] == "blocked_missing_actual_velocity_or_yaw"
    assert (output_dir / "m19r_missing_measurement_report.md").exists()
    regions = (output_dir / "region_classification.csv").read_text(encoding="utf-8")
    assert "pending_measurement_extraction" in regions


def test_qc_computes_complete_real_data_evidence(tmp_path):
    csv_path = tmp_path / "m19_trial_records.csv"
    records = [
        row("S1_lab_hard_floor", 0.3, 1, actual="0.28", yaw="0.2"),
        row("S1_lab_hard_floor", 0.3, 2, actual="0.29", yaw="0.3"),
        row("S1_lab_hard_floor", 0.3, 3, actual="0.27", yaw="0.4"),
    ]
    write_records(csv_path, records)

    summary = build_qc(csv_path, tmp_path / "out")

    assert summary["missing_actual_velocity_valid_rows"] == 0
    assert summary["missing_yaw_drift_valid_rows"] == 0
    assert summary["validation_status"] == "complete_real_data_evidence"
    stats = list(csv.DictReader((tmp_path / "out" / "surface_response_statistics.csv").open(encoding="utf-8")))
    target = [
        item for item in stats
        if item["surface_id"] == "S1_lab_hard_floor" and item["command_velocity"] == "0.3"
    ][0]
    assert abs(float(target["mean_actual_velocity"]) - 0.28) < 0.001


def test_normalized_json_extraction(tmp_path):
    norm = tmp_path / "trial.json"
    norm.write_text(
        json.dumps(
            {
                "samples": [
                    {"time_sec": 0.5, "x": 0.0, "yaw": 0.0},
                    {"time_sec": 1.0, "x": 0.1, "yaw": 0.1},
                    {"time_sec": 6.0, "x": 1.1, "yaw": 0.4},
                ]
            }
        ),
        encoding="utf-8",
    )
    measurements = compute_measurements_from_normalized(
        norm,
        {"analysis_window_start_sec": "1.0", "analysis_window_end_sec": "6.0"},
    )
    assert measurements is not None
    actual, yaw = measurements
    assert abs(actual - 0.2) < 0.001
    assert abs(yaw - 0.3) < 0.001


def test_expected_matrix_constants():
    assert len(SURFACES) * len(COMMAND_VELOCITIES) == 24
