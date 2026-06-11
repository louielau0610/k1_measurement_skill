"""Measurement Data Contract v1.0.

Defines the formal cross-platform measurement data contract that Booster K1,
Unitree GO1, and Unitree G1 must satisfy before any velocity compensation
stage can consume their data.

Schema version: measurement_v1.0
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Schema version
# ---------------------------------------------------------------------------

MEASUREMENT_CONTRACT_VERSION = "measurement_v1.0"

# ---------------------------------------------------------------------------
# Extraction status enum
# ---------------------------------------------------------------------------

VALID_EXTRACTION_STATUSES = frozenset({
    "ok",
    "invalid_trial",
    "missing_log",
    "insufficient_samples",
    "missing_state_source",
    "extraction_error",
    "not_extracted",
})

# ---------------------------------------------------------------------------
# Trial-level contract fields
# ---------------------------------------------------------------------------

TRIAL_CONTRACT_FIELDS: list[str] = [
    "schema_version",
    "dataset_id",
    "session_id",
    "trial_id",
    "platform",
    "robot_model",
    "robot_id",
    "surface_type",
    "environment_id",
    "command_velocity_mps",
    "measured_actual_velocity_mps",
    "tracking_error_mps",
    "relative_tracking_error",
    "yaw_drift_deg",
    "imu_yaw_drift_deg",
    "state_source",
    "command_source",
    "measurement_source",
    "measurement_method",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "state_log_path",
    "raw_log_path",
    "extraction_status",
    "confidence",
    "invalid_reason",
    "created_at",
]

TRIAL_NUMERIC_FIELDS: list[str] = [
    "command_velocity_mps",
    "measured_actual_velocity_mps",
    "tracking_error_mps",
    "relative_tracking_error",
    "yaw_drift_deg",
    "imu_yaw_drift_deg",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
]

# ---------------------------------------------------------------------------
# Aggregate-level contract fields
# ---------------------------------------------------------------------------

AGGREGATE_CONTRACT_FIELDS: list[str] = [
    "schema_version",
    "dataset_id",
    "platform",
    "robot_model",
    "surface_type",
    "command_velocity_mps",
    "n",
    "mean_actual_velocity_mps",
    "std_actual_velocity_mps",
    "median_actual_velocity_mps",
    "min_actual_velocity_mps",
    "max_actual_velocity_mps",
    "mean_tracking_error_mps",
    "mean_abs_tracking_error_mps",
    "relative_tracking_error",
    "under_tracking_ratio",
    "no_motion_ratio",
    "mean_yaw_drift_deg",
    "std_yaw_drift_deg",
    "max_yaw_drift_deg",
    "response_uncertainty",
    "risk_score",
    "region_label",
    "evidence_level",
    "limitations",
]

# ---------------------------------------------------------------------------
# Session metadata contract fields
# ---------------------------------------------------------------------------

SESSION_METADATA_CONTRACT_FIELDS: list[str] = [
    "schema_version",
    "session_id",
    "dataset_id",
    "platform",
    "robot_model",
    "robot_id",
    "surfaces",
    "speeds_mps",
    "repeats",
    "block_order",
    "timing",
    "command_source",
    "state_sources",
    "coordinate_convention",
    "state_frame",
    "body_frame",
    "measurement_method",
    "analysis_window",
    "hardware_validated_reference",
    "operator_notes",
    "limitations",
    "created_at",
]

# ---------------------------------------------------------------------------
# Coordinate convention
# ---------------------------------------------------------------------------

COORDINATE_CONVENTION = {
    "body_x": "forward",
    "body_y": "left",
    "body_z": "up",
    "yaw_internal_unit": "radians",
    "yaw_export_unit": "degrees",
    "forward_displacement_method": "projection_onto_initial_heading",
}


def build_validation_report(
    valid: bool,
    errors: list[str],
    warnings: list[str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Build a structured validation report."""
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings or [],
        "contract_version": MEASUREMENT_CONTRACT_VERSION,
        **extra,
    }


# ---------------------------------------------------------------------------
# Trial-level validation
# ---------------------------------------------------------------------------

