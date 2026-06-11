"""Legacy-to-contract field mapping for measurement data.

Maps M19C / M21-B field names to the Measurement Data Contract v1.0 names.
Does not overwrite legacy artifacts. Provides conversion helpers.
"""
from __future__ import annotations

from typing import Any

from calibration_core.measurement_contract import MEASUREMENT_CONTRACT_VERSION

# ---------------------------------------------------------------------------
# Legacy → Contract field name mapping (trial-level)
# ---------------------------------------------------------------------------

LEGACY_TO_CONTRACT_TRIAL: dict[str, str] = {
    "command_velocity": "command_velocity_mps",
    "measured_actual_velocity": "measured_actual_velocity_mps",
    "yaw_drift_statistic": "yaw_drift_deg",
    "imu_yaw_drift_deg": "imu_yaw_drift_deg",
    "imu_yaw_drift_statistic": "imu_yaw_drift_deg",
    "measurement_confidence": "confidence",
    "annotation_notes": "invalid_reason",
}

# ---------------------------------------------------------------------------
# Legacy → Contract field name mapping (aggregate-level)
# ---------------------------------------------------------------------------

LEGACY_TO_CONTRACT_AGGREGATE: dict[str, str] = {
    "command_velocity": "command_velocity_mps",
    "mean_actual_velocity": "mean_actual_velocity_mps",
    "std_actual_velocity": "std_actual_velocity_mps",
    "median_actual_velocity": "median_actual_velocity_mps",
    "min_actual_velocity": "min_actual_velocity_mps",
    "max_actual_velocity": "max_actual_velocity_mps",
    "mean_tracking_error": "mean_tracking_error_mps",
    "mean_abs_tracking_error": "mean_abs_tracking_error_mps",
    "mean_yaw_drift_deg": "mean_yaw_drift_deg",
    "std_yaw_drift_deg": "std_yaw_drift_deg",
    "max_yaw_drift_deg": "max_yaw_drift_deg",
    "mean_imu_yaw_drift_deg": "mean_imu_yaw_drift_deg",
    "odom_imu_yaw_disagreement_deg": "odom_imu_yaw_disagreement_deg",
}

# ---------------------------------------------------------------------------
# Legacy → Contract field name mapping (session metadata)
# ---------------------------------------------------------------------------

LEGACY_TO_CONTRACT_SESSION: dict[str, str] = {
    "speeds": "speeds_mps",
    "extraction_method": "measurement_method",
}


def map_legacy_trial_row(
    legacy_row: dict[str, Any],
    *,
    dataset_id: str = "",
    platform: str = "",
    robot_model: str = "",
    robot_id: str = "",
    session_id: str = "",
    environment_id: str = "",
    surface_type: str = "",
    state_source: str = "",
    command_source: str = "",
    raw_log_path: str = "",
    created_at: str = "",
) -> dict[str, Any]:
    """Convert a legacy M19C trial row to contract-compliant format.

    Preserves original trial_id. Fills derivable fields. Leaves unknown
    fields explicit as empty or unavailable.
    """
    row: dict[str, Any] = {}

    # Schema version
    row["schema_version"] = MEASUREMENT_CONTRACT_VERSION

    # Identity fields
    row["dataset_id"] = legacy_row.get("dataset_id", dataset_id)
    row["session_id"] = legacy_row.get("session_id", session_id)
    row["trial_id"] = legacy_row.get("trial_id", "")
    row["platform"] = legacy_row.get("platform", platform)
    row["robot_model"] = legacy_row.get("robot_model", robot_model)
    row["robot_id"] = legacy_row.get("robot_id", robot_id)
    row["surface_type"] = legacy_row.get("surface_type", surface_type)
    row["environment_id"] = legacy_row.get("environment_id", environment_id)

    # Velocity fields (apply mapping)
    cmd_raw = legacy_row.get("command_velocity", legacy_row.get("command_velocity_mps", ""))
    meas_raw = legacy_row.get("measured_actual_velocity", legacy_row.get("measured_actual_velocity_mps", ""))

    cmd = _to_float(cmd_raw)
    meas = _to_float(meas_raw)

    row["command_velocity_mps"] = cmd
    row["measured_actual_velocity_mps"] = meas

    # Tracking error (derived)
    if cmd is not None and meas is not None:
        row["tracking_error_mps"] = round(meas - cmd, 6)
        row["relative_tracking_error"] = round((meas - cmd) / cmd, 6) if cmd != 0 else 0.0
    else:
        row["tracking_error_mps"] = ""
        row["relative_tracking_error"] = ""

    # Yaw fields (apply mapping)
    yaw_raw = legacy_row.get("yaw_drift_statistic", legacy_row.get("yaw_drift_deg", ""))
    imu_yaw_raw = legacy_row.get(
        "imu_yaw_drift_deg",
        legacy_row.get("imu_yaw_drift_statistic", ""),
    )
    row["yaw_drift_deg"] = _to_float(yaw_raw) if yaw_raw not in (None, "") else ""
    row["imu_yaw_drift_deg"] = _to_float(imu_yaw_raw) if imu_yaw_raw not in (None, "") else ""

    # Source fields
    row["state_source"] = legacy_row.get("state_source", state_source)
    row["command_source"] = legacy_row.get("command_source", command_source)
    row["measurement_source"] = legacy_row.get("measurement_source", "")
    row["measurement_method"] = legacy_row.get("measurement_method", "")

    # Analysis window
    row["analysis_window_start_sec"] = legacy_row.get("analysis_window_start_sec", "")
    row["analysis_window_end_sec"] = legacy_row.get("analysis_window_end_sec", "")

    # Log paths — derive from trial_id for legacy M19C data if not present
    trial_id_val = legacy_row.get("trial_id", "")
    state_log = legacy_row.get("state_log_path", "")
    if not state_log and trial_id_val:
        # Legacy M19C logs are under data/m19c_ros2_odometer_logs/<trial_id>.csv
        state_log = f"data/m19c_ros2_odometer_logs/{trial_id_val}.csv"
    row["state_log_path"] = state_log
    row["raw_log_path"] = legacy_row.get("raw_log_path", raw_log_path) or "unavailable"

    # Status and confidence
    row["extraction_status"] = legacy_row.get("extraction_status", "")
    row["confidence"] = legacy_row.get("confidence", legacy_row.get("measurement_confidence", ""))

    # Invalid reason
    row["invalid_reason"] = legacy_row.get("invalid_reason", legacy_row.get("annotation_notes", ""))

    # Timestamp
    row["created_at"] = legacy_row.get("created_at", legacy_row.get("timestamp", created_at))

    return row


