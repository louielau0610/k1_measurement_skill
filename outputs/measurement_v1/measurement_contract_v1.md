# Measurement Data Contract v1.0

**Version**: `measurement_v1.0`
**Scope**: Step 1 — measurement module only. Not compensation.
**Status**: Active for Booster K1. Future requirement for GO1/G1.

## Research Basis

- **ROS Odometry**: Represents position and velocity estimates in free space, separates pose frame and twist frame.
- **ROS REP-103**: Defines body frame orientation: x forward, y left, z up.
- **ROS IMU**: Standardizes orientation (radians), angular velocity (rad/s), linear acceleration (m/s²).
- **rosbag2**: Supports reproducible recording and replay of communication data.

Therefore, this contract standardizes: units, coordinate assumptions, state source, frame semantics, raw log references, extraction method, and QC status.

## Coordinate Convention

| Axis | Direction | Unit (internal) | Unit (export) |
|------|-----------|-----------------|---------------|
| Body x | Forward | meters | meters |
| Body y | Left | meters | meters |
| Body z | Up | meters | meters |
| Yaw | Rotation about z | radians | **degrees** |

Forward displacement is extracted by projection onto initial heading (or equivalent documented method).

## Trial-Level Fields

| # | Field | Type | Unit | Required | Description |
|---|-------|------|------|----------|-------------|
| 1 | `schema_version` | string | — | ✅ | Contract version |
| 2 | `dataset_id` | string | — | ✅ | Dataset identifier |
| 3 | `session_id` | string | — | ✅ | Session identifier |
| 4 | `trial_id` | string | — | ✅ | Unique trial ID |
| 5 | `platform` | string | — | ✅ | Platform ID |
| 6 | `robot_model` | string | — | ✅ | Robot model name |
| 7 | `robot_id` | string | — | ✅ | Individual robot ID |
| 8 | `surface_type` | string | — | ✅ | Surface type |
| 9 | `environment_id` | string | — | ✅ | Environment ID |
| 10 | `command_velocity_mps` | float | m/s | ✅ | Commanded forward velocity |
| 11 | `measured_actual_velocity_mps` | float | m/s | ✅ | Measured actual velocity |
| 12 | `tracking_error_mps` | float | m/s | ✅ | measured − command |
| 13 | `relative_tracking_error` | float | — | ✅ | error / command |
| 14 | `yaw_drift_deg` | float | degrees | ✅ | Odometer yaw drift |
| 15 | `imu_yaw_drift_deg` | float | degrees | ✅ | IMU yaw drift |
| 16 | `state_source` | string | — | ✅ | ROS topic / SDK source |
| 17 | `command_source` | string | — | ✅ | Command source |
| 18 | `measurement_source` | string | — | ✅ | Primary data source |
| 19 | `measurement_method` | string | — | ✅ | Extraction method |
| 20 | `analysis_window_start_sec` | float | seconds | ✅ | Window start |
| 21 | `analysis_window_end_sec` | float | seconds | ✅ | Window end |
| 22 | `state_log_path` | string | — | ✅ | Path to state log |
| 23 | `raw_log_path` | string | — | ✅ | Path to raw log or "unavailable" |
| 24 | `extraction_status` | enum | — | ✅ | See status enum below |
| 25 | `confidence` | string | — | ✅ | Confidence label |
| 26 | `invalid_reason` | string | — | ✅ | Reason if invalid |
| 27 | `created_at` | string | — | ✅ | ISO 8601 timestamp |

### Extraction Status Enum

| Value | Meaning |
|-------|---------|
| `ok` | Measurement extracted successfully |
| `invalid_trial` | Trial was marked invalid (see invalid_reason) |
| `missing_log` | State log file not found |
| `insufficient_samples` | Not enough data points to extract velocity |
| `missing_state_source` | Required state topic/source unavailable |
| `extraction_error` | Extraction failed with error |
| `not_extracted` | Extraction not yet attempted |

### Rules

1. **Velocities must be in m/s.** No cm/s, mm/s, or other units.
2. **Yaw values must be in degrees** for exported statistics. Internal computation may use radians.
3. **Command velocity must never be copied into measured actual velocity.** If they are numerically identical to 1e-9, this is flagged.
4. **measured_actual_velocity may be zero or negative** if extraction produces it, but should be explicit.
5. **Invalid trials must contain `invalid_reason`.**
6. **state_log_path or raw_log_path must exist** or be explicitly marked "unavailable".
7. **extraction_status must be a valid enum value.**

## Aggregate-Level Fields