def validate_trial_measurement(row: dict[str, Any]) -> dict[str, Any]:
    """Validate a single trial measurement row against the contract.

    Returns a structured validation report.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required fields
    for field in TRIAL_CONTRACT_FIELDS:
        if field not in row:
            errors.append(f"missing_field:{field}")

    # Check numeric fields
    for field in TRIAL_NUMERIC_FIELDS:
        if field in row and row[field] not in (None, ""):
            try:
                float(row[field])
            except (TypeError, ValueError):
                errors.append(f"{field}:not_numeric")

    # Check extraction_status enum
    status = row.get("extraction_status", "")
    if status and status not in VALID_EXTRACTION_STATUSES:
        errors.append(f"extraction_status:invalid_enum:{status}")

    # Check invalid trial requires reason
    if status == "invalid_trial":
        reason = row.get("invalid_reason", "")
        if not reason or not str(reason).strip():
            errors.append("invalid_trial:missing_reason")

    # Check command velocity not copied as measured velocity
    try:
        cmd = float(row.get("command_velocity_mps", 0) or 0)
        meas = float(row.get("measured_actual_velocity_mps", 0) or 0)
        if cmd != 0 and abs(cmd - meas) < 1e-9:
            errors.append("command_velocity_copied_as_measured:values_identical")
    except (TypeError, ValueError):
        pass  # Already caught by numeric check

    # Check state_log_path or raw_log_path
    state_log = str(row.get("state_log_path", "")).strip()
    raw_log = str(row.get("raw_log_path", "")).strip()
    if not state_log and not raw_log:
        errors.append("missing_log_paths:both_state_and_raw_empty")
    elif state_log.lower() == "unavailable" and raw_log.lower() == "unavailable":
        errors.append("missing_log_paths:both_marked_unavailable")

    return build_validation_report(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        trial_id=row.get("trial_id", "unknown"),
    )


# ---------------------------------------------------------------------------
# Aggregate-level validation
# ---------------------------------------------------------------------------

def validate_aggregate_response(row: dict[str, Any]) -> dict[str, Any]:
    """Validate a single aggregate response row against the contract."""
    errors: list[str] = []
    warnings: list[str] = []

    for field in AGGREGATE_CONTRACT_FIELDS:
        if field not in row:
            errors.append(f"missing_field:{field}")

    numeric_agg = [
        "command_velocity_mps", "n",
        "mean_actual_velocity_mps", "std_actual_velocity_mps",
        "median_actual_velocity_mps", "min_actual_velocity_mps",
        "max_actual_velocity_mps", "mean_tracking_error_mps",
        "mean_abs_tracking_error_mps", "relative_tracking_error",
        "under_tracking_ratio", "no_motion_ratio",
        "mean_yaw_drift_deg", "std_yaw_drift_deg", "max_yaw_drift_deg",
        "response_uncertainty", "risk_score",
    ]
    for field in numeric_agg:
        if field in row and row[field] not in (None, ""):
            try:
                float(row[field])
            except (TypeError, ValueError):
                errors.append(f"{field}:not_numeric")

    # n must be positive integer
    if "n" in row and row["n"] not in (None, ""):
        try:
            n = int(row["n"])
            if n <= 0:
                errors.append("n:must_be_positive")
        except (TypeError, ValueError):
            errors.append("n:not_integer")

    return build_validation_report(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        surface_type=row.get("surface_type", "unknown"),
        command_velocity_mps=row.get("command_velocity_mps", "unknown"),
    )


# ---------------------------------------------------------------------------
# Session metadata validation
# ---------------------------------------------------------------------------

def validate_session_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate session metadata against the contract."""
    errors: list[str] = []
    warnings: list[str] = []

    for field in SESSION_METADATA_CONTRACT_FIELDS:
        if field not in metadata:
            errors.append(f"missing_field:{field}")

    # Check types
    for list_field in ("surfaces", "speeds_mps", "state_sources", "limitations"):
        if list_field in metadata and not isinstance(metadata[list_field], list):
            errors.append(f"{list_field}:must_be_list")

    if "repeats" in metadata:
        try:
            if int(metadata["repeats"]) <= 0:
                errors.append("repeats:must_be_positive")
        except (TypeError, ValueError):
            errors.append("repeats:must_be_integer")

    if "timing" in metadata and isinstance(metadata["timing"], dict):
        for key in ("idle_sec", "command_sec", "stop_sec"):
            if key in metadata["timing"]:
                try:
                    float(metadata["timing"][key])
                except (TypeError, ValueError):
                    errors.append(f"timing.{key}:not_numeric")

    if "coordinate_convention" in metadata:
        cc = metadata["coordinate_convention"]
        if isinstance(cc, dict):
            if cc.get("body_x") != "forward":
                errors.append("coordinate_convention.body_x:must_be_forward")
            if cc.get("body_y") != "left":
                errors.append("coordinate_convention.body_y:must_be_left")
            if cc.get("body_z") != "up":
                errors.append("coordinate_convention.body_z:must_be_up")

    return build_validation_report(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        session_id=metadata.get("session_id", "unknown"),
    )


