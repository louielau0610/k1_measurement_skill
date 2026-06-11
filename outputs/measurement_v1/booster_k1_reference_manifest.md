# Booster K1 Measurement v1 Reference Manifest

Dataset: `m19c_full_72_ros2_odometer_20260611`

Platform: `booster_k1`

Validation status: `booster_k1_reference_ready`

K1 is the only validated measurement reference for Measurement Module v1. The manifest references existing M19C-E artifacts and does not move or rewrite them.

## M21-B Hardened Reference Implementation

M21-B hardens Booster K1 as the first measurement reference implementation with:

- **Split-process design**: SDK command process isolated from ROS2 logger process.
- **Dry-run by default**: No hardware movement without explicit `--execute`.
- **Per-trial permit mode**: Each trial requires operator confirmation.
- **Standard session layout**: `data/measurement_sessions/booster_k1/<session_id>/`

### Hardened Reference Paths

| Component | Path |
|-----------|------|
| Session manager | `platforms/booster_k1/session.py` |
| Measurement runner | `platforms/booster_k1/measurement_runner.py` |
| State logger | `platforms/booster_k1/measurement_logger.py` |
| Measurement extractor | `platforms/booster_k1/measurement_extractor.py` |
| Measurement QC | `platforms/booster_k1/measurement_qc.py` |
| Platform README | `platforms/booster_k1/README.md` |

### Session Layout

```
data/measurement_sessions/booster_k1/<session_id>/
├── session_metadata.json
├── trial_plan.csv
├── trial_records.csv
├── state_logs/
├── extracted_measurements.csv
├── extraction_summary.json
├── extraction_report.md
├── qc_summary.json
├── qc_report.md
├── response_statistics.csv
├── profile.json
└── profile.md
```

### CLI Commands

```bash
# Dry-run (default)
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor

# Execute with per-trial permit
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute

# Extract measurements
python scripts/extract_booster_k1_measurements.py --session-dir data/measurement_sessions/booster_k1/<id>

# QC session
python scripts/qc_booster_k1_measurement_session.py --session-dir data/measurement_sessions/booster_k1/<id>
```

## Referenced Artifacts

- State logs: `data/m19c_ros2_odometer_logs`
- Trial records: `data/m19_repeated_validation_inputs/m19c_trial_records.csv`
- Extracted measurements: `data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv`
- QC summary: `outputs/real_k1_validation_m19/m19c_measurement_run_qc_summary.json`
- Response statistics: `outputs/real_k1_validation_m19/surface_response_statistics.csv`
- Gold profile: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`
- Empirical summary: `outputs/real_k1_validation_m19/m19c_empirical_summary.json`

## Backward Compatibility

Existing M19C-E gold artifacts remain unchanged. New runs go into new session directories under `data/measurement_sessions/booster_k1/`.

## M21-C Measurement Data Contract

M21-C defines the formal cross-platform measurement data contract. Booster K1 is the first platform with contract-compliant output.

- **Contract version**: `measurement_v1.0`
- **Contract definition**: `outputs/measurement_v1/measurement_contract_v1.json`
- **Contract documentation**: `outputs/measurement_v1/measurement_contract_v1.md`
- **K1 contract measurements**: `outputs/measurement_v1/booster_k1_measurements_contract_v1.csv` (72 rows, all valid)
- **Contract validation**: `outputs/measurement_v1/booster_k1_measurements_contract_validation.json`
- **Contract module**: `calibration_core/measurement_contract.py`
- **Legacy mapping**: `calibration_core/measurement_contract_mapping.py`

### Contract CLI Commands

```bash
# Convert legacy measurements to contract format
python scripts/convert_measurements_to_contract.py \\
  --input data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv \\
  --output outputs/measurement_v1/booster_k1_measurements_contract_v1.csv

# Validate contract compliance
python scripts/validate_measurement_contract.py \\
  --measurements outputs/measurement_v1/booster_k1_measurements_contract_v1.csv
```

## Boundary

- Velocity compensation ready: `false`
- Unitree GO1 measurement ready: `false`
- Unitree G1 measurement ready: `false`
- Cross-platform empirical validation: `false`
