# Booster K1 Measurement Contract Validation Report

**Contract version**: `measurement_v1.0`
**Dataset**: `m19c_booster_k1_gold_v1`
**Conversion time**: 2026-06-11

## Summary

✅ **All 72 legacy M19C measurement rows successfully converted and validated.**

| Metric | Value |
|--------|-------|
| Total rows | 72 |
| Valid rows | 72 |
| Invalid rows | 0 |
| Fields per row | 27 |
| Velocity unit | m/s |
| Yaw unit | degrees |

## Legacy Field Mapping

| Legacy Field | Contract Field |
|-------------|----------------|
| `command_velocity` | `command_velocity_mps` |
| `measured_actual_velocity` | `measured_actual_velocity_mps` |
| `yaw_drift_statistic` | `yaw_drift_deg` |
| `imu_yaw_drift_deg` | `imu_yaw_drift_deg` |
| `measurement_source` | `measurement_source` |
| `measurement_method` | `measurement_method` |
| `extraction_status` | `extraction_status` |
| `analysis_window_start_sec` | `analysis_window_start_sec` |
| `analysis_window_end_sec` | `analysis_window_end_sec` |
| `measurement_confidence` | `confidence` |
| `annotation_notes` | `invalid_reason` |

## Derived Fields

| Field | Derivation |
|-------|-----------|
| `tracking_error_mps` | measured_actual_velocity_mps − command_velocity_mps |
| `relative_tracking_error` | tracking_error_mps / command_velocity_mps |
| `state_log_path` | Derived from trial_id pattern: `data/m19c_ros2_odometer_logs/{trial_id}.csv` |

## Validation Checks Passed

- ✅ All 27 trial contract fields present
- ✅ All numeric fields are valid floats
- ✅ All extraction_status values are valid enums (all "ok")
- ✅ No command_velocity copied as measured_velocity
- ✅ All rows have state_log_path or raw_log_path
- ✅ Schema version consistent across all rows

## Relationship to M19C-E Gold Profile

This contract-compliant dataset is derived from the M19C-E gold profile data. The original M19C artifacts remain unchanged:

- `data/m19c_ros2_odometer_logs/` — Unchanged
- `data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv` — Unchanged
- `outputs/real_k1_validation_m19/k1_gold_profile_v1.json` — Unchanged
