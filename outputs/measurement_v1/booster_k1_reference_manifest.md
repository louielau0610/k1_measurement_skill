# Booster K1 Measurement v1 Reference Manifest

Dataset: `m19c_full_72_ros2_odometer_20260611`

Platform: `booster_k1`

Validation status: `booster_k1_reference_ready`

K1 is the only validated measurement reference for Measurement Module v1. The manifest references existing M19C-E artifacts and does not move or rewrite them.

## Referenced Artifacts

- State logs: `data/m19c_ros2_odometer_logs`
- Trial records: `data/m19_repeated_validation_inputs/m19c_trial_records.csv`
- Extracted measurements: `data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv`
- QC summary: `outputs/real_k1_validation_m19/m19c_measurement_run_qc_summary.json`
- Response statistics: `outputs/real_k1_validation_m19/surface_response_statistics.csv`
- Gold profile: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`
- Empirical summary: `outputs/real_k1_validation_m19/m19c_empirical_summary.json`

## Boundary

- Velocity compensation ready: `false`
- Unitree GO1 measurement ready: `false`
- Unitree G1 measurement ready: `false`
- Cross-platform empirical validation: `false`
