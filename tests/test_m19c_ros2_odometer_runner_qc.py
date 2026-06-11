import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.extract_m19_measurements_from_ros2_odometer_logs import OUTPUT_FIELDS as EXTRACTION_FIELDS
from scripts.qc_m19c_ros2_odometer_measurement_run import qc_measurement_run
from scripts.run_m19c_ros2_odometer_trials import (
    BLOCK_SCHEDULE,
    LOG_FIELDS,
    TRIAL_RECORD_FIELDS,
    generate_trial_plan,
    phase_at,
    speed_code,
    trial_id,
    write_run_summary,
)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def test_trial_id_generation():
    assert speed_code(0.4) == "U040"
    assert trial_id("S1_lab_hard_floor", 1, 0.4, 1) == "M19C_S1_lab_hard_floor_B1_U040_R1"


def test_block_schedule_generation():
    plan = generate_trial_plan("S1_lab_hard_floor")
    assert len(plan) == 24
    assert [item["command_velocity"] for item in plan[:8]] == BLOCK_SCHEDULE[0]
    assert plan[0]["trial_id"] == "M19C_S1_lab_hard_floor_B1_U010_R1"
    assert len(generate_trial_plan()) == 72


def test_dry_run_summary_generation(tmp_path):
    plan = generate_trial_plan("S2_marble_floor")
    summary = write_run_summary(plan, False, tmp_path, "pending_full_m19c_measurement_run", "S2_marble_floor")
    assert summary["status"] == "pending_full_m19c_measurement_run"
    assert summary["planned_trials"] == 24
    assert not summary["empirical_analysis_computed"]
    assert (tmp_path / "m19c_measurement_run_summary.json").exists()
    assert (tmp_path / "m19c_measurement_run_report.md").exists()


def test_phase_at_boundaries():
    assert phase_at(0.5) == "idle"
    assert phase_at(3.0) == "command"
    assert phase_at(8.1) == "stop"


def record(trial, log_path):
    return {
        "trial_id": trial["trial_id"],
        "session_id": "fixture",
        "robot_id": "K1_fixture",
        "environment_id": trial["surface_id"],
        "surface_type": trial["surface_type"],
        "command_velocity": trial["command_velocity"],
        "block_index": trial["block_index"],
        "repeat_index": trial["repeat_index"],
        "idle_sec": 2,
        "command_sec": 6,
        "stop_sec": 2,
        "state_log_path": str(log_path),
        "valid": "TRUE",
        "invalid_reason": "",
        "timestamp": "fixture",
        "notes": "synthetic test fixture",
    }


def test_qc_detects_missing_logs(tmp_path):
    trial = generate_trial_plan("S1_lab_hard_floor")[0]
    records = tmp_path / "records.csv"
    extraction = tmp_path / "extraction.csv"
    write_csv(records, [record(trial, tmp_path / "missing.csv")], TRIAL_RECORD_FIELDS)
    write_csv(extraction, [], EXTRACTION_FIELDS)
    summary = qc_measurement_run(records, extraction, tmp_path / "out")
    assert summary["status"] == "pending_full_m19c_measurement_run"
    assert summary["missing_state_logs"] == [trial["trial_id"]]
    assert summary["missing_velocity"] == [trial["trial_id"]]


def test_qc_detects_duplicate_trial_ids(tmp_path):
    trial = generate_trial_plan("S1_lab_hard_floor")[0]
    log_path = tmp_path / "log.csv"
    write_csv(log_path, [{"phase": "command"}], LOG_FIELDS)
    records = tmp_path / "records.csv"
    extraction = tmp_path / "extraction.csv"
    write_csv(records, [record(trial, log_path), record(trial, log_path)], TRIAL_RECORD_FIELDS)
    write_csv(extraction, [], EXTRACTION_FIELDS)
    summary = qc_measurement_run(records, extraction, tmp_path / "out")
    assert summary["duplicate_trial_ids"] == [trial["trial_id"]]


def test_extraction_output_schema_constant():
    assert "analysis_window_start_sec" in EXTRACTION_FIELDS
    assert "imu_yaw_drift_deg" in EXTRACTION_FIELDS