| # | Field | Type | Unit | Required |
|---|-------|------|------|----------|
| 1 | `schema_version` | string | — | ✅ |
| 2 | `dataset_id` | string | — | ✅ |
| 3 | `platform` | string | — | ✅ |
| 4 | `robot_model` | string | — | ✅ |
| 5 | `surface_type` | string | — | ✅ |
| 6 | `command_velocity_mps` | float | m/s | ✅ |
| 7 | `n` | int | — | ✅ |
| 8 | `mean_actual_velocity_mps` | float | m/s | ✅ |
| 9 | `std_actual_velocity_mps` | float | m/s | ✅ |
| 10 | `median_actual_velocity_mps` | float | m/s | ✅ |
| 11 | `min_actual_velocity_mps` | float | m/s | ✅ |
| 12 | `max_actual_velocity_mps` | float | m/s | ✅ |
| 13 | `mean_tracking_error_mps` | float | m/s | ✅ |
| 14 | `mean_abs_tracking_error_mps` | float | m/s | ✅ |
| 15 | `relative_tracking_error` | float | — | ✅ |
| 16 | `under_tracking_ratio` | float | — | ✅ |
| 17 | `no_motion_ratio` | float | — | ✅ |
| 18 | `mean_yaw_drift_deg` | float | degrees | ✅ |
| 19 | `std_yaw_drift_deg` | float | degrees | ✅ |
| 20 | `max_yaw_drift_deg` | float | degrees | ✅ |
| 21 | `response_uncertainty` | float | — | ✅ |
| 22 | `risk_score` | float | — | ✅ |
| 23 | `region_label` | string | — | ✅ |
| 24 | `evidence_level` | string | — | ✅ |
| 25 | `limitations` | string | — | ✅ |

## Session Metadata Fields

| # | Field | Type | Required |
|---|-------|------|----------|
| 1 | `schema_version` | string | ✅ |
| 2 | `session_id` | string | ✅ |
| 3 | `dataset_id` | string | ✅ |
| 4 | `platform` | string | ✅ |
| 5 | `robot_model` | string | ✅ |
| 6 | `robot_id` | string | ✅ |
| 7 | `surfaces` | list[string] | ✅ |
| 8 | `speeds_mps` | list[float] | ✅ |
| 9 | `repeats` | int | ✅ |
| 10 | `block_order` | string | ✅ |
| 11 | `timing` | object | ✅ |
| 12 | `command_source` | string | ✅ |
| 13 | `state_sources` | list[string] | ✅ |
| 14 | `coordinate_convention` | object | ✅ |
| 15 | `state_frame` | string | ✅ |
| 16 | `body_frame` | string | ✅ |
| 17 | `measurement_method` | string | ✅ |
| 18 | `analysis_window` | object | ✅ |
| 19 | `hardware_validated_reference` | bool | ✅ |
| 20 | `operator_notes` | string | ✅ |
| 21 | `limitations` | list[string] | ✅ |
| 22 | `created_at` | string | ✅ |

## How GO1/G1 Should Satisfy This Contract

Future GO1 and G1 measurement adapters must:

1. Produce CSV rows with all trial-level contract fields.
2. Use m/s for velocities and degrees for exported yaw statistics.
3. Document state source, command source, and measurement method per row.
4. Reference raw log paths or mark them "unavailable".
5. Use valid extraction_status enum values.
6. Never copy command velocity into measured actual velocity.
7. Include invalid_reason for any invalid trials.
8. Provide session metadata with coordinate convention, frame semantics, and limitations.

## Why This Is Still Measurement-Only

This contract defines **data format and validation rules**, not:
- Velocity compensation algorithms
- Inverse response models
- Command remapping
- Navigation control
- Safe command adaptation

The contract is a prerequisite for any future compensation stage. It ensures that all platforms provide data in a consistent, verifiable format before any compensation model consumes it.

## Artifacts

| Artifact | Path |
|----------|------|
| Contract definition (JSON) | `outputs/measurement_v1/measurement_contract_v1.json` |
| Contract documentation (MD) | `outputs/measurement_v1/measurement_contract_v1.md` |
| K1 contract-compliant measurements | `outputs/measurement_v1/booster_k1_measurements_contract_v1.csv` |
| K1 contract validation | `outputs/measurement_v1/booster_k1_measurements_contract_validation.json` |
| Contract module | `calibration_core/measurement_contract.py` |
| Legacy mapping module | `calibration_core/measurement_contract_mapping.py` |

## Phase Gates

| Gate | Status |
|------|--------|
| `velocity_compensation_ready` | `false` |
| `unitree_go1_measurement_ready` | `false` |
| `unitree_g1_measurement_ready` | `false` |
| `cross_platform_empirical_validation` | `false` |
