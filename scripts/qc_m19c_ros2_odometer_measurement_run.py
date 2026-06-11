"""QC the M19C ROS2 odometer measurement run before empirical analysis."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from extract_m19_measurements_from_ros2_odometer_logs import parse_float
from run_m19c_ros2_odometer_trials import BLOCK_SCHEDULE, SURFACES, TRIAL_RECORD_CSV, generate_trial_plan

EXTRACTION_CSV = Path("data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def count_phase_rows(path: Path, phase: str) -> int:
    return sum(1 for row in read_csv(path) if row.get("phase") == phase)


def qc_measurement_run(
    trial_records_csv: Path = TRIAL_RECORD_CSV,
    extraction_csv: Path = EXTRACTION_CSV,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    records = read_csv(trial_records_csv)
    extracted = read_csv(extraction_csv)
    extracted_by_id = {row.get("trial_id", ""): row for row in extracted}
    expected_ids = {trial["trial_id"] for trial in generate_trial_plan()}
    observed_ids = [row.get("trial_id", "") for row in records]
    duplicates = sorted(trial_id for trial_id, count in Counter(observed_ids).items() if trial_id and count > 1)

    per_surface = Counter(row.get("environment_id", "") for row in records)
    per_cell_repeat: dict[str, int] = defaultdict(int)
    missing_logs = []
    missing_velocity = []
    missing_yaw = []
    suspicious_zero_velocity = []
    negative_forward_distance = []
    yaw_mismatch = []
    state_log_row_counts = {}
    command_phase_row_counts = {}

    for row in records:
        trial_id = row.get("trial_id", "")
        surface = row.get("environment_id", "")
        command = row.get("command_velocity", "")
        repeat = row.get("repeat_index", "")
        per_cell_repeat[f"{surface}|{command}|{repeat}"] += 1
        log_path = Path(row.get("state_log_path", ""))
        if not log_path.exists():
            missing_logs.append(trial_id)
            state_log_row_counts[trial_id] = 0
            command_phase_row_counts[trial_id] = 0
        else:
            log_rows = read_csv(log_path)
            state_log_row_counts[trial_id] = len(log_rows)
            command_phase_row_counts[trial_id] = count_phase_rows(log_path, "command")
        measurement = extracted_by_id.get(trial_id, {})
        velocity = parse_float(measurement.get("measured_actual_velocity"))
        yaw = parse_float(measurement.get("yaw_drift_statistic"))
        distance = parse_float(measurement.get("distance_m"))
        command_velocity = parse_float(command)
        imu_yaw = parse_float(measurement.get("imu_yaw_drift_deg"))
        if velocity is None:
            missing_velocity.append(trial_id)
        if yaw is None:
            missing_yaw.append(trial_id)
        if velocity is not None and command_velocity is not None and command_velocity >= 0.20 and abs(velocity) < 1e-5:
            suspicious_zero_velocity.append(trial_id)
        if distance is not None and distance < 0:
            negative_forward_distance.append(trial_id)
        if yaw is not None and imu_yaw is not None and abs(yaw - imu_yaw) > 5.0:
            yaw_mismatch.append({"trial_id": trial_id, "odom_yaw": yaw, "imu_yaw": imu_yaw})

    complete_ids = set(observed_ids)
    missing_expected_ids = sorted(expected_ids - complete_ids)
    unexpected_ids = sorted(complete_ids - expected_ids)
    complete_repeats = len([key for key, count in per_cell_repeat.items() if count == 1])
    all_expected_present = not missing_expected_ids and not unexpected_ids and len(records) == len(expected_ids)
    extraction_ready = (
        all_expected_present
        and not duplicates
        and not missing_logs
        and not missing_velocity
        and not missing_yaw
        and len(extracted_by_id) == len(expected_ids)
    )
    status = "m19c_measurement_extraction_ready_for_empirical_analysis" if extraction_ready else "pending_full_m19c_measurement_run"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "trial_records_csv": str(trial_records_csv),
        "extraction_csv": str(extraction_csv),
        "trial_record_count": len(records),
        "expected_trial_count": len(expected_ids),
        "per_surface_trial_count": dict(per_surface),
        "per_surface_speed_repeat_entries": complete_repeats,
        "missing_expected_trial_ids": missing_expected_ids,
        "unexpected_trial_ids": unexpected_ids,
        "duplicate_trial_ids": duplicates,
        "missing_state_logs": missing_logs,
        "state_log_row_counts": state_log_row_counts,
        "command_phase_row_counts": command_phase_row_counts,
        "extracted_measurement_count": len(extracted_by_id),
        "missing_velocity": missing_velocity,
        "missing_yaw_drift": missing_yaw,
        "suspicious_zero_velocity_at_non_low_speeds": suspicious_zero_velocity,
        "negative_forward_distance": negative_forward_distance,
        "odom_imu_yaw_drift_mismatch": yaw_mismatch,
        "empirical_analysis_computed": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19c_measurement_run_qc_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19c_measurement_run_qc_report.md").write_text(render_qc_report(summary), encoding="utf-8")
    (output_dir / "m19c_measurement_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19c_measurement_run_report.md").write_text(render_qc_report(summary), encoding="utf-8")
    return summary


def render_qc_report(summary: dict[str, Any]) -> str:
    return (
        "# M19C ROS2 Odometer Measurement Run QC\n\n"
        f"Status: `{summary['status']}`\n\n"
        f"Trial records: {summary['trial_record_count']} / {summary['expected_trial_count']}\n\n"
        f"Extracted measurements: {summary['extracted_measurement_count']}\n\n"
        f"Duplicate trial IDs: {len(summary['duplicate_trial_ids'])}\n\n"
        f"Missing state logs: {len(summary['missing_state_logs'])}\n\n"
        f"Missing velocity: {len(summary['missing_velocity'])}\n\n"
        f"Missing yaw drift: {len(summary['missing_yaw_drift'])}\n\n"
        f"Suspicious zero velocity at non-low speeds: {len(summary['suspicious_zero_velocity_at_non_low_speeds'])}\n\n"
        f"Negative forward distance: {len(summary['negative_forward_distance'])}\n\n"
        f"Odom/IMU yaw drift mismatches: {len(summary['odom_imu_yaw_drift_mismatch'])}\n\n"
        "No empirical response analysis or risk-map validation is computed by this QC step.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-records", type=Path, default=TRIAL_RECORD_CSV)
    parser.add_argument("--extraction-csv", type=Path, default=EXTRACTION_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    summary = qc_measurement_run(args.trial_records, args.extraction_csv, args.output_dir)
    print(f"M19C measurement run status={summary['status']}")
    print(f"M19C trial records={summary['trial_record_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