# ---------------------------------------------------------------------------
# CSV-level validation
# ---------------------------------------------------------------------------

def validate_measurement_csv(path: Path) -> dict[str, Any]:
    """Validate a measurement CSV file against the contract.

    Returns a structured report with per-row results.
    """
    errors: list[str] = []
    row_results: list[dict[str, Any]] = []

    if not path.exists():
        return build_validation_report(
            valid=False,
            errors=[f"file_not_found:{path}"],
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            row_results=[],
        )

    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except Exception as exc:
        return build_validation_report(
            valid=False,
            errors=[f"csv_read_error:{exc}"],
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            row_results=[],
        )

    if not rows:
        return build_validation_report(
            valid=False,
            errors=["empty_csv"],
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            row_results=[],
        )

    valid_count = 0
    invalid_count = 0
    for row in rows:
        result = validate_trial_measurement(row)
        row_results.append(result)
        if result["valid"]:
            valid_count += 1
        else:
            invalid_count += 1
            errors.extend(result["errors"])

    return build_validation_report(
        valid=invalid_count == 0,
        errors=errors,
        total_rows=len(rows),
        valid_rows=valid_count,
        invalid_rows=invalid_count,
        row_results=row_results,
    )


def validate_response_statistics_csv(path: Path) -> dict[str, Any]:
    """Validate a response statistics CSV against the contract."""
    errors: list[str] = []
    row_results: list[dict[str, Any]] = []

    if not path.exists():
        return build_validation_report(
            valid=False,
            errors=[f"file_not_found:{path}"],
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            row_results=[],
        )

    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except Exception as exc:
        return build_validation_report(
            valid=False,
            errors=[f"csv_read_error:{exc}"],
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            row_results=[],
        )

    valid_count = 0
    invalid_count = 0
    for row in rows:
        result = validate_aggregate_response(row)
        row_results.append(result)
        if result["valid"]:
            valid_count += 1
        else:
            invalid_count += 1
            errors.extend(result["errors"])

    return build_validation_report(
        valid=invalid_count == 0,
        errors=errors,
        total_rows=len(rows),
        valid_rows=valid_count,
        invalid_rows=invalid_count,
        row_results=row_results,
    )


def validate_session_directory(session_dir: Path) -> dict[str, Any]:
    """Validate a measurement session directory against the contract.

    Checks for required files and validates each.
    """
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, dict[str, Any]] = {}

    session_dir = Path(session_dir)
    if not session_dir.is_dir():
        return build_validation_report(
            valid=False,
            errors=[f"directory_not_found:{session_dir}"],
            checks={},
        )

    # Check session_metadata.json
    metadata_path = session_dir / "session_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            meta_result = validate_session_metadata(metadata)
            checks["session_metadata"] = meta_result
            if not meta_result["valid"]:
                errors.extend(meta_result["errors"])
        except Exception as exc:
            checks["session_metadata"] = build_validation_report(False, [str(exc)])
            errors.append(f"session_metadata_parse_error:{exc}")
    else:
        checks["session_metadata"] = build_validation_report(False, ["session_metadata.json:missing"])
        errors.append("session_metadata.json:missing")

    # Check extracted_measurements.csv
    meas_path = session_dir / "extracted_measurements.csv"
    if meas_path.exists():
        meas_result = validate_measurement_csv(meas_path)
        checks["extracted_measurements"] = meas_result
        if not meas_result["valid"]:
            errors.extend(meas_result["errors"])
    else:
        checks["extracted_measurements"] = build_validation_report(False, ["extracted_measurements.csv:missing"])
        warnings.append("extracted_measurements.csv:missing")

    # Check response_statistics.csv
    stats_path = session_dir / "response_statistics.csv"
    if stats_path.exists():
        stats_result = validate_response_statistics_csv(stats_path)
        checks["response_statistics"] = stats_result
        if not stats_result["valid"]:
            errors.extend(stats_result["errors"])
    else:
        checks["response_statistics"] = build_validation_report(False, ["response_statistics.csv:missing"])
        warnings.append("response_statistics.csv:missing")

    # Check state_logs directory
    state_logs = session_dir / "state_logs"
    if state_logs.is_dir():
        csv_count = len(list(state_logs.glob("*.csv")))
        checks["state_logs"] = build_validation_report(True, [], csv_count=csv_count)
    else:
        checks["state_logs"] = build_validation_report(False, ["state_logs/:missing"])
        errors.append("state_logs/:missing")

    return build_validation_report(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        checks=checks,
    )
