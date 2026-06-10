"""M19R real test CSV QC and blocker-aware measurement ingestion."""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SURFACES = ["S1_lab_hard_floor", "S2_marble_floor", "S3_artificial_turf"]
COMMAND_VELOCITIES = [0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60]
EXPECTED_REPEATS = 3
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
TRIAL_ID_RE = re.compile(
    r"^M19_(S[123]_[A-Za-z0-9_]+)_B(?P<block>\d+)_U(?P<cmd>\d{3})_R(?P<repeat>\d+)$"
)
DEBUG_KEYWORDS = (
    "returned 400",
    "move_nonzero_return_400",
    "command_not_effective_no_motion",
    "execution_error",
    "debug_invalid_command_path",
)


def default_input_csv() -> Path:
    local = Path("data/m19_repeated_validation_inputs/m19_trial_records.csv")
    if local.exists():
        return local
    desktop_data = Path.cwd().resolve().parent.parent / "data" / "m19_repeated_validation_inputs" / "m19_trial_records.csv"
    return desktop_data


def read_csv_records(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().upper() == "TRUE"


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return number


def debug_indicator(row: dict[str, str]) -> bool:
    blob = " ".join(
        str(row.get(key, ""))
        for key in ("trial_id", "invalid_reason", "notes", "raw_log_path", "normalized_record_path")
    ).lower()
    if any(keyword in blob for keyword in DEBUG_KEYWORDS):
        return True
    duration = parse_float(row.get("trial_duration_sec"))
    return not parse_bool(row.get("valid")) and duration is not None and duration <= 0.1


def resolve_data_path(value: str | None, input_csv: Path) -> Path | None:
    if not value or not value.strip():
        return None
    candidate = Path(value.strip())
    if candidate.is_absolute():
        return candidate
    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate
    desktop_candidate = input_csv.resolve().parents[1] / candidate.relative_to("data") if candidate.parts and candidate.parts[0] == "data" else None
    if desktop_candidate and desktop_candidate.exists():
        return desktop_candidate
    input_relative = input_csv.resolve().parent / candidate
    if input_relative.exists():
        return input_relative
    return cwd_candidate


def _extract_series(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("samples", "records", "messages", "data", "trajectory", "states"):
        value = payload.get(key)
        if isinstance(value, list):
            return [p for p in value if isinstance(p, dict)]
    return []


def _first_number(sample: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        if key in sample:
            parsed = parse_float(sample[key])
            if parsed is not None:
                return parsed
    pose = sample.get("pose")
    if isinstance(pose, dict):
        for key in keys:
            if key in pose:
                parsed = parse_float(pose[key])
                if parsed is not None:
                    return parsed
    return None


def compute_measurements_from_normalized(path: Path, row: dict[str, str]) -> tuple[float, float] | None:
    if not path.exists() or path.suffix.lower() != ".json":
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    samples = _extract_series(payload)
    start = parse_float(row.get("analysis_window_start_sec")) or 1.0
    end = parse_float(row.get("analysis_window_end_sec")) or 6.0
    usable: list[tuple[float, float | None, float | None, float | None]] = []
    for sample in samples:
        t = _first_number(sample, ("t", "time", "timestamp", "time_sec", "elapsed_sec"))
        if t is None or t < start or t > end:
            continue
        x = _first_number(sample, ("x", "position_x", "odom_x", "base_x"))
        yaw = _first_number(sample, ("yaw", "theta", "heading", "yaw_rad", "yaw_deg"))
        vx = _first_number(sample, ("vx", "linear_x", "velocity_x", "actual_velocity", "forward_velocity"))
        usable.append((t, x, yaw, vx))
    if len(usable) < 2:
        return None
    vx_values = [item[3] for item in usable if item[3] is not None]
    if vx_values:
        actual = statistics.fmean(vx_values)
    else:
        positions = [(t, x) for t, x, _, _ in usable if x is not None]
        if len(positions) < 2:
            return None
        actual = (positions[-1][1] - positions[0][1]) / (positions[-1][0] - positions[0][0])
    yaw_points = [(t, yaw) for t, _, yaw, _ in usable if yaw is not None]
    if len(yaw_points) < 2:
        return None
    yaw_drift = abs(yaw_points[-1][1] - yaw_points[0][1])
    return actual, yaw_drift


def build_qc(input_csv: Path, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    rows = read_csv_records(input_csv)
    trial_counts = Counter(row.get("trial_id", "") for row in rows)
    duplicates = sorted(trial_id for trial_id, count in trial_counts.items() if trial_id and count > 1)
    malformed = sorted(row.get("trial_id", "") for row in rows if not TRIAL_ID_RE.match(row.get("trial_id", "")))

    per_surface: dict[str, dict[str, int]] = {}
    per_cell: list[dict[str, Any]] = []
    valid_rows: list[dict[str, str]] = []
    invalid_rows: list[dict[str, str]] = []
    measurement_rows: list[dict[str, Any]] = []
    extracted_actual = 0
    extracted_yaw = 0
    missing_raw = 0
    missing_normalized = 0

    for row in rows:
        if parse_bool(row.get("valid")) and not debug_indicator(row):
            valid_rows.append(row)
        else:
            invalid_rows.append(row)
        raw_path = resolve_data_path(row.get("raw_log_path"), input_csv)
        norm_path = resolve_data_path(row.get("normalized_record_path"), input_csv)
        if not raw_path or not raw_path.exists():
            missing_raw += 1
        if not norm_path or not norm_path.exists():
            missing_normalized += 1
        actual = parse_float(row.get("measured_actual_velocity"))
        yaw = parse_float(row.get("yaw_drift_statistic"))
        if (actual is None or yaw is None) and norm_path:
            computed = compute_measurements_from_normalized(norm_path, row)
            if computed:
                if actual is None:
                    actual = computed[0]
                    extracted_actual += 1
                if yaw is None:
                    yaw = computed[1]
                    extracted_yaw += 1
        measurement_rows.append({"row": row, "actual": actual, "yaw": yaw})

    for surface in SURFACES:
        surface_rows = [row for row in rows if row.get("surface_id") == surface or row.get("environment_id") == surface]
        surface_valid = [row for row in valid_rows if row.get("surface_id") == surface or row.get("environment_id") == surface]
        per_surface[surface] = {"total": len(surface_rows), "valid": len(surface_valid)}
        for command in COMMAND_VELOCITIES:
            cell_rows = [
                row for row in rows
                if (row.get("surface_id") == surface or row.get("environment_id") == surface)
                and parse_float(row.get("command_velocity")) == command
            ]
            cell_valid = [row for row in cell_rows if parse_bool(row.get("valid")) and not debug_indicator(row)]
            per_cell.append(
                {
                    "surface_id": surface,
                    "command_velocity": command,
                    "n_total": len(cell_rows),
                    "n_valid": len(cell_valid),
                    "complete": len(cell_valid) >= EXPECTED_REPEATS,
                }
            )

    valid_measurements = [
        item for item in measurement_rows
        if parse_bool(item["row"].get("valid")) and not debug_indicator(item["row"])
    ]
    missing_actual_valid = sum(1 for item in valid_measurements if item["actual"] is None)
    missing_yaw_valid = sum(1 for item in valid_measurements if item["yaw"] is None)
    measurements_available = missing_actual_valid == 0 and missing_yaw_valid == 0 and bool(valid_measurements)
    validation_status = "complete_real_data_evidence" if measurements_available else "blocked_missing_actual_velocity_or_yaw"

    summary = {
        "analysis_timestamp": datetime.now().isoformat(),
        "input_csv": str(input_csv),
        "validation_status": validation_status,
        "total_rows": len(rows),
        "valid_rows": len(valid_rows),
        "invalid_or_debug_rows": len(invalid_rows),
        "per_surface": per_surface,
        "per_surface_speed_cell": per_cell,
        "duplicate_trial_ids": duplicates,
        "malformed_trial_ids": malformed,
        "missing_command_velocity_rows": sum(1 for row in rows if parse_float(row.get("command_velocity")) is None),
        "missing_actual_velocity_valid_rows": missing_actual_valid,
        "missing_yaw_drift_valid_rows": missing_yaw_valid,
        "missing_raw_log_path_or_file_rows": missing_raw,
        "missing_normalized_record_path_or_file_rows": missing_normalized,
        "measured_actual_velocity_available_or_computed": missing_actual_valid == 0 and bool(valid_measurements),
        "yaw_drift_statistic_available_or_computed": missing_yaw_valid == 0 and bool(valid_measurements),
        "actual_velocity_extracted_from_logs": extracted_actual,
        "yaw_drift_extracted_from_logs": extracted_yaw,
        "debug_invalid_command_path_rows": sum(1 for row in rows if debug_indicator(row)),
        "cells_with_at_least_3_valid_trials": sum(1 for cell in per_cell if cell["complete"]),
        "expected_cells": len(SURFACES) * len(COMMAND_VELOCITIES),
    }
    write_outputs(output_dir, summary, rows, measurement_rows)
    return summary


def _csv_write(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def aggregate_rows(summary: dict[str, Any], measurement_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for cell in summary["per_surface_speed_cell"]:
        surface = cell["surface_id"]
        command = cell["command_velocity"]
        matches = [
            item for item in measurement_rows
            if (item["row"].get("surface_id") == surface or item["row"].get("environment_id") == surface)
            and parse_float(item["row"].get("command_velocity")) == command
            and parse_bool(item["row"].get("valid"))
            and not debug_indicator(item["row"])
        ]
        actuals = [item["actual"] for item in matches if item["actual"] is not None]
        yaws = [item["yaw"] for item in matches if item["yaw"] is not None]
        missing_measurements = len(actuals) < len(matches) or len(yaws) < len(matches)
        mean_actual = statistics.fmean(actuals) if actuals and not missing_measurements else None
        std_actual = statistics.pstdev(actuals) if len(actuals) > 1 and not missing_measurements else None
        mean_tracking = mean_actual - command if mean_actual is not None else None
        abs_tracking = abs(mean_tracking) if mean_tracking is not None else None
        relative_under = (command - mean_actual) / command if mean_actual is not None and command else None
        no_motion_ratio = sum(1 for value in actuals if value < 0.02) / len(actuals) if actuals and not missing_measurements else None
        mean_yaw = statistics.fmean(yaws) if yaws and not missing_measurements else None
        yaw_risk = 1.0 if mean_yaw is not None and abs(mean_yaw) > 2.0 else (None if missing_measurements else 0.0)
        uncertainty = std_actual if std_actual is not None else (None if missing_measurements else 0.0)
        risk_score = (
            abs_tracking + (uncertainty or 0.0) + (1.0 if no_motion_ratio and no_motion_ratio > 0.5 else 0.0) + (yaw_risk or 0.0)
            if not missing_measurements and abs_tracking is not None
            else None
        )
        if missing_measurements:
            region = "pending_measurement_extraction"
            evidence = "pending_measurement_extraction"
        elif len(matches) < EXPECTED_REPEATS:
            region = "insufficient_evidence"
            evidence = "real_single_or_sparse"
        elif no_motion_ratio and no_motion_ratio > 0.5:
            region = "deadzone"
            evidence = "real_repeated"
        elif yaw_risk and yaw_risk > 0.5:
            region = "drift_prone"
            evidence = "real_repeated"
        elif abs_tracking is not None and abs_tracking > 0.05:
            region = "under_track"
            evidence = "real_repeated"
        else:
            region = "reliable"
            evidence = "real_repeated"
        output.append(
            {
                "surface_id": surface,
                "command_velocity": command,
                "n_total": cell["n_total"],
                "n_valid": cell["n_valid"],
                "mean_actual_velocity": mean_actual,
                "std_actual_velocity": std_actual,
                "mean_tracking_error": mean_tracking,
                "abs_mean_tracking_error": abs_tracking,
                "relative_under_tracking": relative_under,
                "no_motion_ratio": no_motion_ratio,
                "mean_yaw_drift": mean_yaw,
                "yaw_drift_risk": yaw_risk,
                "uncertainty": uncertainty,
                "risk_score": risk_score,
                "region_label": region,
                "evidence_level": evidence,
            }
        )
    return output


def write_outputs(output_dir: Path, summary: dict[str, Any], rows: list[dict[str, str]], measurement_rows: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19r_qc_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    aggregates = aggregate_rows(summary, measurement_rows)
    aggregate_fields = [
        "surface_id", "command_velocity", "n_total", "n_valid", "mean_actual_velocity",
        "std_actual_velocity", "mean_tracking_error", "abs_mean_tracking_error",
        "relative_under_tracking", "no_motion_ratio", "mean_yaw_drift", "yaw_drift_risk",
        "uncertainty", "risk_score", "region_label", "evidence_level",
    ]
    _csv_write(output_dir / "surface_response_statistics.csv", aggregates, aggregate_fields)
    _csv_write(output_dir / "repeated_validation_table.csv", aggregates, aggregate_fields)
    _csv_write(
        output_dir / "region_classification.csv",
        aggregates,
        ["surface_id", "command_velocity", "n_total", "n_valid", "region_label", "evidence_level"],
    )
    _csv_write(
        output_dir / "yaw_drift_summary.csv",
        aggregates,
        ["surface_id", "command_velocity", "n_total", "n_valid", "mean_yaw_drift", "yaw_drift_risk", "region_label"],
    )
    validation_summary = {
        "analysis_timestamp": summary["analysis_timestamp"],
        "mode": "blocked_missing_measurement" if summary["validation_status"].startswith("blocked") else "real_data",
        "validation_status": summary["validation_status"],
        "total_trials": summary["total_rows"],
        "total_valid": summary["valid_rows"],
        "commands_evaluated": 0 if summary["validation_status"].startswith("blocked") else len(aggregates),
        "commands_pending": len(aggregates) if summary["validation_status"].startswith("blocked") else 0,
        "per_command": aggregates,
        "notes": "Actual velocity and yaw drift are missing or not computable from available files."
        if summary["validation_status"].startswith("blocked")
        else "Real M19 measurements ingested.",
        "real_repeated_logs_found": True,
        "cross_robot_generalization_claimed": False,
        "compensation_implemented": False,
        "safe_command_adapter_implemented": False,
        "navigation_improvement_claimed": False,
    }
    (output_dir / "repeated_validation_summary.json").write_text(json.dumps(validation_summary, indent=2), encoding="utf-8")
    report = render_report(summary, aggregates)
    (output_dir / "m19r_qc_report.md").write_text(report, encoding="utf-8")
    (output_dir / "m19_validation_report.md").write_text(report, encoding="utf-8")
    if summary["validation_status"].startswith("blocked"):
        (output_dir / "m19r_missing_measurement_report.md").write_text(render_missing_report(summary), encoding="utf-8")


def render_report(summary: dict[str, Any], aggregates: list[dict[str, Any]]) -> str:
    surface_lines = "\n".join(
        f"- {surface}: {counts['valid']} valid / {counts['total']} total"
        for surface, counts in summary["per_surface"].items()
    )
    incomplete = [cell for cell in summary["per_surface_speed_cell"] if not cell["complete"]]
    incomplete_lines = "\n".join(
        f"- {cell['surface_id']} @ {cell['command_velocity']:.2f} m/s: {cell['n_valid']} valid / {cell['n_total']} total"
        for cell in incomplete
    ) or "- None"
    return (
        "# M19R Real Test QC Report\n\n"
        f"Validation status: `{summary['validation_status']}`\n\n"
        f"Input CSV: `{summary['input_csv']}`\n\n"
        f"Total rows: {summary['total_rows']}\n\n"
        f"Valid formal rows after debug exclusion: {summary['valid_rows']}\n\n"
        f"Invalid/debug rows excluded: {summary['invalid_or_debug_rows']}\n\n"
        "## Valid Rows Per Surface\n"
        f"{surface_lines}\n\n"
        "## Incomplete Surface-Speed Cells\n"
        f"{incomplete_lines}\n\n"
        "## Measurement Availability\n"
        f"- measured_actual_velocity available or computed: {summary['measured_actual_velocity_available_or_computed']}\n"
        f"- yaw_drift_statistic available or computed: {summary['yaw_drift_statistic_available_or_computed']}\n"
        f"- valid rows missing actual velocity: {summary['missing_actual_velocity_valid_rows']}\n"
        f"- valid rows missing yaw drift: {summary['missing_yaw_drift_valid_rows']}\n"
        f"- rows with missing raw log files: {summary['missing_raw_log_path_or_file_rows']}\n"
        f"- rows with missing normalized files: {summary['missing_normalized_record_path_or_file_rows']}\n\n"
        "No empirical response-model claim is added while measurement extraction is blocked.\n"
    )


def render_missing_report(summary: dict[str, Any]) -> str:
    return (
        "# M19R Missing Measurement Report\n\n"
        "Real M19 trial execution metadata was found, but empirical analysis is blocked.\n\n"
        f"- Validation status: `{summary['validation_status']}`\n"
        f"- Total CSV rows: {summary['total_rows']}\n"
        f"- Valid formal rows after debug exclusion: {summary['valid_rows']}\n"
        f"- Valid rows missing `measured_actual_velocity`: {summary['missing_actual_velocity_valid_rows']}\n"
        f"- Valid rows missing `yaw_drift_statistic`: {summary['missing_yaw_drift_valid_rows']}\n"
        f"- Rows with missing raw log files: {summary['missing_raw_log_path_or_file_rows']}\n"
        f"- Rows with missing normalized record files: {summary['missing_normalized_record_path_or_file_rows']}\n\n"
        "The available CSV cannot support repeated response statistics without velocity and yaw extraction. "
        "Command velocity, notes, or trial duration were not used as substitutes for measurements.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=default_input_csv())
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    if not args.input_csv.exists():
        print(f"Input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    summary = build_qc(args.input_csv, args.output_dir)
    print(f"M19R validation_status={summary['validation_status']}")
    print(f"Wrote outputs to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
