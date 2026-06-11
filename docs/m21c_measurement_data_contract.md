# M21-C: Measurement Data Contract

M21-C defines the **formal cross-platform measurement data contract** that Booster K1, Unitree GO1, and Unitree G1 must satisfy before any velocity compensation stage can consume their data.

## Motivation

The measurement module (Step 1 of the roadmap) produces data from different robot platforms. Before proceeding to velocity compensation (Step 2/3), we need a contract that ensures:

1. **Consistent units**: All velocities in m/s, yaw exports in degrees.
2. **Consistent semantics**: Same field names, same coordinate conventions.
3. **Verifiable quality**: Extraction status, confidence, invalid reasons.
4. **Traceable provenance**: State sources, command sources, raw log references.
5. **Cross-platform readiness**: GO1/G1 can be validated against the same contract later.

## Research Basis

- **ROS Odometry** (nav_msgs/Odometry): Separates pose frame and twist frame. Position in meters, linear velocity in m/s.
- **ROS REP-103**: Standard body frame: x forward, y left, z up. Yaw is rotation about z.
- **ROS IMU** (sensor_msgs/Imu): Orientation in radians, angular velocity in rad/s, linear acceleration in m/s².
- **rosbag2**: Reproducible recording and replay ensures raw data can be re-examined.

Therefore, the contract standardizes: units, coordinate assumptions, state source naming, frame semantics, raw log references, extraction method documentation, and QC status.

## Schema Design

Three levels:

1. **Trial-level** (27 fields): Per-trial measurement with velocity, yaw drift, extraction metadata.
2. **Aggregate-level** (25 fields): Per-surface-speed aggregated statistics.
3. **Session-level** (22 fields): Session metadata with coordinate conventions, frame semantics.

### Versioning

- Schema version: `measurement_v1.0`
- The version is embedded in every record (`schema_version` field).
- Future schema changes require a version bump and backward-compatible mapping.

## Coordinate Convention

| Axis | Direction | Internal Unit | Export Unit |
|------|-----------|---------------|-------------|
| Body x | Forward | meters | meters |
| Body y | Left | meters | meters |
| Body z | Up | meters | meters |
| Yaw | Rotation about z | radians | **degrees** |

Forward displacement is extracted by projection onto the initial heading. This method must be documented per platform.

## Field Mapping from Legacy K1 Data

The legacy M19C extracted measurements used different field names. The mapping module (`calibration_core/measurement_contract_mapping.py`) provides:

| Legacy Field | Contract Field |
|-------------|----------------|
| `command_velocity` | `command_velocity_mps` |
| `measured_actual_velocity` | `measured_actual_velocity_mps` |
| `yaw_drift_statistic` | `yaw_drift_deg` |
| `imu_yaw_drift_deg` | `imu_yaw_drift_deg` |
| `measurement_confidence` | `confidence` |
| `annotation_notes` | `invalid_reason` |

Derived fields:
- `tracking_error_mps` = measured − command
- `relative_tracking_error` = error / command

## How Future GO1/G1 Adapters Should Produce the Same Contract

Future GO1 and G1 measurement adapters must:

1. **Produce CSV rows** with all 27 trial-level contract fields.
2. **Use m/s** for velocities and **degrees** for exported yaw statistics.
3. **Document** state source (ROS topic or SDK API), command source, and measurement method per row.
4. **Reference raw log paths** or mark them `"unavailable"`.
5. **Use valid extraction_status** enum values.
6. **Never copy** command velocity into measured actual velocity.
7. **Include invalid_reason** for any invalid trials.
8. **Provide session metadata** with coordinate convention, state frame, body frame, and limitations.

## Validation Process

The contract validation module (`calibration_core/measurement_contract.py`) provides:

| Function | Purpose |
|----------|---------|
| `validate_trial_measurement(row)` | Validate a single trial row |
| `validate_aggregate_response(row)` | Validate a single aggregate row |
| `validate_session_metadata(meta)` | Validate session metadata |
| `validate_measurement_csv(path)` | Validate entire measurement CSV |
| `validate_response_statistics_csv(path)` | Validate response statistics CSV |
| `validate_session_directory(dir)` | Validate complete session directory |

All functions return structured validation reports (not just booleans) with errors, warnings, and metadata.

### CLI

```bash
# Convert legacy data
python scripts/convert_measurements_to_contract.py \\
  --input data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv \\
  --output outputs/measurement_v1/booster_k1_measurements_contract_v1.csv

# Validate contract compliance
python scripts/validate_measurement_contract.py \\
  --measurements outputs/measurement_v1/booster_k1_measurements_contract_v1.csv

python scripts/validate_measurement_contract.py \\
  --session-dir data/measurement_sessions/booster_k1/<id>
```

## K1 Conversion Result

- **72 legacy rows** → **72 contract-compliant rows**
- **All 72 rows pass validation** (0 invalid)
- **All extraction_status values**: `ok`
- **No command velocity copy detected**
- **State log paths derived** from trial_id patterns

## Limitations

- Contract is measurement-only: no compensation, no inverse models, no command remapping.
- Yaw drift unit is degrees in export; internal computation may use radians.
- `raw_log_path` marked "unavailable" for legacy M19C data (bag files not tracked in this repo).
- GO1/G1 contract compliance is not yet verified (no hardware data exists).
- Coordinate convention assumes REP-103 body frame; platforms deviating must document.

## What Is NOT Claimed

- ❌ Velocity compensation (future Step 2/3)
- ❌ Inverse response model
- ❌ Command remapping
- ❌ Navigation control
- ❌ GO1 hardware validation (future Step 4)
- ❌ G1 hardware validation (future Step 4)
- ❌ Cross-platform empirical validation
- ❌ Compensation readiness

## Phase Gates

| Gate | Status |
|------|--------|
| `velocity_compensation_ready` | `false` |
| `unitree_go1_measurement_ready` | `false` |
| `unitree_g1_measurement_ready` | `false` |
| `cross_platform_empirical_validation` | `false` |
| `booster_k1_reference_ready` | `true` |
| `measurement_contract_active` | `true` (K1 only) |