def map_legacy_aggregate_row(
    legacy_row: dict[str, Any],
    *,
    dataset_id: str = "",
    platform: str = "",
    robot_model: str = "",
) -> dict[str, Any]:
    """Convert a legacy aggregate response row to contract-compliant format."""
    row: dict[str, Any] = {}
    row["schema_version"] = MEASUREMENT_CONTRACT_VERSION
    row["dataset_id"] = legacy_row.get("dataset_id", dataset_id)
    row["platform"] = legacy_row.get("platform", platform)
    row["robot_model"] = legacy_row.get("robot_model", robot_model)

    # Surface & command velocity
    row["surface_type"] = legacy_row.get("surface_type", legacy_row.get("surface_id", ""))
    cmd_raw = legacy_row.get("command_velocity", legacy_row.get("command_velocity_mps", ""))
    row["command_velocity_mps"] = _to_float(cmd_raw)

    # Count
    row["n"] = legacy_row.get("n", "")

    # Velocity statistics
    for legacy_key, contract_key in LEGACY_TO_CONTRACT_AGGREGATE.items():
        if contract_key not in row:
            val = legacy_row.get(legacy_key, "")
            row[contract_key] = _to_float(val) if val not in (None, "") else ""

    # Ratios
    row["under_tracking_ratio"] = legacy_row.get("under_tracking_ratio", "")
    row["no_motion_ratio"] = legacy_row.get("no_motion_ratio", "")

    # Uncertainty and risk
    row["response_uncertainty"] = legacy_row.get("response_uncertainty", "")
    row["risk_score"] = legacy_row.get("risk_score", "")
    row["region_label"] = legacy_row.get("region_label", "")
    row["evidence_level"] = legacy_row.get("evidence_level", "")

    # Limitations
    row["limitations"] = legacy_row.get("limitations", "")

    return row


def map_legacy_session_metadata(
    legacy_meta: dict[str, Any],
) -> dict[str, Any]:
    """Convert legacy session metadata to contract-compliant format."""
    meta: dict[str, Any] = {}
    meta["schema_version"] = MEASUREMENT_CONTRACT_VERSION

    # Direct copies
    for key in (
        "session_id", "dataset_id", "platform", "robot_model", "robot_id",
        "repeats", "block_order", "timing", "command_source", "state_sources",
        "hardware_validated_reference", "operator_notes", "limitations", "created_at",
    ):
        meta[key] = legacy_meta.get(key, "")

    # Mapped fields
    meta["surfaces"] = legacy_meta.get("surfaces", legacy_meta.get("surface", ""))
    if isinstance(meta["surfaces"], str):
        meta["surfaces"] = [meta["surfaces"]]

    speeds = legacy_meta.get("speeds_mps", legacy_meta.get("speeds", []))
    meta["speeds_mps"] = speeds

    meta["measurement_method"] = legacy_meta.get(
        "measurement_method",
        legacy_meta.get("extraction_method", ""),
    )

    meta["coordinate_convention"] = legacy_meta.get("coordinate_convention", {
        "body_x": "forward",
        "body_y": "left",
        "body_z": "up",
        "yaw_internal_unit": "radians",
        "yaw_export_unit": "degrees",
        "forward_displacement_method": "projection_onto_initial_heading",
    })

    meta["state_frame"] = legacy_meta.get("state_frame", "odom")
    meta["body_frame"] = legacy_meta.get("body_frame", "base_link")
    meta["analysis_window"] = legacy_meta.get("analysis_window", {"start_sec": 3.0, "end_sec": 8.0})

    return meta


def _to_float(value: Any) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None
